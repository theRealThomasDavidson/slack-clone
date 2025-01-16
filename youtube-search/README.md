# YouTube Transcript Search Service

A microservice that enables semantic search over YouTube video transcripts. Built with FastAPI, OpenAI embeddings, and Pinecone vector database.

## Features

- 🔍 Semantic search through video transcripts
- 💡 Question answering based on transcript content
- 🎯 Filter results by channel or video
- 🚀 Fast vector search using Pinecone
- 🤖 OpenAI embeddings for semantic understanding
- 🔄 Real-time transcript processing and chunking

## Setup

1. Clone the repository
2. Create a `.env` file with required credentials:
```env
OPENAI_API_KEY=your_openai_key
PINECONE_API_KEY=your_pinecone_key
PINECONE_ENVIRONMENT=gcp-starter
PINECONE_INDEX=your_index_name
PINECONE_NAMESPACE=youtube_transcripts
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run with Docker:
```bash
docker-compose up --build
```

The service will be available at `http://localhost:8001`

## API Endpoints

### Search Transcripts
```http
POST /api/search
Content-Type: application/json

{
    "query": "your search query",
    "filters": {
        "channel": "optional channel name"
    }
}
```

### Ask Questions
```http
POST /api/ask
Content-Type: application/json

{
    "question": "your question about the content",
    "num_segments": 5
}
```

### List Channels
```http
GET /api/channels
```

## Project Structure

```
youtube-search/
├── src/
│   ├── api/          # FastAPI application and routes
│   ├── core/         # Core types and interfaces
│   ├── search/       # Search and QA functionality
│   └── tests/        # Test scripts and examples
├── data/
│   ├── transcripts/  # Raw transcript data
│   └── processed/    # Processed chunks
├── Dockerfile        # Container definition
└── docker-compose.yml
```

## Development

1. Run with hot reload:
```bash
docker-compose up --build
```

2. Access API documentation:
```
http://localhost:8001/docs
```

3. Run tests:
```bash
python -m pytest src/tests
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| OPENAI_API_KEY | OpenAI API key for embeddings | Yes |
| PINECONE_API_KEY | Pinecone API key | Yes |
| PINECONE_ENVIRONMENT | Pinecone environment (e.g. gcp-starter) | Yes |
| PINECONE_INDEX | Pinecone index name | Yes |
| PINECONE_NAMESPACE | Namespace for vectors (default: youtube_transcripts) | Yes |

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request 