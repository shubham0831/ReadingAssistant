import fitz 
import logging as log
from UniqueDict import UniqueDict
from typing import Dict, Any, Tuple
from anthropic import Anthropic

LOADED = "loaded"
FILE_PATH = "filePath"
DOC = "doc"
TOTAL_PAGES = "totalPages"
PAGES_READ = "pagesRead"
FINISHED = "finished"
PAGES_PER_CHUNK = "pagesPerChunk"
CHUNKS_READ = "chunksRead"
TOKENS_READ = "tokensRead"
CONTENT = "content"
TOKEN_COUNT = "tokenCount"

class PdfManager:
    def __init__(self):
        self.filesDict = dict()
        self.lastKey = 0
        self.anthropicTokenCounter = Anthropic()
                
    def addFile(self, filePath: str, pagesPerChunk: int) -> int:
        log.info(f"adding file to pdf reader, \n file path is {filePath} \n pages per chunk is {pagesPerChunk}")
        key = self.lastKey
        self.filesDict[key] = {
            LOADED: False,
            FILE_PATH: filePath,
            DOC: None,
            TOTAL_PAGES: None,
            PAGES_READ: 0,
            FINISHED: False,
            PAGES_PER_CHUNK: 10,
            CHUNKS_READ: 0,
            TOKENS_READ: 0
        }
        self.lastKey += 1
        return key
    
    def read(self, fileKey: int, startPage: int, endPage: int) -> Tuple[str, int]:
        docDict = self._getDocDict(fileKey)

        doc = docDict["doc"]
        totalPages = docDict[TOTAL_PAGES]

        endPage = min(endPage, totalPages) 
        content = ""
        for pageNum in range(startPage, endPage):
            page = doc[pageNum]
            content += page.get_text()
        
        # will be useful in knowing where to resume from
        docDict[PAGES_READ] = endPage

        if endPage == totalPages:
            docDict[FINISHED]= True

        tokenCount = self.anthropicTokenCounter.count_tokens(content)
        return content, tokenCount
    
    def readComplete(self, fileKey: int) -> dict:
        docDict = self._getDocDict(fileKey)

        pagesPerChunk = docDict[PAGES_PER_CHUNK]

        contentDict = {}
        chunkNumber = 0
        startPage = 0
        endPage = startPage + pagesPerChunk

        while docDict[FINISHED] == False:
            content, tokenCount = self.read(fileKey, startPage, endPage)
            contentDict[chunkNumber] = {CONTENT:content, TOKEN_COUNT:tokenCount}
            chunkNumber += 1
            startPage = endPage
            endPage = startPage + pagesPerChunk
            docDict[CHUNKS_READ] += 1
            docDict[TOKENS_READ] += tokenCount

        return contentDict
    
    def readNextChunk(self, fileKey: int) -> dict:
        docDict = self._getDocDict(fileKey)
        pagesPerChunk = docDict[PAGES_PER_CHUNK]
        chunksRead = docDict[CHUNKS_READ]

        startPage = 0
        if chunksRead != 0:
            startPage = pagesPerChunk * chunksRead
        
        endPage = startPage + pagesPerChunk
        content, tokenCount = self.read(fileKey, startPage, endPage)
        docDict[CHUNKS_READ] += 1

        contentDict = {CONTENT:content, TOKEN_COUNT:tokenCount}

        docDict[TOKENS_READ] += tokenCount

        return contentDict
    
    def readFirstNChunks(self, fileKey: int, n: int) -> dict:
        docDict = self._getDocDict(fileKey)
        pagesPerChunk = docDict[PAGES_PER_CHUNK]
        startPage = 0
        endPage = startPage + pagesPerChunk

        log.warn(f"reading first {n} chunks, resetting stats on chunks read")

        docDict[PAGES_READ] =  0
        docDict[FINISHED] =  False
        docDict[CHUNKS_READ] = 0
        docDict[TOKENS_READ] = 0

        contentDict = {}
        chunkNumber = 0
        while docDict[CHUNKS_READ] != n:
            chunkDict = self.readNextChunk(fileKey)
            contentDict[chunkNumber] = {
                CONTENT: chunkDict["content"],
                TOKEN_COUNT: chunkDict["tokenCount"]
            }
            chunkNumber += 1

        return contentDict

    def getFileStats(self, fileKey: int) -> dict:
        return self._getDocDict(fileKey)
    
    def getFinishedFileReading(self, fileKey: int) -> bool:
        return self._getDocDict(fileKey)[FINISHED]

    def _getDocDict(self, fileKey: int) -> dict:
        docDict = self.filesDict[fileKey]

        if docDict[LOADED] == False:
            filePath = docDict["filePath"]
            doc = fitz.open(filePath)
            totalPages = doc.page_count

            docDict[LOADED] = True
            docDict[DOC] = doc
            docDict[TOTAL_PAGES] = totalPages
        
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