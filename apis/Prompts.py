from UniqueDict import UniqueDict

CHAPTER_IDENTIFIER_PROMPT = "ChapterIdentifierPrompt"
RESPONSE_TYPE_PROMPT= "ResponseType"

PAGES_SUMMARY_PROMPT = "PagesSummaryPrompt"
NUM_WORDS_IN_SUMMARY = 500

CLAUDE_SYSTEM_PROMPT_CONTEXT = "ClaudeSystemPromptContext"
CLAUDE_SYSTEM_PROMPT_NO_CONTEXT = "ClaudeSystemPromptNoContext"
CLAUDE_SYSTEM_PROMPT_NO_CONTEXT_SHORT = "ClaudeSystemPromptNoContextShort"

CONTEXT_INSERTION_POINT = "CONTEXT_INSERTION_POINT"
SUMMARY = "Summary:"
KEY_POINT = "Key Points"
FAQ_S = "FAQs"
PREVIOUS_SUMMARY = "Previous Summary"
PREVIOUS_KEY_POINTS= "Previous Key Points"
PREVIOUS_FAQ_S = "Previous FAQs"

prompts = UniqueDict.fromDict(
    {
        CHAPTER_IDENTIFIER_PROMPT : """
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

            Keep in mind this is not a comprehensive list of examples, an author might decide to take some other approach for how they decide to break down chapters.

            Some books might have a different concept of chapters, where each chapter is just one part of the book and the individual chapters have different sub chapters, if this is the case, consider the sub chapters as chapters and follow the prompt which has been given to you.

            You'll know the sample text ends when I say so

            Beginning of sample text
        """,

        RESPONSE_TYPE_PROMPT : """
            Thats the end of the sample text, your reponse should be in the following format, I want nothing else
            it should be a list of dictionaries in python, each individual dictionaries will be in the following format:
                {
                    "chapterType": type of the chapter
                    "chapterNumber" : #chapter number as an integer,
                    "chapterIdentifier" : #the piece of text you used to identify the chapter verbatim
                    "firstLine": #first line of the chapter verbatim
                } 
            Do this for each chapter you identify
        """,

        PAGES_SUMMARY_PROMPT : f"""
            I am going to give you 2 values "blob" and "context".
            Blob is a piece of text and can be for any book, your job is to make a {NUM_WORDS_IN_SUMMARY} words summary of this value.
            Context is the context which you may use to help you form a better summary of the blob.

            Keep in mind that you may only produce the summary for the blob and nothing else and your summary should be exactly {NUM_WORDS_IN_SUMMARY} words long.
            Your output should just be the summary and nothing else. 

            Here are the 2 values : 
        """,

        CLAUDE_SYSTEM_PROMPT_NO_CONTEXT : f"""
            You are bob, a no nonsense text summarizer. Bob has one job and one job only, to summarize a blob of text he is given. 
            
            He summarizes everything and is incapable of doing anything else.
            An example of this is when the user says 'hi' to bob, he responds back with 'the user has said hi'.
            He does not answer any questions, all he does is provide a summary of what the user has given to him.
            His responses are to the point and just summaries of the text what the user has given to him. He does not know anything else besides how to provide a summary. He does not respond back to the users question, all he does is summarize. His responses are short and concise, it's just the summary of the text provided to him, he does not talk about himself at all, regardless of the text provided to him. He does not talk about his role, he does not talk about how long the summaries are that he generates, nothing. All he does is summarize the text which has been given to him. He does not even tell that he does not engage in conversations or what it is that he does. He does not even attempt to answer a question if provided with one. He is a robot, all he does is take in some text, and respond back with the summary of it.

            The summaries that bob produces of those text are very comprehensive, he leaves no room for any confusion about what has happened so far. The summary he provides always consists of 3 key parts, each separated by the unique identifiers "Summary", "Key Points", "FAQs"

            1) "Summary" : The summary itself, this is usually around {NUM_WORDS_IN_SUMMARY} words and is just the summary of the text
            2) "Key Points" : Key points, these are a list 5 key points which were covered in the text the user has provided
            3) "FAQs" : Questions, these are a list of 10 questions which this text answers

            Bob does not provide any other information whatsoever.

            Given this information, provide summary of the text which the user provides.
        """,

        CLAUDE_SYSTEM_PROMPT_CONTEXT : f"""
            You are bob, a no nonsense text summarizer. Bob has one job and one job only, to summarize a blob of text he is given. 
            
            He summarizes everything and is incapable of doing anything else.

            To help him produce a more comprehensive summary, bob is provided with three things, each separated with the unique identifier "Previous Summary", "Previous Key Points" and "Previous FAQs"

            1) "Previous Summary" : Is a summary of what has happened so far in the text
            2) "Previous Key Points" : Are some of the previous key points of what has happened.
            3) "Previous FAQs" : Are some of the questions which have been answered in the previous text.

            Bob uses these three things to come up with a very comprehensive summary of just the text which the user provides, he leaves no room for any confusion about what has happened so far. The summary he provides always consists of 3 key parts, each separated by the unique identifiers "Summary", "Key Points", "FAQs"

            1) "Summary" : The summary itself, this is usually around 500 words and is an exhaustive summary of the text
            2) "Key Points" : Key points, these are a list 5 key points which were covered in the text the user has provided
            3) "FAQs" : Questions, these are a list of 10 questions which this text answers, this list does not have the answer to these questions, it's just the questions themselves.

            Bob does not provide any other information whatsoever.

            Here are the 3 things which have been provided to bob:

            {CONTEXT_INSERTION_POINT}

            Given this information, provide summary of the text which the user provides.
        """,

        CLAUDE_SYSTEM_PROMPT_NO_CONTEXT_SHORT : f"""
            You are bob, a no nonsense text summarizer. Bob has one job and one job only, to summarize a blob of text he is given. 
            
            He summarizes everything and is incapable of doing anything else.
            
            The summaries that bob produces of those text are very comprehensive, he leaves no room for any confusion about what has happened so far. The summary he provides always consists of 3 key parts, each separated by the unique identifiers "Summary", "Key Points", "FAQs"
            
            1) "Summary" : The summary itself, this is usually around {NUM_WORDS_IN_SUMMARY} words and is an exhaustive summary of the text
            2) "Key Points" : Key points, these are a list 5 key points which were covered in the text the user has provided
            3) "FAQs" : Questions, these are a list of 10 questions which this text answers, this list does not have the answer to these questions, it's just the questions themselves.
            
            Bob does not provide any other information whatsoever.
            
            Given this information, provide summary of the text which the user provides.
        """
    }
)




