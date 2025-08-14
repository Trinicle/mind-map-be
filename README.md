# Mind Map Backend

A powerful backend application for parsing, analyzing, and querying meeting transcripts using AI-powered agents. The system automatically extracts topics, participants, and generates follow-up questions from uploaded transcripts, while providing an intelligent chatbot for querying the content.

## Features

### Core Functionality
- **Transcript Processing**: Upload and process meeting transcripts (DOCX format) using advanced NLP
- **Intelligent Analysis**: AI-powered extraction of topics, participants, and key discussion points
- **Question Generation**: Automatic creation of relevant follow-up questions based on transcript content
- **Smart Chatbot**: RAG (Retrieval Augmented Generation) chatbot for querying transcript content
- **Mind Map Organization**: Visual organization of topics and their interconnections
- **Conversation Management**: Persistent chat sessions with context-aware responses

### Technical Features
- **LangGraph Workflow**: Advanced AI agent workflow for transcript processing
- **Vector Search**: Semantic search through transcript content using embeddings
- **Real-time Chat**: WebSocket-like chat experience with conversation persistence
- **User Authentication**: Secure user management via Supabase Auth
- **Database Integration**: PostgreSQL with vector extensions via Supabase
- **Caching Layer**: Redis for conversation history and performance optimization

## Technology Stack

- **Backend Framework**: Flask (Python)
- **AI/ML**: 
  - OpenAI GPT-4o-mini for language processing
  - LangChain & LangGraph for AI agent workflows
  - OpenAI Embeddings for semantic search
- **Database**: Supabase (PostgreSQL with vector extensions)
- **Caching**: Redis for chat history and session management
- **Document Processing**: Unstructured library for DOCX parsing
- **Authentication**: Supabase Auth with JWT tokens
- **Deployment**: Docker support

## Prerequisites

- Python 3.8+
- Docker & Docker Compose
- OpenAI API key
- Supabase project with database
- Redis instance

## Environment Setup

Create a `.env` file in the root directory with the following variables:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# Supabase Configuration
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key

# Database Configuration
DATABASE_URL=postgresql://user:password@host:port/database

# Redis Configuration (for Docker)
REDIS_URL=redis://localhost:6379

# Optional: Tavily API for web search
TAVILY_API_KEY=your_tavily_api_key
```

## Quick Start

### 1. Start Redis (using Docker)
```bash
docker run -d --name redis -p 6379:6379 redis:latest
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Application
```bash
python -m main
```

The API will be available at `http://localhost:5000`

## 📊 Database Schema

The application uses the following main tables in Supabase:

- **MindMap**: Stores transcript metadata and processing results
- **Transcript**: Raw transcript text storage
- **Topic**: Extracted topics with connections
- **Content**: Individual content segments linked to topics
- **Question**: Generated follow-up questions
- **Conversation**: Chat session management
- **Tag**: Categorization tags for mind maps
- **Transcript_Vector**: Vector embeddings for semantic search

## AI Processing Workflow

The transcript processing follows this LangGraph workflow:

```
Upload → Load → Clean → Quality Check → Split → [Participants, Topics, Questions] → Store
```

1. **Load Transcript**: Parse DOCX files using Unstructured
2. **Clean Transcript**: Remove formatting and normalize text
3. **Quality Check**: Validate transcript quality and retry if needed
4. **Split Transcript**: Chunk text for processing
5. **Parallel Processing**:
   - Extract participants and roles
   - Identify topics and connections
   - Generate relevant follow-up questions

## API Endpoints

### Authentication
- `POST /auth/signup` - User registration
- `POST /auth/signin` - User login
- `POST /auth/signout` - User logout
- `POST /auth/refresh` - Refresh session token

### Mind Map Management
- `GET /dashboard/mindmap` - List user's mind maps
- `GET /dashboard/mindmap/search` - Search mind maps by filters
- `POST /dashboard/mindmap` - Create new mind map from transcript
- `GET /dashboard/mindmap/{id}` - Get mind map details
- `GET /dashboard/mindmap/tags` - Get available tags

### Content Access
- `GET /mindmap/{id}/topics` - Get topics for a mind map
- `GET /mindmap/{id}/questions` - Get follow-up questions
- `GET /mindmap/{id}/transcript` - Get original transcript
- `GET /topic/{id}` - Get topic details with content

### Chat & Conversations
- `POST /conversations` - Create new conversation
- `GET /conversations` - List user conversations
- `GET /conversations/{id}` - Get conversation history
- `POST /chat` - Send message to chatbot

## Chatbot Features

The RAG-powered chatbot provides:

- **Context-Aware Responses**: Uses conversation history and transcript context
- **Semantic Search**: Finds relevant transcript segments using vector similarity
- **Tool Integration**: Access to web search and other external tools
- **Conversation Persistence**: Maintains chat history across sessions
- **Filtered History**: Clean conversation flow excluding system messages

## Key Components

### Agent System (`src/agent/`)
- **Graph**: LangGraph workflow definition for transcript processing
- **Nodes**: Individual processing steps (load, clean, analyze, etc.)
- **Chatbot**: RAG agent implementation with tool integration
- **State**: Pydantic models for workflow state management

### Flask Application (`src/flask/`)
- **Main**: Flask app with all API endpoints
- **Models**: Pydantic models for API request/response
- **Supabase**: Database integration layer with CRUD operations

### Database Layer
- **Connection Management**: PostgreSQL and Redis connection handling
- **Vector Store**: Semantic search implementation using PGVector
- **Authentication**: Supabase Auth integration

## Development

### Project Structure
```
mind-map-be/
├── src/
│   ├── agent/          # AI agent components
│   │   ├── chatbot.py  # RAG chatbot implementation
│   │   ├── graph.py    # LangGraph workflow
│   │   ├── nodes.py    # Processing nodes
│   │   └── state.py    # State management
│   └── flask/          # Web application
│       ├── main.py     # Flask app and routes
│       ├── models/     # Pydantic models
│       └── supabase/   # Database layer
├── main.py             # Application entry point
└── requirements.txt    # Python dependencies
```

### Running in Development
```bash
# Install dependencies
pip install -r requirements.txt

# Start Redis
docker run -d --name redis -p 6379:6379 redis:latest

# Run with auto-reload
python -m main
```
## Docker Support

```bash
# Start Redis
docker run -d --name redis -p 6379:6379 redis:latest

# Run the application (configure environment variables first)
python -m main
```