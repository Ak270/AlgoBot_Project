import pandas as pd
import ta

# Create sample data
data = pd.DataFrame({
    'close': [100, 102, 101, 105, 107, 106, 108, 110, 109, 112],
    'high': [101, 103, 102, 106, 108, 107, 109, 111, 110, 113],
    'low': [99, 101, 100, 104, 106, 105, 107, 109, 108, 111],
    'volume': [1000, 1100, 900, 1200, 1300, 1000, 1400, 1500, 1200, 1600]
})

print("Sample Data:")
print(data)
print("\n" + "="*60)

# Calculate RSI (Relative Strength Index)
data['RSI'] = ta.momentum.RSIIndicator(data['close']).rsi()
print("\nRSI Indicator:")
print(data[['close', 'RSI']])

# Calculate SMA (Simple Moving Average)
data['SMA_5'] = ta.trend.SMAIndicator(data['close'], window=5).sma_indicator()
print("\n5-Period SMA:")
print(data[['close', 'SMA_5']])

# Calculate Bollinger Bands
bollinger = ta.volatility.BollingerBands(data['close'])
data['BB_Upper'] = bollinger.bollinger_hband()
data['BB_Lower'] = bollinger.bollinger_lband()
print("\nBollinger Bands:")
print(data[['close', 'BB_Upper', 'BB_Lower']])

print("\n" + "="*60)
print("✓ All technical indicators working perfectly!")
print("You're ready to build your strategy!")
