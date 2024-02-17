from flask import Flask, request, g
import logging as log
from Config import Config
from PdfManager import PdfManager
from ClaudeManager import ClaudeManager
from ReadingAssistant import ReadingAssistant
from DbHandler import DbHandler

PDF_FILE_PATH = "/Users/shubham/Code/personal/ReadingAssistant/apis/testpdfs/duneBook1.pdf"
INDEX_NAME = "DuneBookOne"

app = Flask(__name__)

def getDb():
    if 'db' not in g:
        g.db = DbHandler(Config().get("db"))
        g.db.deleteAllIndexes()
        g.db.createIndexIfNotExist(INDEX_NAME)
    return g.db

def getClaudeManager():
    if 'cm' not in g:
        g.cm = ClaudeManager(Config().get("anthropic"))
    return g.cm

def getPdfManager():
    if 'pm' not in g:
        g.pm = PdfManager()
    return g.pm

def getReadingAssistant():
    if 'ra' not in g:
        dbHandler = getDb()
        claudeManager = getClaudeManager()
        pdfManager = getPdfManager()
        g.ra = ReadingAssistant(claudeManager, pdfManager, dbHandler, Config().get("copyTextToClipboard"))
        g.ra.preprocess(PDF_FILE_PATH, INDEX_NAME, 100)

    return g.ra

@app.route('/', methods=['GET'])
def handleGet():
    log.info("Got a GET request")
    return '''
        <html>
        <head>
            <title>Flask Form Example</title>
        </head>
        <body>
            <h2>Submit Text</h2>
            <form method="post">
                <label for="user_input">Enter Text:</label>
                <input type="text" id="user_input" name="user_input" required>
                <br>
                <button type="submit">Submit</button>
            </form>
        </body>
        </html>
    '''
@app.route('/', methods=['POST'])
def handlePost():
    getDb() # cleans the db
    readingAssistant = getReadingAssistant()
    log.info("Got a POST request")
    query = request.form['user_input']
    response = readingAssistant.processQuery(INDEX_NAME, query)
    print("debug")
    return response

# Get and post for convinience purpose
@app.route('/shutdown', methods=['GET, POST'])
def shutdown():
    # Check if the request comes from localhost for security reasons
    log.warn('Shutting down server...')
    g.db.deleteAllIndexes()
    shutdown_func = request.environ.get('werkzeug.server.shutdown')
    if shutdown_func:
        shutdown_func()

'''
TODO: Read this 
    Good document for end user use case, when they provide a question, we need to figure out the relevant summary to be used, etc
    https://www.marqo.ai/blog/from-iron-manual-to-ironman-augmenting-gpt-with-marqo-for-fast-editable-memory-to-enable-context-aware-question-answering
'''
if __name__ == '__main__':
    config = Config()
    log.basicConfig(level=config.get("logLevel"), format='%(asctime)s - %(levelname)s - %(message)s')

    log.info("Starting flask server")
    app.run(port=config.get("port"), debug=True)  # Run the Flask app