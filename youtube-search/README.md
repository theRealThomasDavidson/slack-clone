# YouTube Transcript Search

A semantic search engine for YouTube video transcripts. This service allows users to search through video content using natural language queries and get relevant video segments as responses.

## Features

- 🔍 Semantic search through video transcripts
- 💡 Question answering based on transcript content
- 🎯 Filter results by channel or video
- 🎥 Direct video playback at relevant timestamps
- 🌙 Dark mode UI with responsive design
- 🚀 Fast vector search using Pinecone
- 🤖 OpenAI embeddings for semantic understanding
- 🔄 Real-time transcript processing and chunking

## How It Works

1. **Data Collection**:
   - Using the YouTube Data API, we fetch video information from specified channels
   - We download video transcripts using `youtube_transcript_api`
   - Transcripts are saved as JSON files in `data/transcripts/`

2. **Data Processing**:
   - Transcripts are split into overlapping chunks (850-1000 characters)
   - Each chunk includes metadata: video title, URL, timestamps, and channel
   - Chunks are processed to maintain context and readability

3. **Vector Database**:
   - We use Pinecone as our vector database
   - Each chunk is converted to embeddings using OpenAI's text-embedding-ada-002 model
   - Embeddings are stored in Pinecone for efficient semantic search

4. **Search Implementation**:
   - User queries are converted to embeddings using the same model
   - Pinecone performs similarity search to find relevant transcript chunks
   - Results include direct links to video timestamps

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

## Environment Setup

1. **Prerequisites**:
   - Python 3.11+
   - Node.js 18+
   - Docker and Docker Compose
   - Pinecone account
   - OpenAI API key

2. **Environment Variables**:
   Create a `.env` file with:
   ```env
   OPENAI_API_KEY=your_openai_key
   PINECONE_API_KEY=your_pinecone_key
   PINECONE_ENVIRONMENT=gcp-starter
   PINECONE_INDEX=your_index_name
   PINECONE_NAMESPACE=youtube_transcripts
   ```

3. **Running the Application**:
   ```bash
   # Build and start containers
   docker-compose up --build

   # The API will be available at http://localhost:8001
   # Frontend will be available at http://localhost:5173
   ```

4. **Data Pipeline** (if you want to add more videos):
   ```bash
   # Fetch transcripts
   python src/fetch.py

   # Process and chunk transcripts
   python src/process.py

   # Upload to Pinecone
   python src/data/upload.py
   ```

## API Documentation

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

## Tech Stack

- **Backend**: 
  - FastAPI for API development
  - OpenAI for embeddings and question answering
  - Pinecone for vector search
  - Python 3.11+ for processing

- **Frontend**:
  - React with TypeScript
  - Tailwind CSS for styling
  - Video embedding and playback

- **Infrastructure**:
  - Docker and Docker Compose
  - Environment-based configuration
  - Hot reload for development

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request 