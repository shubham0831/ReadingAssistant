Reading assistant for mobile devices and ipads

Supported formats
    1) PDF
    2) EPUB

Features
    1) Interface from which user can read a file or document
    2) User can upload a book to the app
    3) Chat interface slider using which user can ask specific questions related to the book
    4) User will get their answer and a reference to which page/chapter did the bot use to generate the answer
    5) User will be able to configure which AI assistant they want to use for this and provide their token in the setting

Repositories
    1) Backend
        Python backend which contains the APIs which the mobile device will be calling
        Contains the vector db we use to get the context
    2) IOS
        App interface code for ios devices
    3) Android
        App interface code for android devices

Flow
    Once a user uploads a file, we generate the summary for each chapter and store that in a vector database
    When the user asks a question we get the context from the vector database and feed that context to the bot 
    We provide the bot with context and the users question - the bot returns the answer alongside the chapter and text in the summary from which the answer was derived
    We then use that summary to get the exact page and line which we then show the user - this is also returned by the bot

Future ideas
    Caching for regularly asked questions
    Make it a full fledged reader app in which the user can write their own notes
    Check for kindle support
