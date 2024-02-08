from UniqueDict import UniqueDict
prompts = UniqueDict.fromDict({
"ChapterIdentifierPrompt" : """
    I'm going to give you the first 100 pages from a book which I have scanned. Keep your response short and concise. 
    For the first chapter return the piece of text you used to identify that the chapter has started.
    For each chapter you identify I want you to give me the following :
        1) the chapter number, if there is no chapter number available, start from chapter 1 and keep incrementing. 
        2) the first sentence from the chapter
        3) the piece of text you used to identify the chapter.
        4) the type of the chapter, some books might have an appendix, so the type will be "appendix", for regular chapters the type will be "regular"
    
    Here are some of the different ways a chapter might start
        1) They might have a chapter number at the start of the page, such as chapter 1
        2) They might have a random blob of text which is short and concise, it might be the name of the chapter
        3) They might have a random blob of text at the start of the page, which may or may not be related to what's happened before in the book and it may or may not relate to whats coming up in the chapter as well
        4) They might have a random quote from some one, this quote may or may not be related to what's happened before in the book and it may or may not relate to whats coming up in the chapter as well
        5) There might be no indication of when the chapter starts, it might just be that the context or the narrator is now different

    Keep in mind this is not a comprehensive list of examples, an author might decide to take some other approach for how they decide to break down chapters.

    Some books might have a different concept of chapters, where each chapter is just one part of the book and the individual chapters have different sub chapters, if this is the case, consider the sub chapters as chapters and follow the prompt which has been given to you.

    Your reponse should be in the form of a list of dictionaries in python, each individual dictionaries will be in the following format:
        {
            "chapterType": type of the chapter
            "chapterNumber" : #chapter number as an integer,
            "chapterIdentifier" : #the piece of text you used to identify the chapter
            "firstLine": #first line of the chapter
        }
""",
}
)