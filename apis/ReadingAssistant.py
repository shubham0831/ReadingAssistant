import logging as log
from UniqueDict import UniqueDict
from PdfManager import PdfManager
from ClaudeManager import ClaudeManager
import PdfManager as pdfm
import ClaudeManager as cm
from typing import Any, Dict, List
import pyperclip
from DbHandler import DbHandler

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
        
        # self.pdfManager.readNextChunk(fileKey)
        # chunkContent = self.pdfManager.readNextChunk(fileKey)[pdfm.CONTENT]

        # userPrompt, systemPrompt = self.claudeManager.generatePrompt(chunkContent, context="")
        # pyperclip.copy(chunkContent)
        chunksRead = len(fileChunks)
        log.info(f"total number of chunks is {chunksRead}")

        documents: List[Dict[str, Any]] = []
        for i in range(0, chunksRead):
            chunk = fileChunks[i]
            chunkContent = chunk[pdfm.CONTENT]
            if (i % 5 == 0 and i != 0):
                log.info(f"read {i} out of {chunksRead} chunks, inserting chunk of 5")
                response = self.dbHandler.addDocuments(indexName, documents, ["text"])
                documents = []
                
            userPrompt, systemPrompt = self.claudeManager.generatePrompt(chunkContent, context="")
            prevSummary = self.claudeManager.sendMessage(cm.USER, systemPrompt, userPrompt)
            cleanResponse = self.claudeManager.cleanResponse(prevSummary)
            cleanResponse["chunkNumber"] = i
            cleanResponse["text"] = chunkContent
            documents.append(cleanResponse)
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
        
        log.info("Done readin the chunks, inserting to db now")
        return self.dbHandler.addDocuments(indexName, documents, ["text"])
    
    def processQuery(self, indexName: str, query: str) -> Dict[str, Any]:
        return self.dbHandler.searchInIndex(indexName, query)
