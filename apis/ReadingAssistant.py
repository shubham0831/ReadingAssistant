import logging as log
from UniqueDict import UniqueDict
from PdfManager import PdfManager
from ClaudeManager import ClaudeManager
import PdfManager as pdfm
import ClaudeManager as cm
from typing import Any, Dict, List
import pyperclip
from DbHandler import DbHandler
import os
import json

PROMPT_OUTPUT_FILE_PATH = "/Users/shubham/Code/personal/ReadingAssistant/apis/testpdfs/textCleaning"

raw = """Summary:\n\nThe text depicts several conversations as final preparations are made before House Atreides departs Caladan for Arrakis. Thufir Hawat continues testing Paul's knowledge about Arrakis, emphasizing the planet's harsh conditions. Dr. Yueh informs Paul that regular lessons will be interrupted by the travel, but he will have filmbooks and lessons during the journey. He provides brief information about the native Fremen people of Arrakis and the ecosystem. Yueh also gifts Paul with an old Orange Catholic Bible before leaving to meet Duke Leto. The conversations reveal the risky political situation House Atreides is walking into on Arrakis.\n\nKey Points:\n\n1. Thufir Hawat quizzes Paul about Arrakis, stressing the extreme climate, water scarcity, and potential alliance with the Fremen.\n\n2. Dr. Yueh tells Paul his regular lessons will be interrupted by travel to Arrakis but he will study the planet's life forms and people during the journey. \n\n3. Yueh provides basic details about the Fremen, their fierce and violent culture, and the worms of Arrakis.\n\n4. Yueh gifts Paul with a very old Orange Catholic Bible before his meeting with Duke Leto.\n\n5. The conversations underscore the peril House Atreides faces in taking control of Arrakis away from the Harkonnens.\n\nFAQs:\n\n1. Why is Arrakis so dangerous for House Atreides?\n\n2. What are the most dangerous creatures on Arrakis? \n\n3. Who are the Fremen and why are they important?\n\n4. What is melange and why is it important on Arrakis?\n\n5. Why does Dr. Yueh give Paul the Orange Catholic Bible?  \n\n6. How does Leto prepare Paul for the journey to Arrakis?\n\n7. What is the graben, the sink, and the pan on Arrakis?  \n\n8. How might Fremen make good allies for House Atreides?\n\n9. What are the costs and perils involved in making Arrakis economically feasible?  \n\n10. What senses may humans lack according to the Orange Catholic Bible?"""
class ReadingAssistant():
    def __init__(self, claudeManager: ClaudeManager, pdfManager: PdfManager, dbHandler: DbHandler, copyTextToClipboard=False):
        self.claudeManager = claudeManager
        self.pdfManager = pdfManager
        self.dbHandler = dbHandler
        self.copyText = copyTextToClipboard

    def preprocess(self, filepath: str, indexName:str, pagesPerChunk: int, maxChunks: int = -1):
        fileKey = self.pdfManager.addFile(filepath, pagesPerChunk)

        if maxChunks == -1:
            fileChunks = self.pdfManager.readComplete(fileKey)
        else:
            fileChunks = self.pdfManager.readFirstNChunks(fileKey, maxChunks)
        
        return fileKey
        
        chunksRead = len(fileChunks)
        log.info(f"total number of chunks is {chunksRead}")

        documents: List[Dict[str, Any]] = []
        prevSummary = ""

        insertionResponse = []
        for i in range(0, chunksRead):
            chunk = fileChunks[i]
            chunkContent = chunk[pdfm.CONTENT]
            if (i % 5 == 0 and i != 0):
                log.info(f"read {i} out of {chunksRead} chunks, inserting chunk of 10")
                response = self.dbHandler.addDocuments(indexName, documents, ["raw"])

                if isinstance(response, list):
                    for resp in response:
                        insertionResponse.append(resp)
                else:
                    insertionResponse.append(response)
                documents = []
            
            documents.append({
                "raw": chunkContent,
                "chunkNumber": i
            })
            # systemPrompt, userPrompt = self.claudeManager.generatePrompt(chunkContent, context=prevSummary)
            # # raw = self.claudeManager.sendMessage(cm.USER, systemPrompt, userPrompt)
            # raw = self.getSavedRaw(i)

            # if raw == "":
            #     break

            # try:
            #     cleanResponse = self.claudeManager.cleanResponse(raw)
            #     prevSummary = cleanResponse["PreviousSummary"]
            #     cleanResponse["chunkNumber"] = i
            #     cleanResponse["raw"] = chunkContent
            #     documents.append(cleanResponse)
            #     # self.createFolderAndFile(PROMPT_OUTPUT_FILE_PATH, f"Chunk{i}.json,", [{"raw" : raw, "clean": cleanResponse, "sysPrompt": systemPrompt, "userPrompt": userPrompt}])
            # except IndexError:
            #     log.warn(f"Index error, output from claude was not right, writing down the output in Chunk{i}Error.json")
            #     self.createFolderAndFile(PROMPT_OUTPUT_FILE_PATH, f"Chunk{i}.json,", [{"raw" : raw, "sysPrompt": systemPrompt, "userPrompt": userPrompt}])
            #     break

            """
                The summaries generated have 3 parts
                    "Summary", "Key Point", "FAQs"
                Clean this summary, to extract out the 3 points, then create a dict with the following keys
                {"Summaries", "KeyPoint", "FAQs", "ChunkNumber", "RawText"=chunkContent}

                TODO: Read this 
                Good document for end user use case, when they provide a question, we need to figure out the relevant summary to be used, etc
                https://www.marqo.ai/blog/from-iron-manual-to-ironman-augmenting-gpt-with-marqo-for-fast-editable-memory-to-enable-context-aware-question-answering
            """
            # todo store these summaries in a database, the dummies are in the comment of prompts.py, use them and store those in the db
        
        # self.createFolderAndFile(PROMPT_OUTPUT_FILE_PATH, "output.json", allDocuments)
        log.info("for loop over, adding remaining chunks now")
        if len(documents) > 0:
            response = self.dbHandler.addDocuments(indexName, documents, ["PreviousSummary"])
            if isinstance(response, list):
                for resp in response:
                    insertionResponse.append(resp)
            else:
                insertionResponse.append(response)
        
        documentIds = []
        for response in insertionResponse:
            itemList = response['items']
            for item in itemList:
                statusCode = item['status']
                if statusCode > 299 or statusCode < 200:
                    log.warn(f"error in inserting document \n full item is \n{item}")

                docId = item['_id']
                documentIds.append(docId)
        
        log.info(f"\n\n inserted document ids are {documentIds}")
        return fileKey
    
    def createFolderAndFile(self, folderPath: str, fileName: str, content: List[Dict[str, Any]]) -> None:
        if not os.path.exists(folderPath):
            os.makedirs(folderPath)

        filePath = os.path.join(folderPath, fileName)
        if not os.path.exists(filePath):
            with open(filePath, 'w') as file:
                # Write content to the file
                json.dump(content, file, indent=2)
            log.info(f"File '{fileName}' created in folder '{folderPath}'")
        else:
            log.warn(f"File '{fileName}' already exists in folder '{folderPath}'")

    def getSavedRaw(self, i: int) -> str:
        folderPath = "/Users/shubham/Code/personal/ReadingAssistant/apis/testpdfs/modelOutput/"
        # Construct the filename with "Chunk+i.json"
        filename = f"Chunk{i}.json,"
        filepath = folderPath + filename

        try:
            # Open the JSON file
            with open(filepath, 'r', encoding='utf-8') as file:
                # Load the JSON data
                json_data = json.load(file)

                # Check if the data is a list with at least one element
                if isinstance(json_data, list) and len(json_data) > 0:
                    # Retrieve the 'raw' value from the first element
                    raw_value = json_data[0].get('raw', '')
                    return raw_value
                else:
                    # Return an empty string if the JSON structure is unexpected
                    return ''
        except FileNotFoundError:
            # Handle the case where the file is not found
            print(f"File {filename} not found.")
            return ''
        except json.JSONDecodeError:
            # Handle JSON decoding errors
            print(f"Error decoding JSON from file {filename}.")
            return ''
    
    def processQuery(self, indexName: str, fileKey: int, query: str, tillChunk:int=None) -> Dict[str, Any]:
        # todo better query for model to ensure that it always returns in the same format
        # todo better search in pdf, maybe use vector search and try to find the most similar text
        # todo add better filter in the query for tillChunk
        dbResponse = self.dbHandler.searchInIndex(indexName, query, str(tillChunk))

        if not isinstance(dbResponse, dict):
            log.error(dbResponse)
            raise TypeError("response from db is not a dict")

        if "hits" not in dbResponse:
            log.error(dbResponse)
            raise TypeError("response dict from db has no attribute hits") 
        
        hits = dbResponse['hits']
        log.info(f"got {len(hits)} hits")

        # when we have docs inserted properly
        # filteredAndSorterHits = sorted([item for item in hits if item['chunkNumber'] > 5], key=lambda x: x['_score'])

        # sortedHits = sorted(hits, key=lambda hit: hit['_score'], reverse=True)
        response: Dict[Any, Any] = {}
        i = 0
        for hit in hits:
            context = hit['raw']

            systemPrompt = self.claudeManager.generateSystemPromptForUserQuestion(context)
            modelResponseRaw = self.claudeManager.sendMessage("user", systemPrompt, query)

            resDict = self.claudeManager.cleanUserQueryResponse(modelResponseRaw)
                
            for res in resDict:
                if "error" in res:
                    log.warn(f"claude did not have enough context, continuing")
                    continue
                
                if "response" not in res and "verbatim_line" not in res:
                    log.warn(f"claude dict is not proper {modelResponseRaw}")

                verbatimLine = res["verbatim_line"]
                modelReason = res["response"]

                chunkNumber = hit['chunkNumber']
                found, pageNumber = self.pdfManager.search(fileKey, chunkNumber, verbatimLine)

                response[i] = {
                    "modelResponse": modelReason,
                    "verbatimLine": verbatimLine
                }

                if not found:
                    i+=1
                    log.warn(f"Did not find verbatim line {verbatimLine} in chunk {chunkNumber}")
                    continue

                if pageNumber not in response[i]:
                    response[i]["verbatimLine"] = {}
                
                response[i]["verbatimLine"]['pageNumber'] = pageNumber
                response[i]["verbatimLine"]['line'] = verbatimLine
                i+=1

        return response
