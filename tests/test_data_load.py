import pandas as pd

# Load data
df = pd.read_csv('data/banknifty_daily_10y.csv')
df['Date'] = pd.to_datetime(df['Date'])

print("="*70)
print("DATA VERIFICATION")
print("="*70)

print(f"\nTotal rows: {len(df)}")
print(f"Date type: {df['Date'].dtype}")
print(f"First date: {df['Date'].iloc[0]}")
print(f"Last date: {df['Date'].iloc[-1]}")

print("\nFirst 10 rows:")
print(df.head(10))

print("\nData types:")
print(df.dtypes)

# Check if Date column is actually datetime
if df['Date'].dtype == 'datetime64[ns]':
    print("\n✓✓✓ Date column is properly formatted!")
else:
    print("\n✗ Date column has wrong type!")

# Check for reasonable prices
if df['Close'].min() > 1000 and df['Close'].max() < 100000:
    print("✓ Price range is reasonable (1,000 - 100,000)")
else:
    print("⚠ Price range looks unusual")

print("\n" + "="*70)
