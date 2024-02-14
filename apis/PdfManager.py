import fitz 
import logging as log
from UniqueDict import UniqueDict
from typing import Dict, Any, Tuple
from anthropic import Anthropic

class PdfManager:
    def __init__(self):
        self.filesDict = dict()
        self.lastKey = 0
        self.anthropicTokenCounter = Anthropic()
                
    def addFile(self, filePath: str, pagesPerChunk: int) -> int:
        key = self.lastKey
        self.filesDict[key] = {
            "loaded": False,
            "filePath": filePath,
            "doc": None,
            "totalPages": None,
            "pagesRead": 0,
            "finished": False,
            "pagesPerChunk": pagesPerChunk,
            "chunksRead": 0,
            "tokensRead": 0
        }
        
        self.lastKey += 1
        return key
    
    def read(self, fileKey: int, startPage: int, endPage: int) -> Tuple[str, int]:
        docDict = self._getDocDict(fileKey)

        doc = docDict["doc"]
        totalPages = docDict['totalPages']

        endPage = min(endPage, totalPages) 
        content = ""
        for pageNum in range(startPage, endPage):
            page = doc[pageNum]
            content += page.get_text()
        
        # will be useful in knowing where to resume from
        docDict["pagesRead"] = endPage

        if endPage == totalPages:
            docDict['finished'] = True

        tokenCount = self.anthropicTokenCounter.count_tokens(content)
        return content, tokenCount
    
    def readComplete(self, fileKey: int) -> dict:
        docDict = self._getDocDict(fileKey)

        pagesPerChunk = docDict["pagesPerChunk"]

        contentDict = {}
        chunkNumber = 0
        startPage = 0
        endPage = startPage + pagesPerChunk

        while docDict['finished'] == False:
            content, tokenCount = self.read(fileKey, startPage, endPage)
            contentDict[chunkNumber] = {"content":content, "tokenCount":tokenCount}
            chunkNumber += 1
            startPage = endPage
            endPage = startPage + pagesPerChunk
            docDict["chunksRead"] += 1
            docDict["tokensRead"] += tokenCount

        return contentDict
    
    def readNextChunk(self, fileKey: int) -> dict:
        docDict = self._getDocDict(fileKey)
        pagesPerChunk = docDict["pagesPerChunk"]
        chunksRead = docDict["chunksRead"]

        startPage = 0
        if chunksRead != 0:
            startPage = pagesPerChunk * chunksRead
        
        endPage = startPage + pagesPerChunk
        content, tokenCount = self.read(fileKey, startPage, endPage)
        docDict["chunksRead"] += 1

        contentDict = dict()
        contentDict[0] = {"content":content, "tokenCount":tokenCount}

        docDict["tokensRead"] += tokenCount
        
        return contentDict

    def getFileStats(self, fileKey: int) -> dict:
        return self._getDocDict(fileKey)

    def _getDocDict(self, fileKey: int) -> dict:
        docDict = self.filesDict[fileKey]

        if docDict["loaded"] == False:
            filePath = docDict["filePath"]
            doc = fitz.open(filePath)
            totalPages = doc.page_count

            docDict["loaded"] = True
            docDict["doc"] = doc
            docDict["totalPages"] = totalPages
        
        return docDict


# from Prompts import *
# import pyperclip

# PDF_FILE_PATH = "/Users/shubham/Code/personal/ReadingAssistant/apis/testpdfs/duneBook1.pdf"

# def pdfToText(pdfPath: str):
#     doc = fitz.open(pdfPath)

#     # totalPages = doc.page_count

#     context = ""
#     blob = ""

#     for pageNum in range(100):
#        page = doc[pageNum]
#        context += page.get_text()
    
#     for pageNum in range(100, 200):
#         page = doc[pageNum]
#         blob += page.get_text()

#     doc.close()
#     return blob, context

# # Example usage
# blob, context = pdfToText(PDF_FILE_PATH)

# samplePrompt = prompts[PAGES_SUMMARY_PROMPT] + f"\n here is the blob : {blob} \n here is the context : {context}"

# pyperclip.copy(samplePrompt)
# # singleLineText = ' '.join(samplePrompt.splitlines())
# # singleLineText = singleLineText.strip()
# # singleLineText = ' '.join(singleLineText.split())

# # client = Anthropic()
# # print(client.count_tokens(singleLineText))
# # pyperclip.copy(singleLineText)