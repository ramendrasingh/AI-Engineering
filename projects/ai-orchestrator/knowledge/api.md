# AI Orchestrator API

## Base URL

The service is exposed through FastAPI and is typically available at:

```text
http://localhost:8000
```

## Endpoints

### Health Check

Method:

```text
GET /health
```

Purpose:

Returns the health status of the service and verifies that the Ollama server is reachable.

Example response:

```json
{
  "status": "healthy",
  "model": "gemma3:4b"
}
```

### Generate

Method:

```text
POST /generate
```

Purpose:

Generates a text completion from a prompt.

Example request:

```json
{
  "prompt": "Explain what an API is."
}
```

Example response:

```json
{
  "response": "An API is..."
}
```

### Chat

Method:

```text
POST /chat
```

Purpose:

Processes a conversational request using conversation memory, summaries, and token-aware context management.

Example request:

```json
{
  "user_id": "abc",
  "prompt": "What is my name?"
}
```

Example response:

```json
{
  "response": "Your name is Ram."
}
```

## Chat Processing Flow

1. Retrieve conversation state.
2. Retrieve summary.
3. Retrieve recent messages.
4. Trigger summarization if required.
5. Build the final message context.
6. Apply token budgeting.
7. Call the Ollama chat endpoint.
8. Store the assistant response.
9. Return the generated response.

## Context Structure

The final context sent to the language model contains:

- system prompt,
- conversation summary,
- recent chat messages,
- and the current user message.

This structure enables long-running conversations while remaining within the model context window.

## Error Handling

The service may return errors for:

- invalid requests,
- context window overflow,
- Ollama connectivity failures,
- and internal processing errors.