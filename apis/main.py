from flask import Flask, request, g
import logging as log
from Config import Config
from PdfManager import PdfManager
from ClaudeManager import ClaudeManager
from ReadingAssistant import ReadingAssistant
from DbHandler import DbHandler

PDF_FILE_PATH = "/Users/shubham/Code/personal/ReadingAssistant/apis/testpdfs/duneBook1.pdf"
INDEX_NAME = "DuneBookOne"

"""
doc ids
['21af09e1-4f4a-4da3-a042-5343555ec44a', '503e8ea8-93c6-4e1c-81f5-ece968f33086', 'fd33d68e-d49e-4650-b279-b2a58cf3bb60',
 'c8d2e182-e7a7-4a7a-9dd5-91795a23b782', 'add06b87-85d8-49d7-964f-415be0d3fc32', '85570f16-802b-43c8-b713-91536a713d2b',
 '88b90f2c-12f6-4a37-a0e4-7f17e15bd1d9', '88d876b9-00c6-4815-937f-5e9139d0485e', '9febe4f1-75a8-43c2-a84e-baf057215125',
 'ba499106-7341-409f-8a72-e757258fe967', 'e9718216-17e1-4706-a68d-75ef1fd686ab', '07ebd6a9-8c73-4889-af99-25c2b387f049',
 '88df3d42-54db-4a4f-9bf3-9a5d5533c094', '0ecf1338-497a-4bf9-bdef-670dd97e747e', '3a34c766-7e5d-4e96-a0cb-4989b7972aa2',
 '3b474fd4-850b-49e4-9c4c-2c4b6413e598']
"""
app = Flask(__name__)

docKeys = [
    '435dd457-e000-4ee4-a7e2-0501d966ca01', '3c863b60-99a7-4a62-a35b-a2c1bb6414cc','33e454dc-1395-4b82-ad9d-9145b1c28540',
    '5d224cee-be96-427b-9edc-703d3bd34fbe', 'f09dac77-2305-42c8-a7b5-95f5f5e1e10c', 'a754c1f7-1b4a-4490-bf1c-01077d485c77',
    '40ffe446-2508-4c4a-ae22-c1be628e417f', '1f981685-61ac-49b0-95f7-429720b416ee', '61dc5f61-b1d9-41ca-b4e9-381320121d90',
    '135e9579-0a7f-4401-b61c-15071233545c','f79eefce-ee73-405a-bad7-46a1a0359958', '02106b53-325c-4f1d-bad8-0e3efab63abb',
    'bd4fce28-99a9-4fce-b80a-3860e493ab51', '8160aae1-d563-4fe6-b64d-fa40e06af145', '6905bc06-fcee-48d7-b8da-883ee412e721',
    '75d134d2-8328-4ea9-9e4b-49e5523d0506', 'b58275bc-b2ce-4e3c-85dd-d5af2ac462ed', '36b7a02d-497b-4cfb-be10-277ee8b70676',
    'f48430df-40bb-4e4b-8d08-e016ac383ef2', '52c78523-7045-4eb8-8783-fceb27281b84', '07fbe236-83ea-41a2-9c98-97bd3403431a',
    '205ebe3f-322e-4de1-bfa4-d5f9b4d1a9bc', '2d19f1ae-2cc4-43ae-b4b2-2ed043c60519', '70c54e3a-8417-40f5-b4cd-90e813b25d59',
    '70465c44-e515-4c9b-8225-29f65472a8b7', '640c4095-583c-4cab-b451-07c72af0d4e1', '7e52c094-4a81-4ae6-9b1c-8fbc616068ed',
    'b2bc3f19-b290-4310-92ce-9bc5e8f34bb0', 'eb3c014b-2687-4b1e-805a-a7677d297b12', '1e9ec8b0-8383-45e3-b2b1-bfafe7992fdd',
    '01a31263-b884-429b-81e8-41634936e112', 'e5ae89a1-3490-4dc7-8927-feb49be1db2c', '1b1c1233-6c6d-4279-888f-5c77eaf7df7d',
    'fa50133a-7b2d-4fe9-863a-fc5976642a64', 'f6f238c9-9558-4729-a032-f623c4f22f83', '213f033f-95ac-4b3d-9d1b-c99e8a7e3c29',
    '33415a9f-10b7-4037-a3bb-88918074c894', '3da2caee-a766-40ad-b0ff-9e6b812cbbd9', 'a3b37d7e-ffc9-4be5-a74d-05b733659b95',
    'cadbd553-c321-40f6-8849-8ca651150659', 'a427fcf6-f961-4b26-beed-c1a7cb4a4592', '446ced36-3a6b-4027-abd8-a8cefec3b046',
    'd9b9edb9-8ffa-4c5f-8ac5-442912a04688', '42e46fbb-741f-464c-bcf0-630e305dcd54', 'd5ec5d10-f05f-42e6-95b9-bf04a0bd8a5e',
    'c4a9858c-6914-43b2-a396-e070e346b400', '7b4f80f3-9b5c-4cc7-bb48-9c20ab787bda', '46a65478-60e0-47be-92e6-01dceb7a42d1',
    '586a15a8-7106-4221-ac5c-54306e442858', 'e3dc0f66-e73b-4a7a-ab9e-c2f91c0df72e', 'ffefe93a-52b1-4f80-87dc-7237cc4bf08b',
    '505a5987-6bb5-4a4f-894c-c25449542b63', '484ea107-7fe4-4dea-9cbd-c299aecfcab9', '3498c841-432e-4999-ba4b-5d9d9a3dbbcd',
    '01b98081-caca-4653-887c-5bf77c500b17', 'aae0c1b0-7855-410e-9f90-436ae5acf3ec', 'abf2e08c-5be7-42e1-8712-1fd8a37750bd',
    '0390a03e-882e-4ea0-8523-3a465b7934b0']

