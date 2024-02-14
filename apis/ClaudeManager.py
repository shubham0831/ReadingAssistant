import anthropic
from anthropic import Anthropic
import logging as log
from UniqueDict import UniqueDict

class ClaudeManager():
    def __init__(self, config: UniqueDict):
        self.config = config

        self.client = Anthropic(
            api_key = self.config.get("accessToken"),
        )

        self.maxTokens = self.config.get("maxTokens")
        self.model = self.config.get("model")

    def sendMessage(self, role: str, prompt: str) -> str:
        try:
            response = self.client.messages.create(
                max_tokens=1024,
                messages=[
                    {
                        "role": role,
                        "content": prompt,
                    }
                ],
                model=self.model,
            )

            return response.content
        except anthropic.APIConnectionError as e:
            log.error(f"The server could not be reached \n {e.__cause__}")
        except anthropic.RateLimitError as e:
            log.error("A 429 status code was received; we should back off a bit.")
        except anthropic.APIStatusError as e:
            log.error(f"Another non-200-range status code was received \n Status Code : {e.status_code} \n message : {e.response}")
    
    def buildPrompt(self) -> None:
        return None