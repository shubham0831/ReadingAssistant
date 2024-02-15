import logging as log
from UniqueDict import UniqueDict
from PdfManager import PdfManager
from ClaudeManager import ClaudeManager
import PdfManager as pdfm
import ClaudeManager as cm
from typing import Any
import pyperclip

class ReadingAssistant():
    def __init__(self, claudeManager: ClaudeManager, pdfManager: PdfManager, copyTextToClipboard=False):
        self.claudeManager = claudeManager
        self.pdfManager = pdfManager
        self.copyText = copyTextToClipboard

    def generateSummary(self, filepath: str, pagesPerChunk: int, maxChunks: int = -1):
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
        prevSummary = ""
        for i in range(0, chunksRead):
            chunk = fileChunks[i]
            chunkContent = chunk[pdfm.CONTENT]

            systemPrompt, userPrompt = self.claudeManager.generatePrompt(chunkContent, context=prevSummary)
            prevSummary = self.claudeManager.sendMessage(cm.USER, systemPrompt, userPrompt)
            # todo store these summaries in a database, the dummies are in the comment of prompts.py, use them and store those in the db
            

        return
