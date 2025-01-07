# Chat Application MVP Demo

A real-time chat application with user authentication, channels, and message polling.

## Quick Start

### Requirements
- Python 3.11+
- Node.js 18+
- npm 9+

### Environment Setup
Create a `.env` file in the `api` directory:
```bash
JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Backend Setup
```bash
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Unix/MacOS

# Install dependencies
cd api
pip install -r requirements.txt

# Run the server
uvicorn api.main:app --reload
```

### Frontend Setup
```bash
# Install dependencies
cd frontend
npm install

# Run the development server
npm run dev
```

## Features
- User authentication (register/login)
- Channel creation and management
- Real-time messaging with polling (333ms interval)
- Modern UI with Tailwind CSS
- TypeScript for type safety

## 5-Minute Demo Script

### 1. Backend Architecture (1 minute)
- Open `http://localhost:8000/docs` to show Swagger UI
- Highlight key endpoints: auth, messages, channels
- Show request/response schemas
- Point out JWT authentication

### 2. Testing & Code Quality (1 minute)
```bash
cd api
pytest
```
- Show test organization in `api/tests/`
- Highlight key test files:
  - `test_auth.py`
  - `test_messages.py`
  - `test_channels.py`

### 3. Live Demo (3 minutes)
1. Create two accounts for testing:
   ```
   Account 1:
   - Username: alice
   - Password: test1234

   Account 2:
   - Username: bob
   - Password: test1234
   ```
2. Open two browser windows (or use incognito for second window)
3. Log in as alice in one window and bob in the other
4. Create a channel as alice
5. Join the channel as bob
6. Demonstrate real-time chat
7. Show message persistence (refresh page)

### Code Organization
```
api/
├── routes/      # API endpoints
├── services/    # Business logic
├── models/      # Data models
├── repositories/# Data storage
├── core/        # Configuration
└── tests/       # Test suite
```

## API Documentation
FastAPI provides automatic interactive API documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Using Swagger with LLMs
The Swagger UI provides a machine-readable JSON format of the API documentation at `http://localhost:8000/openapi.json`. This JSON schema:
- Contains complete API endpoint definitions
- Includes request/response models
- Documents authentication requirements
- Lists all available endpoints and methods

This structured format makes it ideal for:
- Feeding into LLMs for API understanding
- Automated code generation
- Integration testing
- Client library generation

You can test all API endpoints directly through the Swagger UI interface.

## Tech Stack
- Backend: FastAPI + Python
- Frontend: React + TypeScript + Vite
- Styling: Tailwind CSS
- State Management: React Context
- Testing: Jest + React Testing Library

## Development
- Backend API runs on `http://localhost:8000`
- Frontend dev server runs on `http://localhost:5173` 

## Implementation Details

### Real-time Messaging
The chat implementation uses a polling mechanism with a 333ms interval for real-time updates:
- Client polls the server every 333ms for new messages
- Messages are stored with timestamps for ordering
- Channel-specific message retrieval for efficiency
- Automatic reconnection handling

### WebSocket Implementation (Disabled for Demo)
The codebase includes a WebSocket implementation that is disabled for this demo in favor of the simpler polling approach:
- Endpoint: `/api/ws/{username}`
- Authentication via JWT token
- Real-time message broadcasting
- Channel-based message routing 