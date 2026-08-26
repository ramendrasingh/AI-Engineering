# AI Orchestrator

Production-oriented LLM orchestration service built using FastAPI,
Ollama and local LLM/embedding models.

## Architecture

Request
  ↓
Router
  ↓
Memory
  ↓
Retriever
  ↓
LLM
  ↓
Tool
  ↓
LLM
  ↓
Response

## Features

- LLM interaction
- Conversation memory
- Context-window management
- RAG
- Local embeddings
- In-memory vector store
- Tool execution
- Tool registry
- Conversation summarization
- FastAPI REST API
- Docker deployment
- Docker Compose

## Technology Stack

- Python 3.12
- FastAPI
- Pydantic
- Ollama
- Gemma 3 4B
- nomic-embed-text
- Docker
- Docker Compose

## Architecture Components

### LLM

Ollama provides the local inference server.

Default model:

gemma3:4b

### Embeddings

nomic-embed-text

### RAG

Documents are stored under:

knowledge/

The current implementation:

Document
  ↓
Loader
  ↓
Chunker
  ↓
Embedding
  ↓
In-memory Vector Store
  ↓
Retriever

### Memory

Conversation memory is currently maintained in application memory.

### Tools

Available tools:

- search_files
- read_file
- list_directory

## Prerequisites

Install:

- Docker Desktop
- Ollama

Pull models:

```bash
ollama pull gemma3:4b
ollama pull nomic-embed-text
