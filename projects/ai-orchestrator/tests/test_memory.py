from app.memory.conversational import ConversationalMemory
import json

def test_memory_history():
    memory = ConversationalMemory()
    conversation_id = "test_conversation"
    memory.add_message(conversation_id, "user", "Hello")
    memory.add_message(conversation_id, "assistant", "Hi there!")

    history = memory.get_conversation(conversation_id)
    expected_history = [
        json.dumps({"role": "user", "content": "Hello"}),
        json.dumps({"role": "assistant", "content": "Hi there!"})
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
        json.dumps({"role": "user", "content": "Hello Ram"}),
        json.dumps({"role": "assistant", "content": "Hi there Ram!"})
    ]

    assert history == expected_history