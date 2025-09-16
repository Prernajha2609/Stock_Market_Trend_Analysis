
import logging
from sqlalchemy import create_engine, text, MetaData, Table, Column, String, Date, Float, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pandas as pd
from config import SQLALCHEMY_DATABASE_URI
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# Create SQLAlchemy engine
engine = create_engine(SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)
Base = declarative_base()
class Stocks(Base):
    """Stock price data table."""
    __tablename__ = 'stocks'
    id = Column(Integer, primary_key=True)
    symbol = Column(String(10), nullable=False)
    date = Column(Date, nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Integer, nullable=False)
class News(Base):
    """News headlines table."""
    __tablename__ = 'news'
    id = Column(Integer, primary_key=True)
    symbol = Column(String(10), nullable=False)
    date = Column(Date, nullable=False)
    headline = Column(String(500), nullable=False)
    link = Column(String(500), nullable=False)
    source = Column(String(100), nullable=False)
    sentiment_score = Column(Float, nullable=True)
class StocksClean(Base):
    """Cleaned and feature-engineered stock data table."""
    __tablename__ = 'stocks_clean'
    id = Column(Integer, primary_key=True)
    symbol = Column(String(10), nullable=False)
    date = Column(Date, nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Integer, nullable=False)
    ma_5 = Column(Float, nullable=True)
    ma_10 = Column(Float, nullable=True)
    ma_20 = Column(Float, nullable=True)
    daily_return = Column(Float, nullable=True)
class Predictions(Base):
    """Model predictions table."""
    __tablename__ = 'predictions'
    id = Column(Integer, primary_key=True)
    symbol = Column(String(10), nullable=False)
    date = Column(Date, nullable=False)
    predicted_price = Column(Float, nullable=False)
    confidence_lower = Column(Float, nullable=True)
    confidence_upper = Column(Float, nullable=True)
    model_type = Column(String(50), nullable=False)
class ModelMetrics(Base):
    """Model performance metrics table."""
    __tablename__ = 'model_metrics'
    id = Column(Integer, primary_key=True)
    symbol = Column(String(10), nullable=False)
    model_type = Column(String(50), nullable=False)
    accuracy = Column(Float, nullable=False)
    precision = Column(Float, nullable=False)
    recall = Column(Float, nullable=False)
    f1_score = Column(Float, nullable=False)
    created_at = Column(Date, nullable=False)
def create_tables():
    """Create all database tables if they don't exist."""
    try:
        Base.metadata.create_all(engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        raise
def get_session():
    """Get a database session."""
    return Session()
def close_session(session):
    """Close a database session."""
    session.close()
def execute_query(query, params=None):
    """Execute a raw SQL query."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text(query), params or {})
            return result
    except Exception as e:
        logger.error(f"Error executing query: {e}")
        raise
def insert_dataframe(df, table_name):
    """Insert a pandas DataFrame into a database table."""
    try:
        df.to_sql(table_name, engine, if_exists='append', index=False)
        logger.info(f"Successfully inserted {len(df)} rows into {table_name}")
    except Exception as e:
        logger.error(f"Error inserting data into {table_name}: {e}")
        raise
def read_dataframe(query, params=None):
    """Read data from database into a pandas DataFrame."""
    try:
        df = pd.read_sql_query(query, engine, params=params)
        return df
    except Exception as e:
        logger.error(f"Error reading data: {e}")
        raise
def table_exists(table_name):
    """Check if a table exists in the database."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = :table_name)"
            ), {"table_name": table_name})
            return result.scalar()
    except Exception as e:
        logger.error(f"Error checking if table exists: {e}")
        return False 