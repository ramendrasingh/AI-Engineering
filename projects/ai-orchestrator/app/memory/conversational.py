import json

class ConversationalMemory:
    def __init__(self):
        self.history = dict()

    def add_message(self, conversation_id: str, role: str, content: str):
        """Add a message to the conversation history for a given conversation ID."""
        if conversation_id not in self.history:
            self.history[conversation_id] = [json.dumps({"role": role, "content": content})]
        else:
            self.history[conversation_id].append(json.dumps({"role": role, "content": content}))


    def get_conversation(self, conversation_id: str):
        """Retrieve the conversation history for a given conversation ID."""
        conversation = self.history.get(conversation_id, [])
        converted_history = []
        if conversation and len(conversation) > 0:
            converted_history = [f"{item['role']}: {item['content']}" for item in map(json.loads, conversation)]
        return converted_history

    def clear_history(self, conversation_id: str):
        """Clear the conversation history for a given conversation ID."""
        if conversation_id in self.history:
            del self.history[conversation_id]

    