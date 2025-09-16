"""
Random Forest classifier for stock price prediction.
Combines historical stock features and sentiment scores to predict price movements.
"""
import argparse
import logging
import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.database import create_tables, read_dataframe, insert_dataframe, execute_query
from config import DEFAULT_SYMBOL, TOP_50_TICKERS
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
def load_stock_features(symbol):
    """
    Load stock features and sentiment data from database.
    Args:
        symbol (str): Stock symbol
    Returns:
        pd.DataFrame: Combined stock and sentiment features
    """
    try:
        logger.info(f"Loading stock features for {symbol}")
        # Load cleaned stock data
        stock_query = """
        SELECT date, open, high, low, close, volume, 
               ma_5, ma_10, ma_20, daily_return
        FROM stocks_clean 
        WHERE symbol = %(symbol)s 
        ORDER BY date
        """
        stock_df = read_dataframe(stock_query, {'symbol': symbol})
        if stock_df.empty:
            logger.warning(f"No stock data found for {symbol}")
            return pd.DataFrame()
        # Load sentiment data
        sentiment_query = """
        SELECT date, AVG(sentiment_score) as avg_sentiment,
               COUNT(*) as news_count,
               COUNT(CASE WHEN sentiment_score > 0.1 THEN 1 END) as positive_count,
               COUNT(CASE WHEN sentiment_score < -0.1 THEN 1 END) as negative_count
        FROM news 
        WHERE symbol = %(symbol)s AND sentiment_score IS NOT NULL
        GROUP BY date
        ORDER BY date
        """
        sentiment_df = read_dataframe(sentiment_query, {'symbol': symbol})
        # Merge stock and sentiment data
        if not sentiment_df.empty:
            df = pd.merge(stock_df, sentiment_df, on='date', how='left')
            # Fill missing sentiment values with 0
            sentiment_columns = ['avg_sentiment', 'news_count', 'positive_count', 'negative_count']
            df[sentiment_columns] = df[sentiment_columns].fillna(0)
        else:
            df = stock_df.copy()
            # Add default sentiment columns
            df['avg_sentiment'] = 0
            df['news_count'] = 0
            df['positive_count'] = 0
            df['negative_count'] = 0
        logger.info(f"Loaded {len(df)} records with features for {symbol}")
        return df
    except Exception as e:
        logger.error(f"Error loading stock features for {symbol}: {e}")
        raise
def create_target_variable(df, days_ahead=30):
    """
    Create target variable for price movement prediction.
    Args:
        df (pd.DataFrame): Stock data with features
        days_ahead (int): Number of days ahead to predict
    Returns:
        pd.DataFrame: DataFrame with target variable added
    """
    try:
        logger.info(f"Creating target variable for {days_ahead}-day prediction")
        # Calculate future price (shift backwards)
        df['future_price'] = df['close'].shift(-days_ahead)
        # Calculate price change percentage
        df['price_change_pct'] = ((df['future_price'] - df['close']) / df['close']) * 100
        # Create binary target: 1 if price increases by more than 2%, 0 otherwise
        df['target'] = (df['price_change_pct'] > 2).astype(int)
        # Remove rows with missing target (last few days)
        df = df.dropna(subset=['target'])
        logger.info(f"Target variable created: {df['target'].sum()} positive cases out of {len(df)} total")
        return df
    except Exception as e:
        logger.error(f"Error creating target variable: {e}")
        raise

def prepare_features(df):
    """
    Prepare features for machine learning model.
    Args:
        df (pd.DataFrame): DataFrame with features and target
    Returns:
        tuple: (X_features, y_target, feature_names)
    """
    try:
        logger.info("Preparing features for model training")
        # Select feature columns
        feature_columns = [
            'open', 'high', 'low', 'close', 'volume',
            'ma_5', 'ma_10', 'ma_20', 'daily_return',
            'avg_sentiment', 'news_count', 'positive_count', 'negative_count']
        # Only include columns that exist
        available_features = [col for col in feature_columns if col in df.columns]
        # Prepare feature matrix
        X = df[available_features].values
        y = df['target'].values
        # Remove rows with missing values
        mask = ~np.isnan(X).any(axis=1)
        X = X[mask]
        y = y[mask]
        logger.info(f"Prepared {X.shape[1]} features for {X.shape[0]} samples")
        logger.info(f"Feature names: {available_features}")
        return X, y, available_features
    except Exception as e:
        logger.error(f"Error preparing features: {e}")
        raise

def train_random_forest(X, y, feature_names):
    """
    Train Random Forest classifier.
    Args:
        X (np.array): Feature matrix
        y (np.array): Target variable
        feature_names (list): List of feature names
    Returns:
        tuple: (trained_model, scaler, feature_importance)
    """
    try:
        logger.info("Training Random Forest classifier")
        # Split data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y)
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        # Train Random Forest model
        rf_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1)
        # Train the model
        rf_model.fit(X_train_scaled, y_train)
        # Make predictions
        y_pred = rf_model.predict(X_test_scaled)
        # Calculate accuracy
        accuracy = accuracy_score(y_test, y_pred)
        # Cross-validation score
        cv_scores = cross_val_score(rf_model, X_train_scaled, y_train, cv=5)
        logger.info(f"Model Accuracy: {accuracy:.4f}")
        logger.info(f"Cross-validation scores: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
        # Print classification report
        logger.info("Classification Report:")
        logger.info(classification_report(y_test, y_pred))
        # Get feature importance
        feature_importance = pd.DataFrame({
            'feature': feature_names,
            'importance': rf_model.feature_importances_
        }).sort_values('importance', ascending=False)
        logger.info("Top 5 Most Important Features:")
        for idx, row in feature_importance.head().iterrows():
            logger.info(f"  {row['feature']}: {row['importance']:.4f}")
        return rf_model, scaler, feature_importance
    except Exception as e:
        logger.error(f"Error training Random Forest model: {e}")
        raise

def plot_confusion_matrix(y_true, y_pred, symbol):
    """
    Plot confusion matrix.
    Args:
        y_true (np.array): True labels
        y_pred (np.array): Predicted labels
        symbol (str): Stock symbol
    """
    try:
        cm = confusion_matrix(y_true, y_pred)
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                   xticklabels=['Down', 'Up'],
                   yticklabels=['Down', 'Up'])
        plt.title(f'Confusion Matrix - {symbol} Price Prediction')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        # Save plot
        plot_filename = f'confusion_matrix_{symbol.lower()}.png'
        plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
        plt.close()
        logger.info(f"Confusion matrix saved as {plot_filename}")
    except Exception as e:
        logger.error(f"Error plotting confusion matrix: {e}")

