import logging as log
from UniqueDict import UniqueDict
from PdfManager import PdfManager
from ClaudeManager import ClaudeManager

class ReadingAssistant():
    def __init__(self, claudeManager: ClaudeManager, pdfManager: PdfManager, copyPromptsToClipboard=False):
        self.claudeManager = claudeManager
        self.pdfManager = pdfManager
        self.copyPrompts = copyPromptsToClipboard

    def generateSummary(self, filepath: str, pagesPerChunk: int):
        fileId = self.pdfManager.addFile(filepath, pagesPerChunk)

        nextChunk = self.pdfManager.readNextChunk(fileId)
        nextChunk = self.pdfManager.readNextChunk(fileId)

        log.info(f"Done reading, stats are \n {self.pdfManager.getFileStats(fileId)}")
