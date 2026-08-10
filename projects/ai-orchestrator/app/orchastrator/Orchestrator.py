
from click import prompt

from app.core.config import SYSTEM_PROMPT
from app.logger.logger import logger


class Orchastrator:
    def __init__(self, llm_client, memory):
        self.llm_client = llm_client
        self.memory = memory

    def process_message(self, conversation_id: str, role: str, content: str) -> str:

        # 1. Retrieve the conversation history for context
        conversation_history = self.memory.get_conversation(conversation_id)

        logger.info(f"Conversation history for {conversation_id}: {conversation_history}")

        #2. Assemble the conversation history into a single prompt for the LLM
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(conversation_history)
        messages.append({"role": role, "content": content})

        logger.info(f"Message: {messages}")

        # 3. Generate a response using the LLM client with the assembled prompt
        response = self.llm_client.chat(messages=messages)

        # 4. Store the generated response in memory
        self.memory.add_message(conversation_id, role, content)
        self.memory.add_message(conversation_id, "assistant", response)

        return response