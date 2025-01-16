# YouTube Semantic Search Service

A microservice that provides semantic search capabilities over YouTube video transcripts. Part of the Breaking Bad chat application ecosystem.

## Overview
This service:
- Fetches and processes YouTube video transcripts
- Creates semantic embeddings for transcript segments
- Provides a search API to find relevant video clips
- Integrates with the main chat application

## Project Structure
```
youtube-search/
├── src/
│   ├── service.py        # FastAPI service
│   ├── fetch.py          # Transcript fetching
│   ├── process.py        # Chunking and vectorization
│   └── search.py         # Search utilities
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── CHECKLIST.md          # Implementation progress
└── .env.example
```

## Environment Variables
```bash
# Required in .env
YOUTUBE_API_KEY=your_api_key
OPENAI_API_KEY=your_api_key
PINECONE_API_KEY=your_api_key
PINECONE_ENVIRONMENT=your_env
PINECONE_INDEX=your_index
```

## Development
1. Copy `.env.example` to `.env` and fill in values
2. Install dependencies: `pip install -r requirements.txt`
3. Run service: `uvicorn src.service:app --reload`

## Docker Deployment
```bash
docker-compose up -d
```

## API Documentation
Once running, visit:
- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

## Implementation Progress
See [CHECKLIST.md](CHECKLIST.md) for current implementation status and upcoming tasks. 