import React, { useState, useEffect } from 'react'
import axios from 'axios'
import './Predictions.css'

function Predictions() {
  const [symbol, setSymbol] = useState('AAPL')
  const [prediction, setPrediction] = useState(null)
  const [recommendations, setRecommendations] = useState([])
  const [riskLevel, setRiskLevel] = useState('medium')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchRecommendations()
  }, [riskLevel])

  const fetchRecommendations = async () => {
    try {
      const response = await axios.get(`/api/predictions/recommendations?risk_level=${riskLevel}`)
      setRecommendations(response.data.recommendations)
    } catch (error) {
      console.error('Error fetching recommendations:', error)
    }
  }

  const handlePredict = async (e) => {
    e.preventDefault()
    if (!symbol) return

    setLoading(true)
    try {
      const response = await axios.post('/api/predictions/predict', {
        symbol: symbol,
        horizon: '1d'
      })
      setPrediction(response.data)
    } catch (error) {
      console.error('Error getting prediction:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container">
      <div className="predictions-page">
        <header className="page-header">
          <h1>🤖 AI Predictions</h1>
          <p>Advanced AI-powered trading insights</p>
        </header>

        <div className="prediction-form-section">
          <div className="card">
            <h2>Get Price Prediction</h2>
            <form onSubmit={handlePredict} className="prediction-form">
              <input
                type="text"
                placeholder="Enter symbol (e.g., AAPL)"
                value={symbol}
                onChange={(e) => setSymbol(e.target.value.toUpperCase())}
                className="symbol-input"
              />
              <button type="submit" className="btn btn-primary" disabled={loading}>
                {loading ? 'Analyzing...' : 'Get AI Prediction'}
              </button>
            </form>
          </div>
        </div>

        {prediction && (
          <div className="prediction-result">
            <div className="card">
              <div className="prediction-header">
                <h2>{prediction.symbol}</h2>
                <span className={`recommendation-badge ${prediction.recommendation}`}>
                  {prediction.recommendation.toUpperCase()}
                </span>
              </div>

              <div className="price-comparison">
                <div className="price-box">
                  <div className="price-label">Current Price</div>
                  <div className="price-value">${prediction.current_price}</div>
                </div>
                <div className="arrow">→</div>
                <div className="price-box">
                  <div className="price-label">Predicted Price</div>
                  <div className="price-value predicted">${prediction.predicted_price}</div>
                </div>
              </div>

              <div className="prediction-metrics">
                <div className="metric">
                  <span className="metric-label">Expected Change</span>
                  <span className={`metric-value ${prediction.predicted_change >= 0 ? 'positive' : 'negative'}`}>
                    {prediction.predicted_change >= 0 ? '+' : ''}{prediction.predicted_change}
                    ({prediction.predicted_change_percent}%)
                  </span>
                </div>
                <div className="metric">
                  <span className="metric-label">Confidence</span>
                  <span className="metric-value">{(prediction.confidence * 100).toFixed(0)}%</span>
                </div>
                <div className="metric">
                  <span className="metric-label">Direction</span>
                  <span className={`metric-value ${prediction.direction}`}>
                    {prediction.direction === 'up' ? '📈' : prediction.direction === 'down' ? '📉' : '➡️'}
                    {' '}{prediction.direction.toUpperCase()}
                  </span>
                </div>
              </div>

              <div className="factors-section">
                <h3>Analysis Factors</h3>
                <div className="factors">
                  {prediction.factors.map((factor, i) => (
                    <div key={i} className="factor-item">
                      <div className="factor-header">
                        <span className="factor-name">{factor.name}</span>
                        <span className={`factor-impact ${factor.impact}`}>
                          {factor.impact}
                        </span>
                      </div>
                      <div className="factor-score">
                        <div className="score-bar">
                          <div 
                            className="score-fill" 
                            style={{ width: `${factor.score * 100}%` }}
                          ></div>
                        </div>
                        <span className="score-value">{(factor.score * 100).toFixed(0)}%</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        <div className="recommendations-section">
          <div className="recommendations-header">
            <h2>AI Recommendations</h2>
            <div className="risk-selector">
              <label>Risk Level:</label>
              <select value={riskLevel} onChange={(e) => setRiskLevel(e.target.value)}>
                <option value="low">Low Risk</option>
                <option value="medium">Medium Risk</option>
                <option value="high">High Risk</option>
              </select>
            </div>
          </div>

          <div className="grid grid-2">
            {recommendations.map((rec, i) => (
              <div key={i} className="card recommendation-card">
                <div className="rec-header">
                  <h3>{rec.symbol}</h3>
                  <span className={`action-badge ${rec.action}`}>
                    {rec.action.toUpperCase()}
                  </span>
                </div>

                <div className="rec-prices">
                  <div className="rec-price-item">
                    <span>Target:</span>
                    <span className="price">${rec.target_price}</span>
                  </div>
                  <div className="rec-price-item">
                    <span>Stop Loss:</span>
                    <span className="price">${rec.stop_loss}</span>
                  </div>
                </div>

                <div className="rec-confidence">
                  Confidence: {(rec.confidence * 100).toFixed(0)}%
                </div>

                <div className="rec-reasoning">
                  {rec.reasoning}
                </div>

                <div className="rec-meta">
                  <span className="risk-tag">{rec.risk_level} risk</span>
                  <span className="horizon-tag">{rec.time_horizon}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Predictions
