
from app.config.config import MAX_HISTORY_MESSAGES
from app.logger.logger import logger
from app.models.schemas import ConversationState, ChatMessage
from typing import List

class ConversationalMemory:

    def __init__(self):
        self.history: dict[str, ConversationState] = {}

    def add_message(self, conversation_id: str, role: str, content: str):
        """Add a message to the conversation history for a given conversation ID."""
        message = ChatMessage(role=role, content=content)
        if conversation_id not in self.history:
            self.history[conversation_id] = ConversationState(summary="", messages=[message])
        else:
            self.history[conversation_id].messages.append(message)


    def replace_messages(self, conversation_id: str, message: List[ChatMessage]):
        """ update the message for particular user"""
        self.history[conversation_id].messages = message 
        

    def get_conversation(self, conversation_id: str) -> List[ChatMessage]:
        """Retrieve the conversation history for a given conversation ID."""
        conversation = self.history.get(conversation_id, None)

        if conversation is None:
            logger.info(f"No conversation history found for {conversation_id}. Returning empty list.")
            return []   
        
        return conversation.messages

    def clear_history(self, conversation_id: str):
        """Clear the conversation history for a given conversation ID."""
        if conversation_id in self.history:
            del self.history[conversation_id]

    def get_summary(self, conversation_id: str) -> str:
        """Retrieve the summary for a given conversation ID."""
        conversation = self.history.get(conversation_id, None)
        if conversation is None:
            logger.info(f"No conversation history found for {conversation_id}. Returning empty summary.")
            return ""
        return conversation.summary

    def set_summary(self, conversation_id: str, summary: str):
        """Set the summary for a given conversation ID."""
        if conversation_id in self.history:
            self.history[conversation_id].summary = summary
        else:
            self.history[conversation_id] = ConversationState(summary=summary, messages=[])

    