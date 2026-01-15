# TradeCompass AI - Setup Guide

## Quick Setup Guide

### 1. Prerequisites

Before you begin, ensure you have the following installed:
- **Python 3.11 or higher**: [Download Python](https://www.python.org/downloads/)
- **Node.js 18 or higher**: [Download Node.js](https://nodejs.org/)
- **Git**: [Download Git](https://git-scm.com/downloads)

Optional but recommended:
- **Docker Desktop**: [Download Docker](https://www.docker.com/products/docker-desktop)

### 2. Clone the Repository

```bash
git clone https://github.com/QuocKiet-DA22TTD-110122100/TradeCompass_AI.git
cd TradeCompass_AI
```

### 3. Setup Methods

Choose one of the following methods:

#### Method A: Docker (Easiest)

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Access:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

#### Method B: Manual Setup

**Backend:**

```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Start backend server
cd backend
python main.py
```

Backend will run at http://localhost:8000

**Frontend:**

```bash
# In a new terminal, navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will run at http://localhost:3000

### 4. Verify Installation

1. Open http://localhost:3000 in your browser
2. You should see the TradeCompass AI dashboard
3. Navigate through the different pages:
   - Dashboard: Overview of market data
   - Market: Search and view stock quotes
   - AI Predictions: Get AI-powered predictions

### 5. API Testing

Visit http://localhost:8000/docs to access the interactive API documentation.

Try these example requests:

```bash
# Get market overview
curl http://localhost:8000/api/market/overview

# Get stock quote
curl http://localhost:8000/api/market/quote/AAPL

# Get AI prediction
curl -X POST http://localhost:8000/api/predictions/predict \
  -H "Content-Type: application/json" \
  -d '{"symbol":"AAPL","horizon":"1d"}'
```

## Troubleshooting

### Backend Issues

**Port already in use:**
```bash
# Change the port in backend/main.py
uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
```

**Module not found:**
```bash
# Ensure you're in the correct directory and virtual environment is activated
pip install -r requirements.txt
```

### Frontend Issues

**Port already in use:**
```bash
# The dev server will automatically try the next available port
# Or specify a custom port in vite.config.js
```

**Dependencies error:**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Docker Issues

**Permission denied:**
```bash
# On Linux, add your user to docker group
sudo usermod -aG docker $USER
# Log out and back in
```

**Port conflicts:**
```bash
# Edit docker-compose.yml to use different ports
```

## Next Steps

1. Explore the dashboard and try different features
2. Check the API documentation at http://localhost:8000/docs
3. Customize the configuration in `.env` file
4. Read the main README.md for more details
5. Start building your own features!

## Getting Help

- Check the documentation in `/docs` folder
- Create an issue on GitHub
- Review the code comments for implementation details