def plot_feature_importance(feature_importance, symbol):
    """
    Plot feature importance.
    Args:
        feature_importance (pd.DataFrame): Feature importance data
        symbol (str): Stock symbol
    """
    try:
        plt.figure(figsize=(10, 6))
        # Plot top 10 features
        top_features = feature_importance.head(10)
        plt.barh(range(len(top_features)), top_features['importance'])
        plt.yticks(range(len(top_features)), top_features['feature'])
        plt.xlabel('Feature Importance')
        plt.title(f'Feature Importance - {symbol} Price Prediction')
        plt.gca().invert_yaxis()
        # Save plot
        plot_filename = f'feature_importance_{symbol.lower()}.png'
        plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
        plt.close()
        logger.info(f"Feature importance plot saved as {plot_filename}")
    except Exception as e:
        logger.error(f"Error plotting feature importance: {e}")

def save_model_results(model, scaler, feature_importance, symbol, y_test, y_pred):
    """
    Save model results and predictions to database.
    Args:
        model: Trained Random Forest model
        scaler: Fitted StandardScaler
        feature_importance (pd.DataFrame): Feature importance data
        symbol (str): Stock symbol
        y_test: Test set true labels
        y_pred: Test set predicted labels
    """
    try:
        logger.info("Saving model results to database")
        # Calculate metrics
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average='weighted')
        recall = recall_score(y_test, y_pred, average='weighted')
        f1 = f1_score(y_test, y_pred, average='weighted')
        # Save accuracy metrics
        query = """
        INSERT INTO model_metrics (symbol, model_type, accuracy, `precision`, recall, f1_score, created_at)
        VALUES (:symbol, 'RandomForest', :accuracy, :precision, :recall, :f1_score, :created_at)
        """
        execute_query(query, {
            'symbol': symbol,
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'created_at': datetime.now().date()})
        logger.info(f"Saved accuracy metrics for {symbol}: Accuracy={accuracy:.4f}, Precision={precision:.4f}, Recall={recall:.4f}, F1={f1:.4f}")
        # Save feature importance
        for idx, row in feature_importance.iterrows():
            query = """
            INSERT INTO feature_importance (symbol, date, feature, importance, model_type)
            VALUES (:symbol, :date, :feature, :importance, 'RandomForest')
            """
            execute_query(query, {
                'symbol': symbol,
                'date': datetime.now().date(),
                'feature': row['feature'],
                'importance': row['importance']
            })
        logger.info(f"Saved feature importance for {symbol}")
    except Exception as e:
        logger.error(f"Error saving model results: {e}")
        raise

def main():
    """Main function to train Random Forest model for price prediction."""
    parser = argparse.ArgumentParser(description='Train Random Forest model for stock price prediction')
    parser.add_argument('--symbol', type=str, default=DEFAULT_SYMBOL,
                       help=f'Stock symbol (default: {DEFAULT_SYMBOL})')
    parser.add_argument('--days_ahead', type=int, default=30,
                       help='Number of days ahead to predict (default: 30)')
    parser.add_argument('--all', action='store_true',
                       help='Train Random Forest model for all tickers in TOP_50_TICKERS')
    parser.add_argument('--symbols', type=str, default=None,
                       help='Comma-separated list of stock symbols to process')
    args = parser.parse_args()
    if args.all:
        tickers = TOP_50_TICKERS
    elif args.symbols:
        tickers = [s.strip().upper() for s in args.symbols.split(',') if s.strip()]
    else:
        tickers = [args.symbol.upper()]
    try:
        # Create database tables if they don't exist
        create_tables()
        for symbol in tickers:
            # Load stock features
            df = load_stock_features(symbol)
            if df.empty:
                logger.error(f"No data available for {symbol}")
                continue
            # Create target variable
            df = create_target_variable(df, args.days_ahead)
            if df.empty:
                logger.error(f"No data available for prediction after creating target variable for {symbol}")
                continue
            # Prepare features
            X, y, feature_names = prepare_features(df)
            if len(X) == 0:
                logger.error(f"No valid features available for training for {symbol}")
                continue
            # Train Random Forest model
            model, scaler, feature_importance = train_random_forest(X, y, feature_names)
            # Make predictions on test set
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y)
            X_test_scaled = scaler.transform(X_test)
            y_pred = model.predict(X_test_scaled)
            # Plot results
            plot_confusion_matrix(y_test, y_pred, symbol)
            plot_feature_importance(feature_importance, symbol)
            # Save model results
            save_model_results(model, scaler, feature_importance, symbol, y_test, y_pred)
            logger.info(f"Random Forest training and evaluation completed for {symbol}")
    except Exception as e:
        logger.error(f"Error in main function: {e}")
        sys.exit(1)
if __name__ == "__main__":
    main() 