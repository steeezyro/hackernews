# HackerNews Analysis Platform

A modern, real-time HackerNews story analysis platform that captures screenshots and generates AI-powered summaries of the top 10 stories.

## 🚀 Features

- **Real-time Updates**: Auto-refreshing content with manual refresh capability
- **AI Summaries**: Intelligent article summaries powered by Google Gemini
- **Screenshots**: Visual previews of article pages
- **Performance Optimized**: Parallel processing and intelligent caching
- **Rate Limited**: Production-ready API with rate limiting
- **TypeScript Frontend**: Modern React with TypeScript and Tailwind CSS
- **Structured Backend**: Clean architecture with proper separation of concerns
- **SQLite Database**: Persistent data storage with caching
- **Error Handling**: Comprehensive error handling and user feedback

## 🏗️ Architecture

```
hackernews/
├── backend/                 # Python FastAPI backend
│   ├── src/
│   │   ├── models/         # Data models
│   │   ├── services/       # Business logic
│   │   ├── utils/          # Utilities (rate limiting, logging)
│   │   └── routes/         # API endpoints
│   ├── tests/              # Backend tests
│   └── main.py             # Application entry point
└── frontend/               # React TypeScript frontend
    ├── src/
    │   ├── components/     # React components
    │   ├── hooks/          # Custom React hooks
    │   ├── types/          # TypeScript type definitions
    │   └── utils/          # Frontend utilities
    └── package.json
```

## 🛠️ Tech Stack

### Backend
- **FastAPI**: High-performance async web framework
- **Python 3.8+**: Modern Python with type hints
- **Playwright**: Reliable browser automation
- **Google Gemini**: AI-powered text summarization
- **SQLite**: Lightweight database with caching
- **Uvicorn**: ASGI server for production

### Frontend
- **React 19**: Latest React with modern hooks
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS**: Utility-first CSS framework
- **Vite**: Fast build tool and dev server

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 18+
- Google Gemini API key

### Backend Setup

1. **Install dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   playwright install chromium
   ```

2. **Environment configuration**:
   ```bash
   # Create .env file
   echo "GEMINI_API_KEY=your_api_key_here" > .env
   ```

3. **Run backend**:
   ```bash
   python main.py
   # Or with uvicorn directly:
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. **Install dependencies**:
   ```bash
   cd frontend
   npm install
   ```

2. **Environment configuration**:
   ```bash
   # Create .env file
   echo "VITE_API_URL=http://localhost:8000" > .env
   ```

3. **Run frontend**:
   ```bash
   npm run dev
   ```

4. **Build for production**:
   ```bash
   npm run build
   npm run preview
   ```

## 📡 API Endpoints

### Core Endpoints
- `GET /` - Health check and system status
- `GET /api/articles` - Get cached articles with metadata
- `POST /api/refresh` - Trigger article refresh (rate limited)
- `GET /api/status` - System status and cache information

### Legacy Endpoints (for compatibility)
- `GET /api/results` - Legacy articles endpoint
- `GET /run` - Legacy refresh endpoint

### Rate Limiting
- **Refresh endpoint**: 5 requests per 5 minutes per IP
- **Cache-first approach**: Returns cached data if fresh (< 2 minutes old)
- **Background processing**: Long-running tasks execute in background

## 🔧 Configuration

### Backend Environment Variables
```bash
GEMINI_API_KEY=your_gemini_api_key    # Required: Google Gemini API key
LOG_LEVEL=INFO                        # Optional: Logging level
```

### Frontend Environment Variables
```bash
VITE_API_URL=http://localhost:8000    # Backend API URL
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pip install pytest pytest-asyncio
pytest tests/ -v
```

### Frontend Type Checking
```bash
cd frontend
npm run type-check
npm run lint
```

## 📊 Performance Features

- **Parallel Processing**: Screenshots and summaries generated concurrently
- **Smart Caching**: SQLite-based caching with freshness checks
- **Rate Limiting**: Prevents API abuse and ensures stability
- **Image Optimization**: Compressed screenshots for faster loading
- **Auto-refresh**: Background updates every 5 minutes
- **Error Recovery**: Graceful handling of failed requests

## 🛡️ Security Features

- **Rate Limiting**: IP-based request limiting
- **Input Validation**: Comprehensive request validation
- **CORS Configuration**: Restricted cross-origin requests
- **Error Masking**: Sensitive errors not exposed to clients
- **API Key Protection**: Environment-based secret management

## 🚀 Deployment

### Backend Deployment
```bash
# Using uvicorn in production
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# Or using Docker (create Dockerfile)
docker build -t hackernews-backend .
docker run -p 8000:8000 --env-file .env hackernews-backend
```

### Frontend Deployment
```bash
npm run build
# Deploy dist/ folder to your static hosting service
```

## 🔍 Monitoring

The application provides built-in monitoring:
- **Structured Logging**: JSON logs with timestamps and severity
- **Health Checks**: `/` endpoint for health monitoring
- **Cache Metrics**: Cache hit rates and freshness data
- **Rate Limit Metrics**: Request tracking and limit status

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎯 Why This Implementation?

This project demonstrates:
- **Production-ready architecture** with proper separation of concerns
- **Modern full-stack development** with TypeScript and Python
- **Performance optimization** through caching and parallel processing
- **User experience focus** with real-time updates and error handling
- **Security best practices** with rate limiting and validation
- **Scalable design** ready for enterprise deployment