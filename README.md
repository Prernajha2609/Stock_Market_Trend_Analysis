# 📈 Stock Market Prediction Project

A comprehensive stock market analysis and prediction system that combines historical price data, news sentiment analysis, and machine learning to forecast stock price movements.

## 🚀 Features

- **Data Collection**: Automated collection of historical stock prices and news headlines
- **Data Processing**: Cleaning, feature engineering, and sentiment analysis
- **Machine Learning**: ARIMA time series forecasting and Random Forest classification
- **Interactive Dashboard**: Streamlit web application with real-time data visualization
- **Database Integration**: PostgreSQL storage for all data and predictions

## 📁 Project Structure

```
stock-market-project/
├── data/
│   ├── stock_data_collector.py
│   ├── news_data_collector.py
│   └── data_cleaner.py
├── models/
│   ├── arima_forecaster.py
│   ├── sentiment_analyzer.py
│   └── random_forest_predictor.py
├── dashboard/
│   └── app.py
├── tests/
│   ├── test_data_collection.py
│   ├── test_models.py
│   └── test_cleaning.py
├── requirements.txt
├── .gitignore
└── README.md
```

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd stock-market-project
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up PostgreSQL database**
   - Install PostgreSQL on your system
   - Create a new database for the project
   - Update the database connection string in the configuration

5. **Download NLTK data**
   ```python
   import nltk
   nltk.download('vader_lexicon')
   ```

## 🗄️ Database Setup

1. **Install PostgreSQL** (if not already installed)
2. **Create database and tables**:
   ```sql
   CREATE DATABASE stock_market_db;
   ```

The application will automatically create the required tables when first run.

## 📊 Usage

### 1. Data Collection

Collect historical stock data:
```bash
python data/stock_data_collector.py --symbol AAPL --start_date 2020-01-01
```

Collect news headlines:
```bash
python data/news_data_collector.py --symbol AAPL
```

### 2. Data Processing

Clean and engineer features:
```bash
python data/data_cleaner.py --symbol AAPL
```

### 3. Model Training

Train ARIMA model:
```bash
python models/arima_forecaster.py --symbol AAPL
```

Analyze sentiment:
```bash
python models/sentiment_analyzer.py
```

Train Random Forest model:
```bash
python models/random_forest_predictor.py --symbol AAPL
```

### 4. Interactive Dashboard

Launch the Streamlit dashboard:
```bash
streamlit run dashboard/app.py
```

## 🧪 Testing

Run all tests:
```bash
pytest tests/
```

Run specific test files:
```bash
pytest tests/test_data_collection.py
pytest tests/test_models.py
```

## 📈 Dashboard Features

- **Stock Symbol Input**: Enter any stock symbol to analyze
- **Historical Data Visualization**: Interactive charts with moving averages
- **Price Predictions**: 30-day forecast with confidence intervals
- **News Sentiment**: Recent headlines with sentiment scores
- **Model Performance**: Accuracy metrics and feature importance

## 🚀 Deployment

### Streamlit Cloud Deployment

1. **Push your code to GitHub**
2. **Connect to Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository
   - Deploy the `dashboard/app.py` file

3. **Environment Variables**:
   - Set database connection string in Streamlit Cloud secrets
   - Configure any API keys if needed

## 📋 Configuration

Create a `.env` file in the project root:
```
DATABASE_URL=postgresql://username:password@localhost:5432/stock_market_db
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This project is for educational purposes only. Stock market predictions are inherently uncertain and should not be used as the sole basis for investment decisions. Always conduct thorough research and consult with financial advisors before making investment decisions.

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Error**:
   - Ensure PostgreSQL is running
   - Check database credentials in `.env` file
   - Verify database exists

2. **NLTK Data Missing**:
   ```python
   import nltk
   nltk.download('vader_lexicon')
   ```

3. **YFinance API Issues**:
   - Check internet connection
   - Verify stock symbol is valid
   - Try again later if rate limited

## 📞 Support

For issues and questions, please open an issue on GitHub or contact the development team. 