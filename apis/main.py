from flask import Flask, request
import logging as log
from Config import Config
from PdfManager import PdfManager
from ClaudeManager import ClaudeManager
from ReadingAssistant import ReadingAssistant
from DbHandler import DbHandler

PDF_FILE_PATH = "/Users/shubham/Code/personal/ReadingAssistant/apis/testpdfs/duneBook1.pdf"
INDEX_NAME = "DuneBookOne"
'''
TODO: Read this 
    Good document for end user use case, when they provide a question, we need to figure out the relevant summary to be used, etc
    https://www.marqo.ai/blog/from-iron-manual-to-ironman-augmenting-gpt-with-marqo-for-fast-editable-memory-to-enable-context-aware-question-answering
'''
if __name__ == '__main__':
    config = Config()
    log.basicConfig(level=config.get("logLevel"), format='%(asctime)s - %(levelname)s - %(message)s')
    
    dbHandler = DbHandler(config.get("db"))
    dbHandler.createIndexIfNotExist(INDEX_NAME)
    
    claudeManager = ClaudeManager(config.get("anthropic"))
    pdfManager = PdfManager()

    readingAssistant = ReadingAssistant(claudeManager, pdfManager, dbHandler, config.get("copyTextToClipboard"))
    summary = readingAssistant.generateSummary(PDF_FILE_PATH, config.get("pagesPerChunk"), 2)

    # clean up
    dbHandler.deleteAllIndexes()


# app = Flask(__name__)
# 
# @app.route('/', methods=['GET'])
# def handle_get_request():
#     print("got get request")
#     return 'OK'

# # Handle slash command
# @app.route('/', methods=['POST'])
# def handle_slash_command():
#     print("got post request")
#     return 'OK'

# def main():
#     print("running")

# if __name__ == '__main__':
#     app.run(port=config.get("port"), debug=True)  # Run the Flask app