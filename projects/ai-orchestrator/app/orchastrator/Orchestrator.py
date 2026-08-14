from app.config.config import settings
from app.exception.custom_exception import ContextWindowExceededError
from app.logger.logger import logger
from app.models.schemas import ChatMessage, ToolCall
from app.rag.chunker import Chunk
from app.summary.conversation_summary import SummaryManager
from app.tokenizer.token_counter import TokenCounter


class Orchastrator:
    def __init__(self, llm_client, memory, retriever, tool_registory):
        self.llm_client = llm_client
        self.memory = memory
        self.token_counter = TokenCounter()
        self.summary_manager = SummaryManager(llm_client)
        self.retriever = retriever
        self.tool_registry = tool_registory

    def process_message(self, conversation_id: str, role: str, content: str) -> str:

        # 1. Retrieve the conversation history for context
        conversation_history = self.memory.get_conversation(conversation_id)

        # check for tool uses
        decision = self.__should_use_tool(content)

        chunks = []
        tool_chat: str | None = None
        if decision.tool is not None:
            logger.info("Tool path")
            tool_chat = self.execute_tool(decision)
        else:
            logger.info("RAG path")
            chunks = self.retriever.retrieve(
                query=content,
                top_k=settings.RAG_TOP_K,
                min_threshold=settings.RAG_MIN_SIMILARITY,
            )

        formatted_chunks = self.__format_chunks(chunks)

        chunks_token = self.token_counter.count_text(formatted_chunks)

        new_summary = ""
        latest_message = []
        if len(conversation_history) >= settings.SUMMARY_TRIGGER_MESSAGES:
            new_summary = self.__get_message_summary(
                conversation_id, conversation_history
            )
            latest_message = conversation_history[settings.SUMMARY_RETAIN_MESSAGES :]
        else:
            latest_message = conversation_history

        available_budget = settings.MAX_TOKEN_COUNT - settings.OUTPUT_RESERVE_TOKENS

        summary_token = self.token_counter.count_text(new_summary)

        # Always include system prompt
        if chunks:
            system_prompt = f"{settings.SYSTEM_PROMPT.strip()} Retrieved Context\n {formatted_chunks}\nConversation Summary\n {new_summary}"
        else:
            system_prompt = f"{settings.SYSTEM_PROMPT.strip()}\nConversation Summary\n {new_summary}"

        system_message = ChatMessage(role="system", content=system_prompt)
        system_tokens = self.token_counter.count_text(settings.SYSTEM_PROMPT)

        if system_tokens >= available_budget:
            raise ContextWindowExceededError()

        current_message = ChatMessage(role=role, content=content)
        current_tokens = self.token_counter.count_message(current_message)

        if system_tokens + current_tokens > available_budget:
            raise ContextWindowExceededError()

        # Remaining budget for history
        remaining_budget = available_budget - system_tokens - current_tokens

        allowable_history = []

        # Walk backward through history
        for message in reversed(latest_message):
            message_tokens = self.token_counter.count_message(message=message)
            if message_tokens <= remaining_budget:
                allowable_history.append(message)
                remaining_budget -= message_tokens
            else:
                break

        allowable_history.reverse()  # Reverse to maintain the original order

        # 2. Assemble the conversation history into a single prompt for the LLM
        messages = [system_message]
        if tool_chat is not None:
            messages.append(tool_chat)
        messages.extend(allowable_history)
        messages.append(current_message)

        estimated_tokens = (
            self.token_counter.count_messages(messages)
            + chunks_token
            + summary_token
            + current_tokens
            + system_tokens
        )
        final_messages = [chat.model_dump() for chat in messages]
        logger.info(
            f"conversation_id={conversation_id} \n"
            f"budget={available_budget} \n"
            f"estimated={estimated_tokens} \n"
            f"retrived chunks={len(chunks)} \n"
            f"retrival token={chunks_token} \n"
            f"summary token={summary_token} \n"
            f"history messages={len(conversation_history)} \n"
            f"selected={len(allowable_history)} \n"
            f"dropped={len(conversation_history) - len(allowable_history)}"
        )

        logger.info(f"final messgae : {final_messages}")

        # 3. Generate a response using the LLM client with the assembled prompt
        response = self.llm_client.chat(messages=final_messages)

        # 4. Store the generated response in memory
        self.memory.add_message(conversation_id, role, content)
        self.memory.add_message(conversation_id, response.role, response.content)

        return response.content

    def __get_message_summary(self, conversation_id, conversation_history) -> str:
        older_conversation = conversation_history[0 : settings.SUMMARY_RETAIN_MESSAGES]
        latest_conversation = conversation_history[settings.SUMMARY_RETAIN_MESSAGES :]

        existing_summary = self.memory.get_summary(conversation_id)
        new_summary = self.summary_manager.summarize_messages(
            old_summary=existing_summary, messages=older_conversation
        )
        self.memory.set_summary(conversation_id, new_summary)
        self.memory.replace_messages(conversation_id, latest_conversation)
        logger.info(f"New Conversation for {conversation_id}: {latest_conversation}")
        return new_summary, latest_conversation

    def __format_chunks(self, chunks: list[Chunk]) -> str:
        if not chunks:
            return ""
        formatted_chunks = "\n".join(
            [f"[source: {chunk.chunk_id}]\n{chunk.page_content}\n" for chunk in chunks]
        )
        return formatted_chunks

    def __should_use_tool(self, content: str) -> ToolCall:
        prompt = f"{settings.TOOL_SELECTION_PROMPT}\n{content}"
        response = self.llm_client.generate(prompt)
        decision = ToolCall.model_validate_json(response)
        return decision

    def execute_tool(self, tool_call: ToolCall) -> ChatMessage:
        tool = self.tool_registry.get_tool(tool_call.tool)
        tool_result = tool.execute(**tool_call.arguments)
        content = f"Tool executed: {tool_call.tool}\nArguments: {tool_call.arguments}\n\nTool result:\n{tool_result.content}"

        return ChatMessage(role="system", content=content)
