"""
Improved Data Downloader - Multiple Fallback Sources
Tries yfinance, yahooquery, and manual NSE data
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import requests
import time

def download_with_yfinance(symbol, start_date, end_date):
    """Method 1: yfinance (fastest when working)"""
    try:
        print(f"Trying yfinance for {symbol}...")
        df = yf.download(symbol, start=start_date, end=end_date, progress=False, timeout=10, auto_adjust=True)
        
        if len(df) > 0:
            # Handle multi-index columns (happens on GitHub Actions)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.droplevel(1)  # Remove ticker level
            
            # Ensure columns are strings not tuples
            df.columns = [str(col).strip() for col in df.columns]
            
            # Rename to standard format
            df = df.rename(columns={
                'Open': 'Open',
                'High': 'High',
                'Low': 'Low',
                'Close': 'Close',
                'Volume': 'Volume',
                'Adj Close': 'Adj Close'
            })
            
            # Add Adj Close if missing
            if 'Adj Close' not in df.columns and 'Close' in df.columns:
                df['Adj Close'] = df['Close']
            
            print(f"✓ yfinance worked! Got {len(df)} days")
            return df
        else:
            print("✗ yfinance returned no data")
            return None
    except Exception as e:
        print(f"✗ yfinance failed: {str(e)[:100]}")
        return None

def download_with_yahooquery(symbol):
    """Method 1: yahooquery (alternative library)"""
    try:
        from yahooquery import Ticker
        print(f"Trying yahooquery for {symbol}...")
        ticker = Ticker(symbol)
        
        # Request 1 year of data to ensure we have enough
        df = ticker.history(period='1y')
        
        if df is not None and len(df) > 0:
            # Reshape if multi-index
            if isinstance(df.index, pd.MultiIndex):
                df = df.reset_index(level=0, drop=True)
            
            # FIX: Ensure index is datetime, not date
            if not isinstance(df.index, pd.DatetimeIndex):
                df.index = pd.to_datetime(df.index)
            
            # Rename columns to match yfinance
            df = df.rename(columns={
                'open': 'Open',
                'high': 'High', 
                'low': 'Low',
                'close': 'Close',
                'volume': 'Volume'
            })
            
            # Ensure all required columns exist
            for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
                if col not in df.columns:
                    print(f"✗ yahooquery missing column: {col}")
                    return None
            
            df['Adj Close'] = df['Close']
            print(f"✓ yahooquery worked! Got {len(df)} days")
            return df
        else:
            print("✗ yahooquery returned no data")
            return None
    except ImportError:
        print("✗ yahooquery not installed")
        return None
    except Exception as e:
        print(f"✗ yahooquery failed: {str(e)[:100]}")
        return None


def download_with_nse_direct(symbol):
    """Method 3: Direct from NSE (Bank Nifty only)"""
    try:
        print(f"Trying direct NSE download...")
        # Use saved historical data as backup
        backup_file = '../data/banknifty_scaled_backtest.csv'
        df = pd.read_csv(backup_file)
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.set_index('Date')
        
        # Get last 90 days
        df = df.tail(90)
        
        # Add Adj Close column
        df['Adj Close'] = df['Close']
        
        print(f"✓ Using local backup data! Got {len(df)} days")
        return df
    except Exception as e:
        print(f"✗ NSE direct failed: {str(e)[:100]}")
        return None

def get_bank_nifty_data(lookback_days=90):
    """Try multiple methods to get Bank Nifty data"""
    
    # REQUEST MORE DAYS to account for holidays/weekends
    actual_days = lookback_days + 60  # Add buffer for 60-day MA calculation
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=actual_days)
    
    print("="*70)
    print("DOWNLOADING BANK NIFTY DATA - MULTIPLE FALLBACK METHODS")
    print("="*70)
    print(f"Target date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}\n")
    
    # Try Method 1: yahooquery (more reliable on GitHub)
    df = download_with_yahooquery('^NSEBANK')
    if df is not None and len(df) > 60:  # Need at least 60 days for MA
        return scale_prices(df)
    
    time.sleep(1)
    
    # Try Method 2: yfinance
    df = download_with_yfinance('^NSEBANK', start_date, end_date)
    if df is not None and len(df) > 60:
        return scale_prices(df)
    
    time.sleep(1)
    
    # Try Method 3: Local backup
    df = download_with_nse_direct('^NSEBANK')
    if df is not None and len(df) > 60:
        return df  # Already scaled
    
    print("\n❌ All download methods failed!")
    return None

def scale_prices(df):
    """Scale prices (divide by 100 for Bank Nifty)"""
    df = df.copy()
    
    # Handle both string and tuple column names
    columns_to_scale = []
    for col in df.columns:
        col_str = str(col).strip()
        if any(x in col_str for x in ['Open', 'High', 'Low', 'Close', 'Adj Close']):
            columns_to_scale.append(col)
    
    for col in columns_to_scale:
        df[col] = df[col] / 100
    
    return df


if __name__ == "__main__":
    # Test the downloader
    df = get_bank_nifty_data(90)
    
    if df is not None:
        print("\n✓ SUCCESS! Data downloaded:")
        print(f"  Rows: {len(df)}")
        print(f"  Date range: {df.index[0]} to {df.index[-1]}")
        print(f"  Latest close: ₹{df['Close'].iloc[-1]:.2f}")
        print(f"\nFirst few rows:")
        print(df.head())
    else:
        print("\n❌ Could not get data from any source")
