import tiktoken

from app.models.schemas import ChatMessage


class TokenCounter:
    MESSAGE_OVERHEAD = 4

    def __init__(self):
        self.encoding = tiktoken.get_encoding("cl100k_base")

    def count_text(self, text: str) -> int:
        if not text:
            return 0
        return len(self.encoding.encode(text))

    def count_message(self, message: ChatMessage) -> int:
        return (
            self.count_text(message.role)
            + self.count_text(message.content)
            + self.MESSAGE_OVERHEAD
        )

    def count_messages(self, messages: list[ChatMessage]) -> int:
        return sum(self.count_message(m) for m in messages)
