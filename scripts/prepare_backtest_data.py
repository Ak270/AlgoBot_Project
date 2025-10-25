"""
Scale Bank Nifty data for backtesting with small capital
"""
import pandas as pd

print("="*70)
print("PREPARING SCALED BACKTEST DATA")
print("="*70)

# Load data
df = pd.read_csv('../data/banknifty_daily_10y.csv')
print(f"\n✓ Loaded {len(df)} rows")
print(f"Original price range: ₹{df['Close'].min():,.2f} - ₹{df['Close'].max():,.2f}")

# Scale down by 100x
df['Open'] = df['Open'] / 100
df['High'] = df['High'] / 100
df['Low'] = df['Low'] / 100
df['Close'] = df['Close'] / 100

print(f"\nScaled price range: ₹{df['Close'].min():,.2f} - ₹{df['Close'].max():,.2f}")

# Save
df.to_csv('../data/banknifty_scaled_backtest.csv', index=False)
print(f"\n✓ Saved to: banknifty_scaled_backtest.csv")
print("\nNOTE: Scaling is ONLY for backtesting learning.")
print("In live trading, use Bank Nifty futures with leverage.")
print("="*70)
