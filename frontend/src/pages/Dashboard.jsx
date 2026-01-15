import React, { useEffect, useState } from 'react'
import axios from 'axios'
import './Dashboard.css'

function Dashboard() {
  const [overview, setOverview] = useState(null)
  const [signals, setSignals] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const [overviewRes, signalsRes] = await Promise.all([
        axios.get('/api/market/overview'),
        axios.get('/api/predictions/signals?limit=5')
      ])
      setOverview(overviewRes.data)
      setSignals(signalsRes.data.signals)
      setLoading(false)
    } catch (error) {
      console.error('Error fetching data:', error)
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="container">
        <div className="loading">Loading dashboard...</div>
      </div>
    )
  }

  return (
    <div className="container">
      <div className="dashboard">
        <header className="dashboard-header">
          <h1>📊 Trading Dashboard</h1>
          <p>AI-powered insights at your fingertips</p>
        </header>

        {/* Market Indices */}
        <section className="section">
          <h2>Market Overview</h2>
          <div className="grid grid-3">
            {overview?.indices?.map((index, i) => (
              <div key={i} className="card stat-card">
                <div className="stat-name">{index.name}</div>
                <div className="stat-value">{index.value.toLocaleString()}</div>
                <div className={`stat-change ${index.change >= 0 ? 'positive' : 'negative'}`}>
                  {index.change >= 0 ? '↑' : '↓'} {Math.abs(index.change)}%
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Top Movers */}
        <section className="section">
          <h2>Top Market Movers</h2>
          <div className="grid grid-2">
            <div className="card">
              <h3 className="card-title">🚀 Top Gainers</h3>
              {overview?.top_gainers?.map((stock, i) => (
                <div key={i} className="stock-item">
                  <div className="stock-info">
                    <span className="stock-symbol">{stock.symbol}</span>
                    <span className="stock-price">${stock.price}</span>
                  </div>
                  <span className="stock-change positive">
                    +{stock.change_percent.toFixed(2)}%
                  </span>
                </div>
              ))}
            </div>

            <div className="card">
              <h3 className="card-title">📉 Top Losers</h3>
              {overview?.top_losers?.map((stock, i) => (
                <div key={i} className="stock-item">
                  <div className="stock-info">
                    <span className="stock-symbol">{stock.symbol}</span>
                    <span className="stock-price">${stock.price}</span>
                  </div>
                  <span className="stock-change negative">
                    {stock.change_percent.toFixed(2)}%
                  </span>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* AI Trading Signals */}
        <section className="section">
          <h2>🤖 AI Trading Signals</h2>
          <div className="card">
            {signals.map((signal, i) => (
              <div key={i} className="signal-item">
                <div className="signal-header">
                  <span className="signal-symbol">{signal.symbol}</span>
                  <span className={`signal-badge ${signal.signal_type}`}>
                    {signal.signal_type.toUpperCase()}
                  </span>
                </div>
                <div className="signal-details">
                  <div className="signal-strength">
                    Strength: {signal.strength}%
                    <div className="strength-bar">
                      <div 
                        className="strength-fill" 
                        style={{ width: `${signal.strength}%` }}
                      ></div>
                    </div>
                  </div>
                  <div className="signal-price">Price: ${signal.price}</div>
                </div>
                <div className="signal-reasoning">{signal.reasoning}</div>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  )
}

export default Dashboard
