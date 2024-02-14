from flask import Flask, request
import logging as log
from Config import Config
from PdfManager import PdfManager
from ClaudeManager import ClaudeManager
from ReadingAssistant import ReadingAssistant

PDF_FILE_PATH = "/Users/shubham/Code/personal/ReadingAssistant/apis/testpdfs/duneBook1.pdf"

if __name__ == '__main__':
    config = Config()
    log.basicConfig(level=config.get("logLevel"), format='%(asctime)s - %(levelname)s - %(message)s')
    
    claudeManager = ClaudeManager(config.get("anthropic"))
    pdfManager = PdfManager()

    readingAssistant = ReadingAssistant(claudeManager, pdfManager, config.get("copyPromptToClipboard"))
    summary = readingAssistant.generateSummary(PDF_FILE_PATH, config.get("pagesPerChunk"))


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