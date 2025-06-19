const express = require('express');
const cors = require('cors');
const path = require('path');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static('static'));
app.use('/data', express.static('data'));

// Serve the main application
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

// API endpoint for stock tickers (mock data for now)
app.get('/api/tickers', (req, res) => {
  const query = req.query.q || '';
  const page = parseInt(req.query.page) || 1;
  const perPage = 100;
  
  // Mock ticker data based on the CSV
  const mockTickers = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX', 'ADBE', 'CRM',
    'ORCL', 'INTC', 'AMD', 'QCOM', 'AVGO', 'TXN', 'INTU', 'ISRG', 'CMCSA', 'TMUS',
    'COST', 'AMGN', 'HON', 'SBUX', 'GILD', 'MDLZ', 'BKNG', 'ADP', 'VRTX', 'FISV'
  ];
  
  const filtered = query ? 
    mockTickers.filter(ticker => ticker.toLowerCase().includes(query.toLowerCase())) : 
    mockTickers;
  
  const start = (page - 1) * perPage;
  const end = start + perPage;
  const results = filtered.slice(start, end);
  
  res.json({
    results,
    page,
    totalPages: Math.ceil(filtered.length / perPage),
    hasMore: page < Math.ceil(filtered.length / perPage),
    hasPrev: page > 1
  });
});

// Stock detail endpoint
app.get('/api/stock/:ticker', (req, res) => {
  const { ticker } = req.params;
  
  // Mock stock data
  const stockData = {
    symbol: ticker,
    name: `${ticker} Inc.`,
    price: (Math.random() * 200 + 50).toFixed(2),
    change: (Math.random() * 10 - 5).toFixed(2),
    changePercent: (Math.random() * 5 - 2.5).toFixed(2),
    marketCap: `$${(Math.random() * 1000 + 100).toFixed(0)}B`,
    volume: `${(Math.random() * 50 + 10).toFixed(0)}M`,
    pe: (Math.random() * 30 + 10).toFixed(1)
  };
  
  res.json(stockData);
});

app.listen(PORT, () => {
  console.log(`🚀 Calibrisa server running on http://localhost:${PORT}`);
  console.log('📊 Stock Market Platform Ready!');
});