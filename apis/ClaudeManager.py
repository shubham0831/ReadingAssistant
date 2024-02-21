import anthropic
from anthropic import Anthropic
import logging as log
from UniqueDict import UniqueDict
from typing import Any, Literal, Tuple, Dict, List
from Prompts import *
import re
import json

USER = "user"
ASSISTANT = "assistant"

class ClaudeManager():
    def __init__(self, config: UniqueDict):
        self.config = config

        self.client = Anthropic(
            api_key = self.config.get("accessToken"),
        )

        self.maxTokens = self.config.get("maxTokens")
        self.model = self.config.get("model")

    def sendMessage(self, role: str, systemPrompt:str, userPrompt: str) -> str:
        #return """Here is a summary of the text you provided:\n\n
        #Summary:\nThe text is an excerpt from the science fiction novel Dune by Frank Herbert. It describes events taking place on the planet Caladan in the week before the Atreides family departs for the desert planet Arrakis. \n\nAn old witch visits the mother of Paul Atreides, the fifteen-year-old son of Duke Leto Atreides. She questions whether Paul is small for his age and says he will need his wits to meet her "gom jabbar" the next day. Paul wonders what a gom jabbar is. \n\nThere is discussion of the challenges the Atreides family faces - their mortal enemies, the Harkonnens, are relinquishing control of the valuable spice melange on Arrakis, which the Atreides are to take over. However, this victory may arouse jealousy among other powerful families in the Landsraad. Thufir Hawat, the Duke\'s Master of Assassins, warns of deadly peril despite appearances.\n\nPaul dreams of a solemn cavern on Arrakis, filled with Fremen "free people" who live in the deserts beyond the rule of the Padishah Emperor. He wakes thinking of the uncertainties that await on this new planet that will be so different from his water-rich home on Caladan.\n\n
        #Key Points:\n\n1. An old witch visits Paul Atreides and his mother before their departure.\n\n2. The Atreides family is preparing to take over control of the spice melange on the desert planet Arrakis. \n\n3. There are warnings about the dangers they will face despite the appearance of victory.\n\n4. Paul dreams about the little-known Fremen people who inhabit Arrakis.\n\n5. He contemplates the challenges of adjusting to life on Arrakis so different from his home planet.\n\n
        #FAQs:\n\n1. Who is Paul Atreides?\n\n2. Why are the Atreides going to Arrakis? \n\n3. What is melange?\n\n4. Who are the Fremen?\n\n5. What does the old witch want with Paul?\n\n6. What is a gom jabbar? \n\n7. Why does Arrakis contain deadly peril for the Atreides?\n\n8. What are Paul\'s thoughts and feelings about leaving Caladan?\n\n9. What might life be like on Arrakis?\n\n10. What might happen in the next part of the story?"""
        #return "" # to avoid making accidental calls to anthropic, remove when needed
        try:
            response = self.client.messages.create(
                max_tokens=1024,
                messages=[
                    {
                        "role": role,
                        "content": userPrompt,
                    }
                ],
                model=str(self.model),
                system=systemPrompt
            )
            return response.content[0].text
        except anthropic.APIConnectionError as e:
            log.error(f"The server could not be reached \n {e.__cause__}")
        except anthropic.RateLimitError as e:
            log.error("A 429 status code was received; we should back off a bit.")
        except anthropic.APIStatusError as e:
            log.error(f"Another non-200-range status code was received \n Status Code : {e.status_code} \n message : {e.response}")
    
        return "ERROR"
    
    def cleanResponse(self, response: str) -> Dict[str, Any]:
        response = response.strip()
        cleanResponse = response.split("Summary:")[1]
        cleanResponseSplit = cleanResponse.split("Key Points:")

        summary = cleanResponseSplit[0]
        keyPointsAndFaqs = cleanResponseSplit[1]

        keyPointsAndFaqsSplit = keyPointsAndFaqs.split("FAQs")
        keyPoints = keyPointsAndFaqsSplit[0]
        faqs = keyPointsAndFaqsSplit[1]

        summary = summary.replace("\n\n", "\n")
        keyPoints = keyPoints.replace("\n\n", "\n")
        faqs = faqs.replace("\n\n", "\n")

        returnDict = {
            "PreviousSummary" : summary,
            "PreviousKeyPoints" : keyPoints,
            "PreviousFAQs" : faqs
        }
    
        return returnDict 
    
    def generatePromptForSummary(self, content: str, context:str = "") -> Tuple[str, str]:
        # assumption is that if no context has been provided, then it is the start of the book
        if context == "":
            systemPrompt = prompts[CLAUDE_SYSTEM_PROMPT_NO_CONTEXT_SHORT].strip()
            userPrompt = content.strip()
            return systemPrompt, userPrompt
        
        newContext = context.replace(SUMMARY, PREVIOUS_SUMMARY)
        newContext = context.replace(KEY_POINT, PREVIOUS_KEY_POINTS)
        newContext = context.replace(FAQ_S, PREVIOUS_FAQ_S).strip()

        systemPrompt = prompts[CLAUDE_SYSTEM_PROMPT_CONTEXT]
        systemPrompt = systemPrompt.replace(CONTEXT_INSERTION_POINT, newContext).strip()

        userPrompt = content

        return systemPrompt, userPrompt
    
    def generateSystemPromptForUserQuestion(self, context: str) -> str:
        sysPrompt = prompts[USER_QUESTION_PROMPT]
        sysPrompt = sysPrompt.replace("CONTEXT_GOES_HERE", context)
        return sysPrompt
    
    def cleanUserQueryResponse(self, response: str) -> List[Dict[str, str]]:
        try:
            # Find the substring containing the list of dicts
            startIndex = response.find("[")
            endIndex = response.find("]") + 1
            listOfDictsStr = response[startIndex:endIndex]

            # Parse the JSON string into a list of dicts
            listOfDicts = json.loads(listOfDictsStr)
            return listOfDicts
        except (json.JSONDecodeError, ValueError):
            # Handle the case where the string cannot be decoded as a list of dicts
            print("Error decoding the string as a list of dicts.")
            return []
    