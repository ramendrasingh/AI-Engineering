from app.config.config import SYSTEM_PROMPT, MAX_TOKEN_COUNT, OUTPUT_RESERVE_TOKENS, SUMMARY_TRIGGER_MESSAGES, SUMMARY_RETAIN_MESSAGES
from app.exception.custom_exception import ContextWindowExceededError
from app.logger.logger import logger
from app.tokenizer.token_counter import TokenCounter
from app.summary.conversation_summary import SummaryManager
from app.models.schemas import ChatMessage
import json


class Orchastrator:
    def __init__(self, llm_client, memory):
        self.llm_client = llm_client
        self.memory = memory
        self.token_counter = TokenCounter()
        self.summary_manager = SummaryManager(llm_client)

    def process_message(self, conversation_id: str, role: str, content: str) -> str:

        # 1. Retrieve the conversation history for context
        conversation_history = self.memory.get_conversation(conversation_id)

        new_summary = ""
        latest_message = []
        if len(conversation_history) >= SUMMARY_TRIGGER_MESSAGES:
            new_summary = self.__get_message_summary(conversation_id, conversation_history)
            latest_message = conversation_history[SUMMARY_RETAIN_MESSAGES: ]
        else:
            latest_message = conversation_history

        available_budget = MAX_TOKEN_COUNT - OUTPUT_RESERVE_TOKENS

        # Always include system prompt
        system_prompt = f"{SYSTEM_PROMPT.strip()} Conversation Summary\n {new_summary}"

        system_message = ChatMessage(role = "system", content=system_prompt)
        system_tokens = self.token_counter.count_message(system_message)

        if system_tokens >= available_budget:
            raise ContextWindowExceededError()

        current_message = ChatMessage(role= role, content=content)
        current_tokens = self.token_counter.count_message(current_message)

        if system_tokens + current_tokens > available_budget:
            raise ContextWindowExceededError()

        # Remaining budget for history
        remaining_budget = available_budget - system_tokens - current_tokens

        allowable_history = []

        # Walk backward through history
        for message in reversed(latest_message):
            message_tokens = self.token_counter.count_message(message= message)
            if message_tokens <= remaining_budget:
                allowable_history.append(message)
                remaining_budget -= message_tokens
            else:
                break

        allowable_history.reverse() # Reverse to maintain the original order    

        #2. Assemble the conversation history into a single prompt for the LLM
        messages = [system_message]
        messages.extend(allowable_history)
        messages.append(current_message)

        estimated_tokens = self.token_counter.count_messages(messages)
        final_messages = [chat.model_dump() for chat in messages]
        logger.info(
            f"conversation_id={conversation_id} \n"
            f"budget={available_budget} \n"
            f"estimated={estimated_tokens} \n"
            f"history={len(conversation_history)} \n"
            f"selected={len(allowable_history)} \n"
            f"dropped={len(conversation_history) - len(allowable_history)}"
        )

        # 3. Generate a response using the LLM client with the assembled prompt
        response = self.llm_client.chat(messages=final_messages)

        # 4. Store the generated response in memory
        self.memory.add_message(conversation_id, role, content)
        self.memory.add_message(conversation_id, response.role, response.content)

        return response.content


    def __get_message_summary(self, conversation_id, conversation_history)-> str :
        older_conversation = conversation_history[0: SUMMARY_RETAIN_MESSAGES]
        latest_conversation = conversation_history[SUMMARY_RETAIN_MESSAGES:]
        
        existing_summary = self.memory.get_summary(conversation_id)
        new_summary = self.summary_manager.summarize_messages(old_summary= existing_summary, messages= older_conversation)
        self.memory.set_summary(conversation_id, new_summary)
        self.memory.replace_messages(conversation_id, latest_conversation)
        logger.info(f"New Conversation for {conversation_id}: {latest_conversation}")
        return new_summary, latest_conversation
  
