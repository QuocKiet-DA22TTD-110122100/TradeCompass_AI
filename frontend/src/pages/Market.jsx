import React, { useState } from 'react'
import axios from 'axios'
import './Market.css'

function Market() {
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState([])
  const [selectedSymbol, setSelectedSymbol] = useState(null)
  const [quote, setQuote] = useState(null)

  const handleSearch = async (e) => {
    e.preventDefault()
    if (!searchQuery) return

    try {
      const response = await axios.get(`/api/market/search?q=${searchQuery}`)
      setSearchResults(response.data.results)
    } catch (error) {
      console.error('Error searching:', error)
    }
  }

  const handleSelectSymbol = async (symbol) => {
    setSelectedSymbol(symbol)
    try {
      const response = await axios.get(`/api/market/quote/${symbol}`)
      setQuote(response.data)
    } catch (error) {
      console.error('Error fetching quote:', error)
    }
  }

  return (
    <div className="container">
      <div className="market-page">
        <header className="page-header">
          <h1>📈 Market Explorer</h1>
          <p>Search and analyze any stock</p>
        </header>

        <div className="search-section">
          <form onSubmit={handleSearch} className="search-form">
            <input
              type="text"
              placeholder="Search stocks (e.g., AAPL, Microsoft)..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="search-input"
            />
            <button type="submit" className="btn btn-primary">
              Search
            </button>
          </form>

          {searchResults.length > 0 && (
            <div className="card search-results">
              <h3>Search Results</h3>
              {searchResults.map((result, i) => (
                <div
                  key={i}
                  className="search-result-item"
                  onClick={() => handleSelectSymbol(result.symbol)}
                >
                  <div>
                    <div className="result-symbol">{result.symbol}</div>
                    <div className="result-name">{result.name}</div>
                  </div>
                  <div className="result-exchange">{result.exchange}</div>
                </div>
              ))}
            </div>
          )}
        </div>

        {quote && (
          <div className="quote-section">
            <div className="card">
              <div className="quote-header">
                <h2>{quote.symbol}</h2>
                <div className="quote-price">${quote.price}</div>
                <div className={`quote-change ${quote.change >= 0 ? 'positive' : 'negative'}`}>
                  {quote.change >= 0 ? '↑' : '↓'} ${Math.abs(quote.change).toFixed(2)} (
                  {quote.change_percent.toFixed(2)}%)
                </div>
              </div>

              <div className="quote-details grid grid-2">
                <div className="quote-item">
                  <span className="quote-label">Open</span>
                  <span className="quote-value">${quote.open}</span>
                </div>
                <div className="quote-item">
                  <span className="quote-label">High</span>
                  <span className="quote-value">${quote.high}</span>
                </div>
                <div className="quote-item">
                  <span className="quote-label">Low</span>
                  <span className="quote-value">${quote.low}</span>
                </div>
                <div className="quote-item">
                  <span className="quote-label">Volume</span>
                  <span className="quote-value">{quote.volume.toLocaleString()}</span>
                </div>
                <div className="quote-item">
                  <span className="quote-label">Market Cap</span>
                  <span className="quote-value">{quote.market_cap}</span>
                </div>
                <div className="quote-item">
                  <span className="quote-label">P/E Ratio</span>
                  <span className="quote-value">{quote.pe_ratio}</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default Market