def getDb(inContext: bool):
    if not inContext:
        db = DbHandler(Config().get("db"))
        # db.deleteAllIndexes()
        # db.createIndexIfNotExist(INDEX_NAME) 
        # db.getAllIndexes()
        return db

    if 'db' not in g:
        g.db = DbHandler(Config().get("db"))
        # g.db.deleteAllIndexes()
        # g.db.createIndexIfNotExist(INDEX_NAME)
    return g.db

def getClaudeManager(inContext: bool):
    if not inContext:
        return ClaudeManager(Config().get("anthropic"))

    if 'cm' not in g:
        g.cm = ClaudeManager(Config().get("anthropic"))
    return g.cm

def getPdfManager(inContext: bool):
    if not inContext:
        return PdfManager()

    if 'pm' not in g:
        g.pm = PdfManager()
    return g.pm

def getReadingAssistant(inContext: bool):
    dbHandler = getDb(inContext)
    claudeManager = getClaudeManager(inContext)
    pdfManager = getPdfManager(inContext)

    if not inContext:
        ra = ReadingAssistant(claudeManager, pdfManager, dbHandler, Config().get("copyTextToClipboard"))
        return ra

    if 'ra' not in g:
        g.ra = ReadingAssistant(claudeManager, pdfManager, dbHandler, Config().get("copyTextToClipboard"))
        g.ra.preprocess(PDF_FILE_PATH, INDEX_NAME, 100)

    return g.ra

@app.route('/', methods=['GET'])
def handleGet():
    log.info("Got a GET request")
    readingAssistant = getReadingAssistant()
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
    # getDb() # cleans the db
    readingAssistant = getReadingAssistant(inContext=True)
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

    # this will populate db with duplicate documents
    ra = getReadingAssistant(inContext=False)
    fileKey = ra.preprocess(PDF_FILE_PATH, INDEX_NAME, 100)
    log.info(f"preprocess complete fileKey is {fileKey}")
    res = ra.processQuery(INDEX_NAME, fileKey, "Why doesn't hawat like the reverend mother")

    print(res)
    # log.info("Starting flask server")
    # app.run(port=config.get("port"), debug=True)  # Run the Flask app