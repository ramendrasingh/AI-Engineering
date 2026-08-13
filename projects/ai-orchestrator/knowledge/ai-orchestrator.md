# AI Orchestrator Project

## Overview

The AI Orchestrator project is a production-oriented AI backend service built using FastAPI and Ollama. The goal of the project is to provide a unified orchestration layer that manages conversations, context windows, summaries, and future integrations such as Retrieval-Augmented Generation (RAG), tool calling, and multi-provider LLM support.

The orchestrator acts as the central coordinator between the API layer, memory layer, token management, and the language model.

## Current Capabilities

- FastAPI HTTP service
- Ollama integration
- Local Gemma model support
- Conversation memory
- Conversation isolation using conversation IDs
- Structured chat messages
- System prompt injection
- Token-aware context management
- Sliding context windows
- Automatic conversation summarization
- Incremental summary updates
- Logging and health checks
- Unit testing for memory and orchestration components

## Technology Stack

- Python
- FastAPI
- Ollama
- Gemma language model
- Pydantic
- Requests
- tiktoken
- pytest

## Project Goals

The long-term goal of the project is to become a production-ready AI orchestration platform capable of:

- managing long-running conversations,
- retrieving external knowledge,
- switching between multiple LLM providers,
- exposing scalable APIs,
- supporting enterprise AI workflows,
- and being deployed using Docker and cloud infrastructure.

## Design Principles

- Clear separation of concerns
- Provider-agnostic LLM abstraction
- Token-aware context management
- Memory compression through summarization
- Testable and modular architecture
- Incremental extensibility