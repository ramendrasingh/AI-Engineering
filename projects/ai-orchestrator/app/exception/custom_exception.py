
class ContextWindowExceededError(Exception):
    """Custom exception raised when the context window is exceeded."""

    def __init__(self, message="Context window exceeded the maximum token limit."):
        self.message = message
        super().__init__(self.message)