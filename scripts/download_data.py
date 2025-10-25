from yahooquery import Ticker
import pandas as pd
from datetime import datetime
import os

print("="*70)
print("DOWNLOADING BANK NIFTY HISTORICAL DATA (FIXED VERSION)")
print("="*70)

ticker_symbol = "^NSEBANK"
print(f"\nTicker: {ticker_symbol}")
print("Fetching 10 years of daily data... This may take 30-60 seconds.\n")

# Ensure output folder exists
os.makedirs('../data', exist_ok=True)

try:
    ticker = Ticker(ticker_symbol)
    
    # Fetch historical data using period (more reliable than date range)
    print("Downloading data...")
    data = ticker.history(period='10y', interval='1d')
    
    if isinstance(data, pd.DataFrame) and not data.empty:
        
        # CRITICAL FIX: yahooquery returns multi-index with symbol
        if isinstance(data.index, pd.MultiIndex):
            data = data.reset_index()
            if 'date' in data.columns:
                data = data.rename(columns={'date': 'Date'})
            if 'symbol' in data.columns:
                data = data.drop('symbol', axis=1)
        else:
            data = data.reset_index()
            if 'date' in data.columns:
                data = data.rename(columns={'date': 'Date'})
            elif 'index' in data.columns:
                data = data.rename(columns={'index': 'Date'})
        
        # Standardize column names
        column_mapping = {
            'open': 'Open',
            'high': 'High',
            'low': 'Low',
            'close': 'Close',
            'volume': 'Volume',
            'adjclose': 'Adj Close'
        }
        data = data.rename(columns=column_mapping)
        
        # Keep only essential columns
        essential_cols = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
        available_cols = [col for col in essential_cols if col in data.columns]
        data = data[available_cols]
        
        # Convert Date to datetime (tz-naive)
        if 'Date' in data.columns:
            data['Date'] = pd.to_datetime(data['Date'], utc=True).dt.tz_convert(None)
        
        # Sort by date
        data = data.sort_values('Date')
        
        # Remove rows with zero or NaN volume
        if 'Volume' in data.columns:
            print(f"Before filtering: {len(data)} rows")
            data = data[data['Volume'] > 0]
            print(f"After filtering zero volumes: {len(data)} rows")
        
        # Drop remaining rows with missing critical data
        data = data.dropna(subset=['Date', 'Close'])
        
        # Display summary
        print("\n" + "="*70)
        print("DOWNLOAD SUCCESSFUL!")
        print("="*70)
        
        print(f"\nTotal trading days: {len(data)}")
        
        if len(data) > 0:
            print(f"Date range: {data['Date'].min().strftime('%Y-%m-%d')} to {data['Date'].max().strftime('%Y-%m-%d')}")
            
            print("\n--- First 5 Days ---")
            print(data.head().to_string(index=False))
            
            print("\n--- Last 5 Days ---")
            print(data.tail().to_string(index=False))
            
            # Data quality checks
            print("\n" + "="*70)
            print("DATA QUALITY CHECKS")
            print("="*70)
            
            missing_values = data.isnull().sum().sum()
            zero_volumes = (data['Volume'] == 0).sum() if 'Volume' in data.columns else 0
            negative_prices = (data['Close'] < 0).sum() if 'Close' in data.columns else 0
            duplicate_dates = data['Date'].duplicated().sum()
            
            print(f"Missing values: {missing_values}")
            print(f"Zero volume days: {zero_volumes}")
            print(f"Negative prices: {negative_prices}")
            print(f"Duplicate dates: {duplicate_dates}")
            
            # Price statistics
            if 'Close' in data.columns:
                print(f"\nPrice Statistics:")
                print(f"  Highest Close: ₹{data['Close'].max():,.2f}")
                print(f"  Lowest Close: ₹{data['Close'].min():,.2f}")
                print(f"  Average Close: ₹{data['Close'].mean():,.2f}")
                print(f"  Latest Close: ₹{data['Close'].iloc[-1]:,.2f}")
            
            # Save to CSV
            output_file = '../data/banknifty_daily_10y.csv'
            data.to_csv(output_file, index=False)
            print(f"\n✓ Data saved to: {output_file}")
            print(f"  File size: ~{len(data) * 100 / 1024:.1f} KB")
            
            # Quality verdict
            if missing_values == 0 and zero_volumes == 0 and negative_prices == 0 and duplicate_dates == 0:
                print("\n✓✓✓ DATA QUALITY: EXCELLENT - Ready for backtesting!")
            else:
                print("\n⚠ DATA QUALITY: Review issues above")
                if zero_volumes > 0:
                    print("  Note: Zero volume days have been filtered out")
            
            print("\n" + "="*70)
        else:
            print("\n✗ Error: No data rows after filtering")
    
    else:
        print("\n✗ Error: Could not fetch data or data is empty")
        print("Possible issues:")
        print("1. Yahoo Finance may be temporarily down")
        print("2. Symbol ^NSEBANK may have changed")
        print("3. Internet connection issue")
        print("\nTry alternative: Use ^NSEI (Nifty 50) for testing")

except Exception as e:
    print(f"\n✗ Error occurred: {e}")
    import traceback
    print("\nFull error details:")
    print(traceback.format_exc())
    print("\nTroubleshooting:")
    print("1. Check internet connection")
    print("2. Verify yahooquery: pip3.11 install --upgrade yahooquery")
    print("3. Try alternative symbol: ^NSEI")
