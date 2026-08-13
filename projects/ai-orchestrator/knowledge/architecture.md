# AI Orchestrator Architecture

## High-Level Architecture

The system is organized into multiple layers.

```text
Client
  ↓
FastAPI Router
  ↓
Orchestrator
  ├── Conversation Memory
  ├── Token Counter
  ├── Summary Manager
  └── LLM Client
        ↓
      Ollama
        ↓
      Gemma
```

## Router Layer

The router receives HTTP requests and converts them into internal requests for the orchestrator. It is responsible for request validation, response formatting, and HTTP error handling.

## Orchestrator Layer

The orchestrator is the core of the system. It coordinates:

- memory retrieval,
- summary retrieval,
- token budgeting,
- context construction,
- summarization triggers,
- and LLM invocation.

The orchestrator does not perform HTTP-specific logic.

## Conversation Memory

Conversation memory stores conversation state for each conversation ID.

Each conversation contains:

- a summary,
- and a list of recent chat messages.

## Summary Manager

The summary manager compresses older messages into a compact summary.

The summary preserves:

- user goals,
- important decisions,
- technical constraints,
- project status,
- unresolved questions,
- and long-term context.

## Token Counter

The token counter estimates token usage for:

- system prompts,
- summaries,
- chat messages,
- and complete message lists.

Token budgeting ensures that requests stay within the model context window.

## LLM Client

The LLM client abstracts communication with Ollama.

Supported operations:

- text generation,
- chat completion,
- health checking,
- and future embedding generation.

## Future Architecture

Planned additions:

- document loader,
- text chunker,
- embedding service,
- vector store,
- retriever,
- and RAG context builder.

These components will allow the orchestrator to retrieve external knowledge before generating responses.