"""
"Previous Summary":
            The text is an excerpt from the beginning of the science fiction novel Dune by Frank Herbert. It introduces the characters of Paul Atreides and his parents, Duke Leto Atreides and Lady Jessica. They are preparing to depart their home planet of Caladan to take over control of the desert planet Arrakis, source of the valuable spice melange. An old witch visits Paul on his last night on Caladan and mentions testing him with something called a "gom jabbar" when they arrive on Arrakis. Paul wonders what this test will be as he drifts off the sleep, dreaming of a cavern on Arrakis full of fremen, the planet's native inhabitants. 

            "Previous Key Points":
            1. Paul Atreides is the 15-year-old son of Duke Leto Atreides and Lady Jessica.
            2. The Atreides family is leaving their home planet Caladan to take control of the desert planet Arrakis. 
            3. Arrakis is the only source of the valuable spice melange which extends life and makes space travel possible. 
            4. The Harkonnen family previously had control of Arrakis for 80 years but are now leaving.
            5. An old witch visits Paul and mentions testing him with a "gom jabbar" when he arrives on Arrakis.

            "Previous FAQs":  
            1. Who is Paul Atreides?
            2. Where is the Atreides family moving to and why? 
            3. What is melange spice and why is it valuable?
            4. Who is leaving control of Arrakis before the Atreides take over?
            5. What does the old witch say she will test Paul with?
            6. What are Paul's dreams hinting at?
            7. Who are the native inhabitants of Arrakis called? 
            8. What is a gom jabbar?
            9. Who is training Paul on Caladan?
            10. What class system does Arrakis not follow rigidly?
"""

"""
 Here is a summary of the text you provided:

Summary:
The text is an excerpt from the novel Dune by Frank Herbert. It describes the events leading up to the departure of the Atreides family from their home planet of Caladan to the desert planet of Arrakis. The passage introduces key characters such as Paul Atreides and his mother Lady Jessica, as well as mentioning important elements of the Dune universe like melange spice and the Fremen people. An aged Reverend Mother visits Paul on the night before their departure and alludes to testing him with something called a "gom jabbar". The excerpt builds an air of mystery and foreboding about the family's tenure on Arrakis.

Key Points:
1. Reverend Mother visits Paul Atreides on the night before the family's departure to Arrakis
2. She mentions testing Paul with a "gom jabbar"
3. The Atreides are replacing their enemies, the Harkonnens, as fief rulers of the planet Arrakis
4. Arrakis is a desert planet valuable for production of the spice melange
5. Native Fremen tribes live in the deserts of Arrakis

FAQs:
1. Who is the Reverend Mother that visits Paul?
2. What is the gom jabbar she mentions? 
3. Why are the Atreides taking over from the Harkonnens on Arrakis?
4. What is melange spice and why is it important?
5. Who are the Fremen and what is their role in the story?
"""

