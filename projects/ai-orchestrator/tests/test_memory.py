from app.memory.conversational import ConversationalMemory


def test_memory_history():
    memory = ConversationalMemory()
    conversation_id = "test_conversation"
    memory.add_message(conversation_id, "user", "Hello")
    memory.add_message(conversation_id, "assistant", "Hi there!")

    history = memory.get_conversation(conversation_id)
    expected_history = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"},
    ]
    assert history == expected_history


def test_multiple_memory_history():
    memory = ConversationalMemory()
    conversation_id = "test_conversation"
    memory.add_message(conversation_id, "user", "Hello")
    memory.add_message(conversation_id, "assistant", "Hi there!")

    conversation_id1 = "test_conversation1"
    memory.add_message(conversation_id1, "user", "Hello Ram")
    memory.add_message(conversation_id1, "assistant", "Hi there Ram!")

    history = memory.get_conversation(conversation_id1)
    expected_history = [
        {"role": "user", "content": "Hello Ram"},
        {"role": "assistant", "content": "Hi there Ram!"},
    ]

    assert history == expected_history


def test_clear_memory_history():
    memory = ConversationalMemory()
    conversation_id = "test_conversation"
    memory.add_message(conversation_id, "user", "Hello")
    memory.add_message(conversation_id, "assistant", "Hi there!")

    # Clear the conversation history
    memory.clear_history(conversation_id)

    # Verify that the history is empty
    history = memory.get_conversation(conversation_id)
    assert history == []


def test_recent_history():
    memory = ConversationalMemory()
    conversation_id = "test_conversation"

    # Add more than MAX_HISTORY_MESSAGES messages
    for i in range(15):
        memory.add_message(conversation_id, "user", f"Message {i}")

    recent_history = memory.get_recent_history(conversation_id)

    # Verify that only the last MAX_HISTORY_MESSAGES messages are returned
    assert len(recent_history) == 10
    assert recent_history[0]["content"] == "Message 5"
    assert recent_history[-1]["content"] == "Message 14"
