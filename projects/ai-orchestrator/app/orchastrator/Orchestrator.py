from app.config.config import SYSTEM_PROMPT, MAX_TOKEN_COUNT, OUTPUT_RESERVE_TOKENS
from app.exception.custom_exception import ContextWindowExceededError
from app.logger.logger import logger
from app.tokenizer.token_counter import TokenCounter


class Orchastrator:
    def __init__(self, llm_client, memory):
        self.llm_client = llm_client
        self.memory = memory
        self.token_counter = TokenCounter()

    def process_message(self, conversation_id: str, role: str, content: str) -> str:

        # 1. Retrieve the conversation history for context
        conversation_history = self.memory.get_conversation(conversation_id)

        logger.info(f"Conversation history for {conversation_id}: {conversation_history}")
        available_budget = MAX_TOKEN_COUNT - OUTPUT_RESERVE_TOKENS

        # Always include system prompt

        system_message = {"role": "system","content": SYSTEM_PROMPT.strip()}
        system_tokens = self.token_counter.count_message(system_message)

        if system_tokens >= available_budget:
            raise ContextWindowExceededError()

        current_message = {"role": role, "content": content.strip()}
        current_tokens = self.token_counter.count_message(current_message)

        if system_tokens + current_tokens > available_budget:
            raise ContextWindowExceededError()

        # Remaining budget for history
        remaining_budget = available_budget - system_tokens - current_tokens

        allowable_history = []

        # Walk backward through history

        for message in reversed(conversation_history):
            message_tokens = self.token_counter.count_message(message)
            if message_tokens <= remaining_budget:
                allowable_history.append(message)
                remaining_budget -= message_tokens
            else:
                break

        allowable_history.reverse()  # Reverse to maintain the original order    

        #2. Assemble the conversation history into a single prompt for the LLM
        messages = [system_message]
        messages.extend(allowable_history)
        messages.append(current_message)

        estimated_tokens = self.token_counter.count_messages(messages)

        logger.info(
            f"conversation_id={conversation_id} \n"
            f"budget={available_budget} \n"
            f"estimated={estimated_tokens} \n"
            f"history={len(conversation_history)} \n"
            f"selected={len(allowable_history)} \n"
            f"dropped={len(conversation_history) - len(allowable_history)}"
        )

        # 3. Generate a response using the LLM client with the assembled prompt
        response = self.llm_client.chat(messages=messages)

        # 4. Store the generated response in memory
        self.memory.add_message(conversation_id, role, content)
        self.memory.add_message(conversation_id, response.role, response.content)

        return response.content