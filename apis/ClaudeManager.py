import anthropic
from anthropic import Anthropic
import logging as log
from UniqueDict import UniqueDict
from typing import Any, Literal, Tuple
from Prompts import *

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
        return "" # to avoid making accidental calls to anthropic, remove when needed
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
    
    def generatePrompt(self, content: str, context:str = "") -> Tuple[str, str]:
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
    