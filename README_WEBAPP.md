# RiskIQ Web Application

A modern, responsive web application for advanced risk analysis and portfolio management, built on top of your existing RiskIQ backend API.

## 🚀 Features

### Single Stock Analysis
- **Real-time Risk Metrics**: Historical volatility, VaR (95%), and CVaR (95%)
- **AI-Powered Forecasts**: GARCH, XGBoost, and LSTM volatility predictions
- **Interactive Charts**: Price history and returns visualization
- **Intelligent Risk Assessment**: AI-generated risk analysis and recommendations
- **Risk Level Classification**: Visual risk badges (LOW, MODERATE, HIGH, etc.)

### Portfolio Analysis
- **Multi-Stock Analysis**: Analyze up to 10 stocks simultaneously
- **Portfolio Risk Metrics**: Average volatility, VaR, and CVaR across holdings
- **Individual Stock Breakdown**: Detailed risk metrics for each position
- **Risk Distribution Charts**: Visual representation of portfolio risk
- **Diversification Analysis**: AI-powered portfolio recommendations

### Modern UI/UX
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Beautiful Interface**: Modern gradient design with smooth animations
- **Interactive Elements**: Hover effects, loading states, and smooth transitions
- **Error Handling**: User-friendly error messages and validation
- **Tab-based Navigation**: Easy switching between single stock and portfolio analysis

## 🛠️ Technology Stack

### Frontend
- **HTML5**: Semantic markup structure
- **CSS3**: Modern styling with gradients, flexbox, and grid
- **JavaScript (ES6+)**: Interactive functionality and API communication
- **Chart.js**: Beautiful data visualizations
- **Font Awesome**: Professional icons

### Backend Integration
- **FastAPI**: RESTful API endpoints
- **CORS Support**: Cross-origin resource sharing enabled
- **Error Handling**: Comprehensive error management

## 📁 Project Structure

```
frontend/
├── index.html          # Main HTML structure
├── styles.css          # CSS styling and responsive design
├── script.js           # JavaScript functionality and API integration
├── server.py           # Simple HTTP server for development
├── run.bat            # Windows batch file to start server
├── run.sh             # Unix/Linux shell script to start server
└── assets/            # Static assets (if any)
```

## 🚀 Quick Start

### Prerequisites
- Python 3.7+ installed
- Your RiskIQ backend API running on `http://localhost:8000`

### 1. Start the Backend API
First, make sure your backend is running:

```bash
# Navigate to your project root
cd E:\MyQuantProjects\Project_2_RiskIQ

# Activate virtual environment (if using one)
backend\venv\Scripts\activate

# Start the FastAPI backend
uvicorn backend.api.app:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Start the Frontend Server

#### Option A: Using Python (Recommended)
```bash
# Navigate to frontend directory
cd frontend

# Start the server
python server.py
```

#### Option B: Using Batch File (Windows)
```bash
# Double-click run.bat or run from command line
frontend\run.bat
```

#### Option C: Using Shell Script (Unix/Linux/Mac)
```bash
# Make executable and run
chmod +x frontend/run.sh
./frontend/run.sh
```

### 3. Access the Application
Open your browser and navigate to: `http://localhost:3000`

The application will automatically open in your default browser.

## 📖 How to Use

### Single Stock Analysis
1. Click on the "Single Stock Analysis" tab
2. Enter a stock ticker symbol (e.g., AAPL, MSFT, TSLA)
3. Click "Analyze Risk" or press Enter
4. View the comprehensive risk analysis including:
   - Risk level classification
   - Historical volatility metrics
   - VaR and CVaR calculations
   - Volatility forecasts from multiple models
   - Interactive price and returns chart
   - AI-generated risk summary

### Portfolio Analysis
1. Click on the "Portfolio Analysis" tab
2. Enter multiple stock tickers separated by commas (e.g., AAPL, MSFT, GOOGL, TSLA)
3. Click "Analyze Portfolio" or press Ctrl+Enter
4. View the portfolio analysis including:
   - Overall portfolio risk assessment
   - Portfolio summary statistics
   - Individual stock breakdown
   - Risk distribution chart
   - AI-powered portfolio recommendations

## 🎨 Customization

### API Configuration
To change the backend API URL, edit the `API_BASE_URL` variable in `script.js`:

```javascript
const API_BASE_URL = 'http://your-backend-url:port';
```

### Styling
The application uses CSS custom properties and modern styling. You can customize:
- Color schemes in `styles.css`
- Layout and spacing
- Typography and fonts
- Animation effects

### Features
- Add new chart types in `script.js`
- Modify risk level thresholds
- Customize AI summary prompts
- Add new metrics or visualizations

## 🔧 Development

### Adding New Features
1. **New API Endpoints**: Update the JavaScript API calls in `script.js`
2. **New UI Components**: Add HTML structure and CSS styling
3. **New Charts**: Extend the Chart.js configuration
4. **New Metrics**: Update the display functions

### Debugging
- Open browser developer tools (F12)
- Check the Console tab for JavaScript errors
- Check the Network tab for API call issues
- Verify backend API is running and accessible

## 🐛 Troubleshooting

### Common Issues

1. **"Failed to analyze" errors**
   - Ensure backend API is running on `http://localhost:8000`
   - Check if the stock ticker is valid
   - Verify CORS is enabled in your backend

2. **Charts not displaying**
   - Check browser console for JavaScript errors
   - Ensure Chart.js is loaded properly
   - Verify data format from API

3. **Styling issues**
   - Clear browser cache
   - Check CSS file is loaded
   - Verify responsive design breakpoints

4. **Port conflicts**
   - Change the PORT variable in `server.py` if 3000 is occupied
   - Update the frontend URL accordingly

### Backend API Requirements
Your backend should have these endpoints:
- `GET /risk/{ticker}` - Single stock analysis
- `POST /portfolio_risk` - Portfolio analysis
- CORS headers enabled for `http://localhost:3000`

## 📱 Mobile Support

The application is fully responsive and works on:
- Desktop computers (1200px+)
- Tablets (768px - 1199px)
- Mobile phones (320px - 767px)

## 🔒 Security Notes

- This is a development server, not production-ready
- For production deployment, use a proper web server (nginx, Apache)
- Implement proper authentication and authorization
- Add HTTPS support
- Validate and sanitize all inputs

## 🚀 Deployment

### Production Deployment
1. **Build for Production**: Minify CSS/JS, optimize images
2. **Web Server**: Use nginx or Apache to serve static files
3. **Backend**: Deploy FastAPI with proper WSGI server (Gunicorn)
4. **Database**: Set up persistent storage for models
5. **Security**: Implement authentication, HTTPS, and input validation

### Docker Deployment
Create a `Dockerfile` for containerized deployment:

```dockerfile
FROM nginx:alpine
COPY frontend/ /usr/share/nginx/html/
EXPOSE 80
```

## 📄 License

This web application is part of your RiskIQ project. Please refer to your main project license.

## 🤝 Contributing

To contribute to this webapp:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review browser console for errors
3. Verify backend API functionality
4. Check network connectivity

---

**Happy Risk Analyzing! 📊📈**
