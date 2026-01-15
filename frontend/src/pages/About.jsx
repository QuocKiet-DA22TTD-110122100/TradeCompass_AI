import React from 'react'
import './About.css'

function About() {
  return (
    <div className="container">
      <div className="about-page">
        <header className="page-header">
          <h1>ℹ️ About TradeCompass AI</h1>
          <p>Democratizing AI-powered trading for everyone</p>
        </header>

        <div className="about-content">
          <section className="card about-section">
            <h2>🎯 Our Mission</h2>
            <p>
              TradeCompass AI is built to democratize access to advanced trading insights. 
              We believe that everyone should have access to professional-grade AI-powered 
              market analysis, regardless of their background or resources.
            </p>
          </section>

          <section className="card about-section">
            <h2>✨ Key Features</h2>
            <div className="features-grid">
              <div className="feature-item">
                <div className="feature-icon">📊</div>
                <h3>Real-time Market Data</h3>
                <p>Access live market data and quotes for thousands of stocks</p>
              </div>
              <div className="feature-item">
                <div className="feature-icon">🤖</div>
                <h3>AI Predictions</h3>
                <p>Advanced machine learning models for price predictions</p>
              </div>
              <div className="feature-item">
                <div className="feature-icon">📈</div>
                <h3>Trading Signals</h3>
                <p>Real-time buy/sell signals powered by AI analysis</p>
              </div>
              <div className="feature-item">
                <div className="feature-icon">💡</div>
                <h3>Smart Recommendations</h3>
                <p>Personalized trading recommendations based on your risk profile</p>
              </div>
              <div className="feature-item">
                <div className="feature-icon">🎯</div>
                <h3>Sentiment Analysis</h3>
                <p>Market sentiment from news, social media, and analyst reports</p>
              </div>
              <div className="feature-item">
                <div className="feature-icon">🔒</div>
                <h3>Secure & Reliable</h3>
                <p>Enterprise-grade security and 99.9% uptime</p>
              </div>
            </div>
          </section>

          <section className="card about-section">
            <h2>🚀 How It Works</h2>
            <div className="steps">
              <div className="step">
                <div className="step-number">1</div>
                <div className="step-content">
                  <h3>Explore the Market</h3>
                  <p>Browse real-time market data and search for stocks you're interested in</p>
                </div>
              </div>
              <div className="step">
                <div className="step-number">2</div>
                <div className="step-content">
                  <h3>Get AI Insights</h3>
                  <p>Our AI analyzes multiple factors to generate predictions and recommendations</p>
                </div>
              </div>
              <div className="step">
                <div className="step-number">3</div>
                <div className="step-content">
                  <h3>Make Informed Decisions</h3>
                  <p>Use our insights to make better trading decisions with confidence</p>
                </div>
              </div>
            </div>
          </section>

          <section className="card about-section">
            <h2>🛠️ Technology Stack</h2>
            <div className="tech-stack">
              <div className="tech-category">
                <h3>Backend</h3>
                <ul>
                  <li>Python with FastAPI</li>
                  <li>Machine Learning with scikit-learn</li>
                  <li>Real-time data processing</li>
                </ul>
              </div>
              <div className="tech-category">
                <h3>Frontend</h3>
                <ul>
                  <li>React for UI</li>
                  <li>Modern responsive design</li>
                  <li>Real-time data visualization</li>
                </ul>
              </div>
              <div className="tech-category">
                <h3>AI & Analytics</h3>
                <ul>
                  <li>Advanced ML models</li>
                  <li>Sentiment analysis</li>
                  <li>Technical indicators</li>
                </ul>
              </div>
            </div>
          </section>

          <section className="card about-section cta-section">
            <h2>🌟 Ready to Get Started?</h2>
            <p>
              Join thousands of users who are already making smarter trading decisions 
              with TradeCompass AI. Our platform is completely free and accessible to everyone.
            </p>
            <div className="cta-buttons">
              <a href="/" className="btn btn-primary">Go to Dashboard</a>
              <a href="/predictions" className="btn btn-success">Try AI Predictions</a>
            </div>
          </section>

          <section className="card about-section">
            <h2>📞 Contact & Support</h2>
            <p>
              Have questions or feedback? We'd love to hear from you!
            </p>
            <div className="contact-info">
              <p>📧 Email: support@tradecompass-ai.com</p>
              <p>🐙 GitHub: github.com/QuocKiet-DA22TTD-110122100/TradeCompass_AI</p>
              <p>📚 Documentation: Available in the repository</p>
            </div>
          </section>
        </div>
      </div>
    </div>
  )
}

export default About
