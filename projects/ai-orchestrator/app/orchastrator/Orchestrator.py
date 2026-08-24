from app.config.config import settings
from app.exception.custom_exception import ContextWindowExceededError
from app.logger.logger import logger
from app.models.schemas import ChatMessage, ConversationContext, ToolCall
from app.rag.chunker import Chunk
from app.summary.conversation_summary import SummaryManager
from app.tokenizer.token_counter import TokenCounter
from app.tool.registry import ToolRegistry


class Orchestrator:
    def __init__(
        self,
        llm_client,
        memory,
        retriever,
        tool_registory: ToolRegistry,
        token_counter: TokenCounter,
        summary_manager: SummaryManager,
    ):
        self.llm_client = llm_client
        self.memory = memory
        self.token_counter = token_counter
        self.summary_manager = summary_manager
        self.retriever = retriever
        self.tool_registry = tool_registory

    def process_message(self, conversation_id: str, role: str, content: str) -> str:

        # 1. Retrieve the conversation history for context
        conversation_context = self.__prepare_conversation_context(
            conversation_id=conversation_id, role=role, content=content
        )

        # check for tool uses
        decision = self.__procees_with_tool(content)

        final_messages = []
        if decision.tool is not None:
            final_messages = self.__build_tool_context(
                context=conversation_context,
                decision=decision,
            )
        else:
            final_messages = self.__build_rag_context(context=conversation_context)

        logger.info(f"final messgae : {final_messages}")

        # 3. Generate a response using the LLM client with the assembled prompt
        response = self.llm_client.chat(messages=final_messages)

        # 4. Store the generated response in memory
        self.memory.add_message(conversation_id, role, content)
        self.memory.add_message(conversation_id, response.role, response.content)

        return response.content

    def __get_message_summary(
        self, conversation_id, conversation_history
    ) -> tuple[str, list[ChatMessage]]:
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

    def __format_message(self, messages: list[ChatMessage]) -> str:
        if not messages:
            return ""
        conversation = "\n\n".join(
            f"ROLE: {message.role}\nCONTENT:\n{message.content}" for message in messages
        )
        return conversation

    def __should_use_tool(self, user_message: list[ChatMessage]) -> ToolCall:
        convesation = self.__format_message(user_message)
        prompt = f"{settings.TOOL_SELECTION_PROMPT} conversation: \n{convesation} \n Decide the NEXT action."
        response = self.llm_client.generate(prompt, True)
        logger.info(f"Raw response form LLM for tool :  {response}")
        response = response.replace("```json", "").replace("```", "").strip()
        decision = ToolCall.model_validate_json(response)
        return decision

    def __procees_with_tool(self, content: str) -> ToolCall:
        prompt = f"{settings.TOOL_SELECTION_PROMPT}\n{content}"
        response = self.llm_client.generate(prompt, True)
        logger.info(f"Raw response form LLM for tool :  {response}")
        response = response.replace("```json", "").replace("```", "").strip()
        decision = ToolCall.model_validate_json(response)
        return decision

    def execute_tool(self, tool_call: ToolCall) -> ChatMessage:
        tool = self.tool_registry.get_tool(tool_call.tool)
        tool_result = tool.execute(**tool_call.arguments)
        content = f"Tool executed: {tool_call.tool}\nArguments: {tool_call.arguments}\n\nTool result:\n{tool_result.content}"

        return ChatMessage(role="system", content=content)

    def __build_tool_context(
        self,
        context: ConversationContext,
        decision: ToolCall,
    ) -> list[dict]:
        logger.info("Tool path")

        system_content = (
            f"{settings.SYSTEM_PROMPT.strip()}\n\n"
            f"Conversation Summary:\n"
            f"{context.summary}"
        )

        messages = self.__build_common_context(
            context=context, system_content=system_content
        )

        messages = self.__run_tool_loop(
            messages=messages,
            initial_decision=decision,
        )

        estimated_tokens = self.token_counter.count_messages(messages)

        logger.info(
            f"conversation_id={context.conversation_id}\n"
            f"path=TOOLS\n"
            f"tool_messages={len(messages)}\n"
            f"estimated_tokens={estimated_tokens}\n"
            f"history_messages="
            f"{len(context.latest_messages)}"
        )

        return [message.model_dump() for message in messages]

    def __build_rag_context(self, context: ConversationContext) -> list[dict]:

        logger.info("RAG path")

        chunks = self.retriever.retrieve(
            query=context.user_message,
            top_k=settings.RAG_TOP_K,
            min_threshold=settings.RAG_MIN_SIMILARITY,
        )

        formatted_chunks = self.__format_chunks(chunks)

        system_content = (
            f"{settings.SYSTEM_PROMPT.strip()}\n\n"
            f"Retrieved Context:\n"
            f"{formatted_chunks}\n\n"
            f"Conversation Summary:\n"
            f"{context.summary}"
        )

        messages = self.__build_common_context(
            context=context, system_content=system_content
        )

        estimated_tokens = self.token_counter.count_messages(messages)

        logger.info(
            f"conversation_id={context.conversation_id}\n"
            f"path=RAG\n"
            f"retrieved_chunks={len(chunks)}\n"
            f"retrieval_tokens={formatted_chunks}\n"
            f"summary_tokens="
            f"{self.token_counter.count_text(context.summary)}\n"
            f"estimated_tokens={estimated_tokens}\n"
            f"history_messages="
            f"{len(context.latest_messages)}"
        )

        return [message.model_dump() for message in messages]

    def __build_common_context(
        self,
        context: ConversationContext,
        system_content: str,
    ) -> list[ChatMessage]:
        available_budget = self.__calculate_available_budget()

        system_message = ChatMessage(role="system", content=system_content)
        system_tokens = self.token_counter.count_text(settings.SUMMARY_PROMPT)
        if system_tokens >= available_budget:
            raise ContextWindowExceededError()

        current_message = ChatMessage(role=context.role, content=context.user_message)
        current_tokens = self.token_counter.count_message(current_message)

        if system_tokens + current_tokens > available_budget:
            raise ContextWindowExceededError()

        # Remaining budget for history
        remaining_budget = available_budget - system_tokens - current_tokens

        allowable_history = self.__select_history(
            context.latest_messages,
            remaining_budget,
        )

        # 2. Assemble the conversation history into a single prompt for the LLM
        messages = [system_message]
        messages.extend(allowable_history)
        messages.append(current_message)

        return messages

    def __prepare_conversation_context(
        self,
        conversation_id: str,
        role: str,
        content: str,
    ) -> ConversationContext:

        conversation_history = self.memory.get_conversation(conversation_id)

        new_summary = ""

        if len(conversation_history) >= settings.SUMMARY_TRIGGER_MESSAGES:
            new_summary, latest_messages = self.__get_message_summary(
                conversation_id,
                conversation_history,
            )
        else:
            latest_messages = conversation_history

        current_message = ChatMessage(role=role, content=content)

        system_message = ChatMessage(
            role="system", content=settings.SYSTEM_PROMPT.strip()
        )

        return ConversationContext(
            conversation_id=conversation_id,
            role=role,
            user_message=content,
            conversation_history=conversation_history,
            latest_messages=latest_messages,
            summary=new_summary,
            system_message=system_message,
            current_message=current_message,
        )

    def __select_history(
        self,
        latest_messages: list[ChatMessage],
        available_budget: int,
    ) -> list[ChatMessage]:
        allowable_history = []

        remaining_budget = available_budget

        for message in reversed(latest_messages):
            message_tokens = self.token_counter.count_message(message)

            if message_tokens <= remaining_budget:
                allowable_history.append(message)
                remaining_budget -= message_tokens
            else:
                break

        allowable_history.reverse()

        return allowable_history

    def __run_tool_loop(
        self,
        messages: list[ChatMessage],
        initial_decision: ToolCall,
    ) -> list[ChatMessage]:

        logger.info("Starting tool execution loop")

        decision = initial_decision

        max_steps = settings.MAX_TOOL_STEPS

        for step in range(max_steps):
            logger.info(f"Tool step {step + 1}/{max_steps}")

            tool_result = self.execute_tool(decision)

            messages.append(tool_result)

            self.__validate_context_budget(messages)

            decision = self.__should_use_tool(messages)

            if decision.tool is None:
                logger.info("Tool execution completed")
                break

        if step > max_steps:
            raise RuntimeError("Maximum tool steps exceeded")

        return messages

    def __calculate_available_budget(self) -> int:
        return settings.MAX_TOKEN_COUNT - settings.OUTPUT_RESERVE_TOKENS

    def __validate_context_budget(self, messages: list[ChatMessage]) -> None:
        available_budget = self.__calculate_available_budget()

        estimated_tokens = self.token_counter.count_messages(messages)

        if estimated_tokens > available_budget:
            raise ContextWindowExceededError()
