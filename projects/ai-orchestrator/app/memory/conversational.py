import json
from app.config.config import MAX_HISTORY_MESSAGES
from app.logger.logger import logger

class ConversationalMemory:
    def __init__(self):
        self.history = dict()

    def add_message(self, conversation_id: str, role: str, content: str):
        """Add a message to the conversation history for a given conversation ID."""
        message = {"role": role, "content": content}
        if conversation_id not in self.history:
            self.history[conversation_id] = [message]
        else:
            self.history[conversation_id].append(message)


    def get_conversation(self, conversation_id: str):
        """Retrieve the conversation history for a given conversation ID."""
        conversation = self.history.get(conversation_id, [])
        converted_history = []
        if conversation and len(conversation) > 0:
            logger.info(f"Conversation history for {conversation_id}: {conversation}")
            converted_history = conversation
        return converted_history

    def clear_history(self, conversation_id: str):
        """Clear the conversation history for a given conversation ID."""
        if conversation_id in self.history:
            del self.history[conversation_id]


    def get_recent_history(self, conversation_id: str):
        """Retrieve the most recent messages for a given conversation ID, limited to a certain number of messages."""
        conversation = self.history.get(conversation_id, [])
        logger.info(f"Total conversation history for {conversation_id}: {len(conversation)}, sliding window size: {MAX_HISTORY_MESSAGES}")
        if len(conversation) > MAX_HISTORY_MESSAGES:
            return conversation[-MAX_HISTORY_MESSAGES:]
        return conversation

    