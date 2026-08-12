
from app.config.config import SUMMARY_PROMPT
from app.logger.logger import logger
from typing import List
from app.models.schemas import ChatMessage

class SummaryManager():

    def __init__(self, client):
        self.client = client

    def summarize_messages(self, old_summary: str, messages: List[ChatMessage]):
        """
        Summarize the given messages.

        Args:
            messages (list of {ChatMessage}): A list of messages to summarize.

        Returns:
            str: The summary of the messages.
        """

        convesation = "\n".join([f"{message.role}: {message.content}" for message in messages])

        summary_prompt = SUMMARY_PROMPT.format(existing_summary = old_summary, conversation = convesation)

        return self.__process_messages(summary_prompt)


    def __process_messages(self, prompt: str) -> str:
        """
        Process the given messages to prepare them for summarization.

        Args:
            prompt : prompt to process.

        Returns:
            summary of the message.
        """
        # Implement your message processing logic here
        summary = self.client.generate(prompt)
        logger.info(f"Summary : {summary}")
        return summary