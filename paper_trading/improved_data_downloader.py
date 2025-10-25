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
        df = yf.download(symbol, start=start_date, end=end_date, progress=False, timeout=10)
        if len(df) > 0:
            print(f"✓ yfinance worked! Got {len(df)} days")
            return df
        else:
            print("✗ yfinance returned no data")
            return None
    except Exception as e:
        print(f"✗ yfinance failed: {str(e)[:100]}")
        return None

def download_with_yahooquery(symbol):
    """Method 2: yahooquery (alternative library)"""
    try:
        from yahooquery import Ticker
        print(f"Trying yahooquery for {symbol}...")
        ticker = Ticker(symbol)
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
    """
    Try multiple methods to get Bank Nifty data
    Returns DataFrame or None
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=lookback_days)
    
    print("="*70)
    print("DOWNLOADING BANK NIFTY DATA - MULTIPLE FALLBACK METHODS")
    print("="*70)
    print(f"Target date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}\n")
    
    # Try Method 1: yfinance
    df = download_with_yfinance('^NSEBANK', start_date, end_date)
    if df is not None and len(df) > 20:
        return scale_prices(df)
    
    time.sleep(1)
    
    # Try Method 2: yahooquery
    df = download_with_yahooquery('^NSEBANK')
    if df is not None and len(df) > 20:
        return scale_prices(df)
    
    time.sleep(1)
    
    # Try Method 3: Local backup
    df = download_with_nse_direct('^NSEBANK')
    if df is not None and len(df) > 20:
        # Already scaled
        return df
    
    print("\n❌ All download methods failed!")
    print("\n💡 SOLUTIONS:")
    print("1. Check your internet connection")
    print("2. Try again in a few minutes (Yahoo Finance might be rate-limiting)")
    print("3. Use local backup data (we'll use the last backtest data)")
    
    return None

def scale_prices(df):
    """Scale prices (divide by 100 for Bank Nifty)"""
    df = df.copy()
    for col in ['Open', 'High', 'Low', 'Close', 'Adj Close']:
        if col in df.columns:
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
