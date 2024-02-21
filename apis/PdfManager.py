import fitz 
import logging as log
from UniqueDict import UniqueDict
from typing import Dict, Any, Tuple
from anthropic import Anthropic
import chardet
import ast
import re

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
CONTENT_DICT = "contentDict"
START_PAGE = "startPage"
END_PAGE = "endPage"
PAGE_DICT = "pageDict"

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
    
    def read(self, fileKey: int, startPage: int, endPage: int, cleanText: bool = True) -> Tuple[str, Dict[int, str], int]:
        docDict = self._getDocDict(fileKey)

        doc = docDict["doc"]
        totalPages = docDict[TOTAL_PAGES]

        endPage = min(endPage, totalPages) 
        content = ""
        pageDict = {}
        for pageNum in range(startPage, endPage):
            page = doc[pageNum]
            content += page.get_text()
            pageDict[pageNum] = content
        # will be useful in knowing where to resume from
        docDict[PAGES_READ] = endPage

        if endPage == totalPages:
            docDict[FINISHED]= True

        if cleanText:
            content = self.cleanText(content)

        tokenCount = self.anthropicTokenCounter.count_tokens(content)
        return content, pageDict, tokenCount
    
    def readComplete(self, fileKey: int) -> dict:
        docDict = self._getDocDict(fileKey)

        pagesPerChunk = docDict[PAGES_PER_CHUNK]

        contentDict = {}
        chunkNumber = 0
        startPage = 0
        endPage = startPage + pagesPerChunk

        while docDict[FINISHED] == False:
            content, pageDict, tokenCount = self.read(fileKey, startPage, endPage)
            contentDict[chunkNumber] = {
                CONTENT:content,
                TOKEN_COUNT:tokenCount,
                START_PAGE: startPage,
                END_PAGE: endPage,
                PAGE_DICT: pageDict
            }
            chunkNumber += 1
            startPage = endPage
            endPage = startPage + pagesPerChunk
            docDict[CHUNKS_READ] += 1
            docDict[TOKENS_READ] += tokenCount

        docDict[CONTENT_DICT] = contentDict
        
        return contentDict
    
    def readNextChunk(self, fileKey: int) -> dict:
        docDict = self._getDocDict(fileKey)
        pagesPerChunk = docDict[PAGES_PER_CHUNK]
        chunksRead = docDict[CHUNKS_READ]

        startPage = 0
        if chunksRead != 0:
            startPage = pagesPerChunk * chunksRead
        
        endPage = startPage + pagesPerChunk
        content, pageDict, tokenCount = self.read(fileKey, startPage, endPage)
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

    def cleanText(self, content: str) -> str:
        # try:
        #     textEncoding = chardet.detect(content.encode())["encoding"]

        #     if not textEncoding:
        #         textEncoding = "utf-8"
        #     else:
        #         textEncoding = str(textEncoding)

        #     decodedText = content.encode(textEncoding).decode("unicode_escape")
        #     cleanText = decodedText
        # except UnicodeDecodeError:
        #     log.warn("Error in decoding text, aborting this operation")
        #     cleanText = content
        # content = content.replace(r"\u", r"\\u")
        # content = ast.literal_eval(f'r"""{content}"""')
        cleanText = content.encode("utf-8").decode("unicode_escape")
        cleanText = re.sub(r'\\u([0-9a-fA-F]{4})', lambda m: chr(int(m.group(1), 16)), cleanText)
        cleanText = ''.join(char for char in cleanText if char.isprintable())
        cleanText = cleanText.strip()
        cleanText = ' '.join(cleanText.split())

        return cleanText

    def search(self, fileKey: int, chunkNumber:int, value:str) -> Tuple[bool, int]:
        docDict = self._getDocDict(fileKey)
        contentDict = docDict[CONTENT_DICT][chunkNumber]
        pageDict = contentDict[PAGE_DICT]

        for pageNumber, pageContent in pageDict.items():
            if value in pageContent:
                return True, pageNumber 

        return False, -1