# VeriFact

An AI-powered news validation system that helps verify the credibility of news articles by analyzing claims, checking sources, and detecting contradictions across multiple news sources.

## Features

- **Claim Extraction**: Automatically identify key claims in news articles
- **Source Verification**: Cross-reference information with multiple news sources
- **Contradiction Detection**: Identify conflicting information across sources
- **Credibility Scoring**: Generate confidence scores for news articles
- **API Integration**: Built with FastAPI for easy integration

## Tech Stack

### Backend
- **Framework**: FastAPI (Python)
- **AI/ML**: Google Gemini API
- **News API**: NewsAPI/Google News API
- **Database**: PostgreSQL
- **Caching**: Redis
- **Containerization**: Docker

### Frontend (Coming Soon)
- **Framework**: React + Vite
- **Styling**: Tailwind CSS
- **Deployment**: Vercel

## Getting Started

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- Google Gemini API Key
- NewsAPI Key

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/news-validator-agent.git
   cd news-validator-agent
   ```

2. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

3. Build and start the services:
   ```bash
   docker-compose up --build
   ```

4. Access the API documentation at `http://localhost:8000/docs`

## Project Structure

```
.
├── backend/               # Backend FastAPI application
│   ├── src/               # Source code
│   │   ├── __init__.py
│   │   ├── main.py        # FastAPI application entry point
│   │   ├── config.py      # Configuration settings
│   │   ├── models/        # Database models
│   │   ├── routes/        # API routes
│   │   ├── services/      # Business logic
│   │   └── utils/         # Utility functions
│   ├── tests/             # Test files
│   ├── requirements.txt   # Python dependencies
│   └── Dockerfile         # Docker configuration
├── frontend/              # Frontend React application (coming soon)
├── docs/                  # Documentation
├── docker-compose.yml     # Docker Compose configuration
└── README.md              # This file
```

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
# Backend
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_ORIGINS=*

# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=news_validator
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# Google Gemini API
GEMINI_API_KEY=your-gemini-api-key

# NewsAPI
NEWS_API_KEY=your-newsapi-key
```

## API Documentation

Once the application is running, you can access the interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=backend tests/
```

### Code Style

This project uses:
- **Black** for code formatting
- **Flake8** for linting
- **Mypy** for type checking

Run the following commands before committing:

```bash
black .
flake8
mypy .
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Team

- [Your Name] - Backend Developer
- [Team Member 2] - Frontend Developer
- [Team Member 3] - DevOps & Documentation

## Acknowledgments

- Google Gemini for the powerful AI capabilities
- FastAPI for the excellent web framework
- NewsAPI for providing news data