"""
 Here is a summary of the text you provided:

Summary:
The text is an excerpt from the novel Dune by Frank Herbert. It describes the events leading up to the departure of the Atreides family from their home planet of Caladan to the desert planet of Arrakis. The passage introduces key characters such as Paul Atreides and his mother Lady Jessica, as well as mentioning important elements of the Dune universe like melange spice and the Fremen people. An aged Reverend Mother visits Paul on the night before their departure and alludes to testing him with something called a "gom jabbar". The excerpt builds an air of mystery and foreboding about the family's tenure on Arrakis.

Key Points:
1. Reverend Mother visits Paul Atreides on the night before the family's departure to Arrakis
2. She mentions testing Paul with a "gom jabbar" which he does not understand
3. The Atreides are replacing their enemies, the Harkonnens, as rulers of the planet Arrakis
4. Arrakis is a desert planet valuable for production of the spice melange
5. Native Fremen tribes live in the deserts of Arrakis

FAQs:
1. Who is the Reverend Mother that visits Paul?
2. What is her relationship with Paul's mother Lady Jessica?
3. Why does the Reverend Mother suggest Paul get extra sleep? 
4. What role do the Harkonnens and melange spice play on Arrakis?
5. Why does Thufir Hawat warn that the Duke's popularity is dangerous?
6. What is life like for natives on Arrakis away from the rulers?
7. What might the Reverend Mother's test involve for Paul?
8. Why might Paul not miss his home planet of Caladan?
9. Who are the Fremen tribes mentioned living in Arrakis' deserts?  
10. What events or signs foreshadow coming challenges on Arrakis?
"""

# resp no context
"""
'Here is a summary of the text you provided:\n\nSummary:\nThe text is an excerpt from the science fiction novel Dune by Frank Herbert. It describes events taking place on the planet Caladan in the week before the Atreides family departs for the desert planet Arrakis. \n\nAn old witch visits the mother of Paul Atreides, the fifteen-year-old son of Duke Leto Atreides. She questions whether Paul is small for his age and says he will need his wits to meet her "gom jabbar" the next day. Paul wonders what a gom jabbar is. \n\nThere is discussion of the challenges the Atreides family faces - their mortal enemies, the Harkonnens, are relinquishing control of the valuable spice melange on Arrakis, which the Atreides are to take over. However, this victory may arouse jealousy among other powerful families in the Landsraad. Thufir Hawat, the Duke\'s Master of Assassins, warns of deadly peril despite appearances.\n\nPaul dreams of a solemn cavern on Arrakis, filled with Fremen "free people" who live in the deserts beyond the rule of the Padishah Emperor. He wakes thinking of the uncertainties that await on this new planet that will be so different from his water-rich home on Caladan.\n\nKey Points:\n\n1. An old witch visits Paul Atreides and his mother before their departure.\n\n2. The Atreides family is preparing to take over control of the spice melange on the desert planet Arrakis. \n\n3. There are warnings about the dangers they will face despite the appearance of victory.\n\n4. Paul dreams about the little-known Fremen people who inhabit Arrakis.\n\n5. He contemplates the challenges of adjusting to life on Arrakis so different from his home planet.\n\nFAQs:\n\n1. Who is Paul Atreides?\n\n2. Why are the Atreides going to Arrakis? \n\n3. What is melange?\n\n4. Who are the Fremen?\n\n5. What does the old witch want with Paul?\n\n6. What is a gom jabbar? \n\n7. Why does Arrakis contain deadly peril for the Atreides?\n\n8. What are Paul\'s thoughts and feelings about leaving Caladan?\n\n9. What might life be like on Arrakis?\n\n10. What might happen in the next part of the story?'
"""

# resp with context
"""
'Here is a summary of the additional text provided:\n\nSummary: The passage describes several characters - the Baron Vladimir Harkonnen, Piter, and Feyd-Rautha - looking at a relief globe of the desert planet Arrakis. The Baron explains with glee how the Atreides family is heading into a trap on Arrakis. Piter and Feyd-Rautha listen as the Baron traces details on the globe, describing the lack of water and polar ice caps that make Arrakis so inhospitable, yet also unique. The Baron and Piter anticipate the coming Harkonnen victory against House Atreides on the planet. \n\nKey Points:\n\n1. The Baron Vladimir Harkonnen spins a globe of Arrakis while speaking with Piter and Feyd-Rautha. \n\n2. The Baron describes features of Arrakis - lack of water, small polar caps - that make it extremely harsh but also unique.\n\n3. The Baron eagerly anticipates defeating House Atreides in a "unique victory" on Arrakis.\n\n4. Piter smiles, sharing in the Baron\'s anticipation of triumph over their enemies on the desert planet.\n\nFAQs: \n\n1. Who are the main characters described in this passage?\nThe Baron Vladimir Harkonnen, Piter, and Feyd-Rautha.\n\n2. Why do the Harkonnens anticipate victory against House Atreides on Arrakis? \nThey have set a trap for the Atreides on the inhospitable desert planet.\n\n3. What features make Arrakis so unique?\nThe complete lack of water and very small polar ice caps.\n\n4. How does the Baron feel about the upcoming conflict with House Atreides?\nHe is eager and extremely pleased, anticipating a great victory.\n\n5. What role might Piter and Feyd-Rautha play in the Baron\'s plans?\nAs his mentat and heir, they assist and share in the Baron\'s schemes against his enemies.'
"""

# NOTES
chapterStartTypes = {
    "Number",
    "Random Quote", # dune
    "Character Name", # game of throne
}