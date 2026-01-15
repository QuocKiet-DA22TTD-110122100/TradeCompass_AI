# TradeCompass AI 📊

**AI-Powered Trading Ecosystem for Everyone**

TradeCompass AI is a comprehensive trading platform that democratizes access to advanced AI-powered market analysis and trading insights. Built with modern technologies and designed for accessibility, it provides professional-grade trading tools to everyone.

## 🌟 Features

- **📈 Real-time Market Data**: Access live market data, quotes, and indices
- **🤖 AI Predictions**: Advanced machine learning models for price predictions
- **📊 Trading Signals**: Real-time buy/sell signals powered by AI analysis
- **💡 Smart Recommendations**: Personalized trading recommendations based on risk profiles
- **🎯 Sentiment Analysis**: Market sentiment from news, social media, and analyst reports
- **🔒 Secure & Reliable**: Enterprise-grade security and reliability

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker (optional)

### Option 1: Docker (Recommended)

The easiest way to run TradeCompass AI is with Docker:

```bash
# Clone the repository
git clone https://github.com/QuocKiet-DA22TTD-110122100/TradeCompass_AI.git
cd TradeCompass_AI

# Start with Docker Compose
docker-compose up -d

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 2: Manual Setup

#### Backend Setup

```bash
# Navigate to project root
cd TradeCompass_AI

# Install Python dependencies
pip install -r requirements.txt

# Run the backend server
cd backend
python main.py
```

The backend API will be available at `http://localhost:8000`

#### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run the development server
npm run dev
```

The frontend will be available at `http://localhost:3000`

## 📖 API Documentation

Once the backend is running, visit:
- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

### Key Endpoints

#### Market Data
- `GET /api/market/overview` - Get market overview
- `GET /api/market/quote/{symbol}` - Get stock quote
- `GET /api/market/history/{symbol}` - Get historical data
- `GET /api/market/search?q={query}` - Search for stocks

#### AI Predictions
- `POST /api/predictions/predict` - Get AI price prediction
- `GET /api/predictions/signals` - Get trading signals
- `GET /api/predictions/recommendations` - Get AI recommendations
- `GET /api/predictions/sentiment/{symbol}` - Get sentiment analysis

#### Health & Status
- `GET /health` - Health check
- `GET /status` - Detailed status

## 🏗️ Architecture

```
TradeCompass_AI/
├── backend/              # Python FastAPI backend
│   ├── main.py          # Main application entry
│   ├── api/             # API routes
│   │   └── routes/      # Endpoint definitions
│   ├── core/            # Core functionality
│   ├── models/          # Data models
│   └── services/        # Business logic
├── frontend/            # React frontend
│   ├── src/
│   │   ├── pages/       # Page components
│   │   ├── components/  # Reusable components
│   │   ├── App.jsx      # Main app component
│   │   └── main.jsx     # Entry point
│   └── public/          # Static assets
├── requirements.txt     # Python dependencies
├── package.json         # Node.js dependencies
├── docker-compose.yml   # Docker orchestration
└── README.md           # This file
```

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **Python 3.11**: Core programming language
- **scikit-learn**: Machine learning for predictions
- **pandas & numpy**: Data processing and analysis
- **yfinance**: Market data fetching
- **uvicorn**: ASGI server

### Frontend
- **React 18**: Modern UI library
- **Vite**: Fast build tool and dev server
- **React Router**: Client-side routing
- **Axios**: HTTP client for API calls
- **Recharts**: Data visualization (future enhancement)

### DevOps
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration

## 🎯 Use Cases

1. **Individual Traders**: Get AI-powered insights for better trading decisions
2. **Investors**: Analyze market trends and sentiment
3. **Students**: Learn about trading and AI applications
4. **Researchers**: Study market behavior and AI predictions
5. **Developers**: Build on top of the API

## 🌐 Ecosystem Philosophy

TradeCompass AI is built on the principle that **everyone should have access to professional-grade trading tools**. The ecosystem includes:

- **Open API**: RESTful API for integration
- **Web Interface**: User-friendly dashboard
- **Documentation**: Comprehensive guides
- **Community Support**: Open-source collaboration
- **Extensibility**: Easy to extend and customize

## 📚 Development

### Running Tests

```bash
# Backend tests (when implemented)
cd backend
pytest

# Frontend tests (when implemented)
cd frontend
npm test
```

### Building for Production

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
npm run build
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is open source and available for everyone to use.

## 🙏 Acknowledgments

- Market data powered by various financial APIs
- AI models built with scikit-learn
- UI inspired by modern trading platforms

## 📞 Support

For questions, issues, or feedback:
- Create an issue on GitHub
- Email: support@tradecompass-ai.com
- Documentation: See `/docs` folder

## 🔮 Roadmap

- [ ] Enhanced AI models with deep learning
- [ ] Real-time WebSocket updates
- [ ] Portfolio tracking
- [ ] Mobile app
- [ ] Multi-language support
- [ ] Advanced charting
- [ ] Social trading features
- [ ] Backtesting capabilities

---

**Built with ❤️ for the trading community**