# 🚀 Deployment Guide

This guide covers how to deploy the Stock Market Prediction project on various platforms.

## 📋 Prerequisites

1. **Python 3.8+** installed on your system
2. **PostgreSQL** database (local or cloud)
3. **Git** for version control
4. **Streamlit Cloud** account (for dashboard deployment)

## 🗄️ Database Setup

### Local PostgreSQL Setup

1. **Install PostgreSQL**:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install postgresql postgresql-contrib
   
   # macOS
   brew install postgresql
   
   # Windows
   # Download from https://www.postgresql.org/download/windows/
   ```

2. **Create Database**:
   ```bash
   sudo -u postgres psql
   CREATE DATABASE stock_market_db;
   CREATE USER stock_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE stock_market_db TO stock_user;
   \q
   ```

3. **Update Configuration**:
   Create a `.env` file in the project root:
   ```
   DATABASE_URL=postgresql://stock_user:your_password@localhost:5432/stock_market_db
   ```

### Cloud Database Options

#### Heroku Postgres
1. Create a Heroku account
2. Install Heroku CLI
3. Create a new app and add Postgres:
   ```bash
   heroku create your-app-name
   heroku addons:create heroku-postgresql:hobby-dev
   heroku config:get DATABASE_URL
   ```

#### AWS RDS
1. Create an RDS PostgreSQL instance
2. Configure security groups
3. Update connection string in `.env`

## 🐍 Local Development Setup

1. **Clone Repository**:
   ```bash
   git clone <your-repo-url>
   cd stock-market-project
   ```

2. **Create Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Download NLTK Data**:
   ```python
   import nltk
   nltk.download('vader_lexicon')
   ```

5. **Run Data Collection**:
   ```bash
   # Collect stock data
   python data/stock_data_collector.py --symbol AAPL --start_date 2020-01-01
   
   # Collect news data
   python data/news_data_collector.py --symbol AAPL
   
   # Clean and engineer features
   python data/data_cleaner.py --symbol AAPL
   ```

6. **Train Models**:
   ```bash
   # Train ARIMA model
   python models/arima_forecaster.py --symbol AAPL
   
   # Analyze sentiment
   python models/sentiment_analyzer.py --symbol AAPL
   
   # Train Random Forest
   python models/random_forest_predictor.py --symbol AAPL
   ```

7. **Run Dashboard**:
   ```bash
   streamlit run dashboard/app.py
   ```

## ☁️ Streamlit Cloud Deployment

### Step 1: Prepare Repository

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Create Streamlit Secrets**:
   Create a `.streamlit/secrets.toml` file:
   ```toml
   [database]
   url = "postgresql://username:password@host:port/database"
   ```

### Step 2: Deploy on Streamlit Cloud

1. **Go to Streamlit Cloud**: https://share.streamlit.io/
2. **Sign in with GitHub**
3. **Connect Repository**:
   - Click "New app"
   - Select your repository
   - Set the path to `dashboard/app.py`
   - Click "Deploy"

### Step 3: Configure Environment

1. **Add Secrets**:
   - Go to your app settings
   - Add database connection string
   - Add any API keys if needed

2. **Set Environment Variables**:
   ```bash
   # In Streamlit Cloud settings
   DATABASE_URL=your_database_url
   ```

## 🐳 Docker Deployment

### Create Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Download NLTK data
RUN python -c "import nltk; nltk.download('vader_lexicon')"

# Expose port
EXPOSE 8501

# Run the application
CMD ["streamlit", "run", "dashboard/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Create docker-compose.yml

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8501:8501"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/stock_market_db
    depends_on:
      - db
    volumes:
      - .:/app

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=stock_market_db
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Run with Docker

```bash
# Build and run
docker-compose up --build

# Or run individual containers
docker build -t stock-predictor .
docker run -p 8501:8501 stock-predictor
```

## 🔧 Environment Configuration

### Required Environment Variables

```bash
# Database
DATABASE_URL=postgresql://username:password@host:port/database

# Optional: API Keys (if using paid services)
ALPHA_VANTAGE_API_KEY=your_key_here
NEWS_API_KEY=your_key_here
```

### Configuration Files

1. **`.env`** (for local development):
   ```
   DATABASE_URL=postgresql://localhost:5432/stock_market_db
   LOG_LEVEL=INFO
   ```

2. **`.streamlit/secrets.toml`** (for Streamlit Cloud):
   ```toml
   [database]
   url = "postgresql://username:password@host:port/database"
   ```

## 🧪 Testing

### Run All Tests
```bash
pytest tests/
```

### Run Specific Test Categories
```bash
# Data collection tests
pytest tests/test_data_collection.py

# Model tests
pytest tests/test_models.py

# Cleaning tests
pytest tests/test_cleaning.py
```

### Test Coverage
```bash
pip install pytest-cov
pytest --cov=. --cov-report=html tests/
```

## 📊 Monitoring and Logging

### Application Logs
- Logs are automatically generated in the application
- Check console output for real-time logs
- Log files are created in the `logs/` directory

### Database Monitoring
```sql
-- Check table sizes
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Check recent predictions
SELECT * FROM predictions ORDER BY date DESC LIMIT 10;
```

## 🔒 Security Considerations

1. **Database Security**:
   - Use strong passwords
   - Enable SSL connections
   - Restrict database access

2. **API Security**:
   - Store API keys in environment variables
   - Use HTTPS for all connections
   - Implement rate limiting

3. **Application Security**:
   - Keep dependencies updated
   - Use virtual environments
   - Implement input validation

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection Error**:
   ```bash
   # Check if PostgreSQL is running
   sudo systemctl status postgresql
   
   # Test connection
   psql -h localhost -U username -d stock_market_db
   ```

2. **NLTK Data Missing**:
   ```python
   import nltk
   nltk.download('vader_lexicon')
   ```

3. **Streamlit Deployment Issues**:
   - Check secrets configuration
   - Verify database connectivity
   - Review application logs

### Performance Optimization

1. **Database Indexing**:
   ```sql
   CREATE INDEX idx_stocks_symbol_date ON stocks(symbol, date);
   CREATE INDEX idx_news_symbol_date ON news(symbol, date);
   ```

2. **Caching**:
   - Implement Redis for caching
   - Cache frequently accessed data
   - Use Streamlit's caching decorators

## 📈 Scaling Considerations

1. **Database Scaling**:
   - Use read replicas
   - Implement connection pooling
   - Consider database sharding

2. **Application Scaling**:
   - Use load balancers
   - Implement horizontal scaling
   - Use container orchestration (Kubernetes)

3. **Data Pipeline Scaling**:
   - Use message queues (Celery, Redis)
   - Implement batch processing
   - Use cloud data warehouses

## 📞 Support

For deployment issues:
1. Check the logs for error messages
2. Verify all environment variables are set
3. Test database connectivity
4. Review the troubleshooting section above

For additional help, create an issue in the project repository. 