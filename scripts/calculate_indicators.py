import pandas as pd
import ta
import matplotlib.pyplot as plt

print("Loading data...")
df = pd.read_csv('../data/banknifty_daily_10y.csv')
df['Date'] = pd.to_datetime(df['Date'])

print("Calculating technical indicators...\n")

# Moving Averages
df['SMA_50'] = ta.trend.SMAIndicator(df['Close'], window=50).sma_indicator()
df['SMA_200'] = ta.trend.SMAIndicator(df['Close'], window=200).sma_indicator()
df['EMA_20'] = ta.trend.EMAIndicator(df['Close'], window=20).ema_indicator()

# RSI (Relative Strength Index)
df['RSI'] = ta.momentum.RSIIndicator(df['Close'], window=14).rsi()

# MACD
macd = ta.trend.MACD(df['Close'])
df['MACD'] = macd.macd()
df['MACD_Signal'] = macd.macd_signal()

# Bollinger Bands
bollinger = ta.volatility.BollingerBands(df['Close'], window=20, window_dev=2)
df['BB_Upper'] = bollinger.bollinger_hband()
df['BB_Middle'] = bollinger.bollinger_mavg()
df['BB_Lower'] = bollinger.bollinger_lband()

# ATR (Average True Range) - For volatility
df['ATR'] = ta.volatility.AverageTrueRange(df['High'], df['Low'], df['Close'], window=14).average_true_range()

print("✓ All indicators calculated")

# Show latest values
print("\n" + "="*70)
print("LATEST INDICATOR VALUES")
print("="*70)
latest = df.iloc[-1]
print(f"\nDate: {latest['Date'].strftime('%Y-%m-%d')}")
print(f"Close: ₹{latest['Close']:,.2f}")
print(f"\nMoving Averages:")
print(f"  20-day EMA: ₹{latest['EMA_20']:,.2f}")
print(f"  50-day SMA: ₹{latest['SMA_50']:,.2f}")
print(f"  200-day SMA: ₹{latest['SMA_200']:,.2f}")
print(f"\nMomentum:")
print(f"  RSI(14): {latest['RSI']:.2f}")
print(f"  MACD: {latest['MACD']:.2f}")
print(f"  MACD Signal: {latest['MACD_Signal']:.2f}")
print(f"\nBollinger Bands:")
print(f"  Upper: ₹{latest['BB_Upper']:,.2f}")
print(f"  Middle: ₹{latest['BB_Middle']:,.2f}")
print(f"  Lower: ₹{latest['BB_Lower']:,.2f}")
print(f"\nVolatility:")
print(f"  ATR(14): ₹{latest['ATR']:.2f}")

# Market Analysis
print("\n" + "="*70)
print("TECHNICAL ANALYSIS")
print("="*70)

# Trend Analysis
if latest['Close'] > latest['SMA_50'] > latest['SMA_200']:
    trend = "🟢 STRONG UPTREND"
elif latest['Close'] > latest['SMA_200']:
    trend = "🟢 UPTREND"
elif latest['Close'] < latest['SMA_50'] < latest['SMA_200']:
    trend = "🔴 STRONG DOWNTREND"
else:
    trend = "🟡 SIDEWAYS/MIXED"

print(f"\nTrend: {trend}")

# RSI Analysis
if latest['RSI'] > 70:
    rsi_signal = "⚠️ OVERBOUGHT (Potential reversal down)"
elif latest['RSI'] < 30:
    rsi_signal = "✓ OVERSOLD (Potential reversal up)"
else:
    rsi_signal = "NEUTRAL (30-70 range)"

print(f"RSI Signal: {rsi_signal}")

# MACD Analysis
if latest['MACD'] > latest['MACD_Signal']:
    macd_signal = "🟢 BULLISH (MACD > Signal)"
else:
    macd_signal = "🔴 BEARISH (MACD < Signal)"

print(f"MACD Signal: {macd_signal}")

# Bollinger Band Analysis
bb_position = ((latest['Close'] - latest['BB_Lower']) / (latest['BB_Upper'] - latest['BB_Lower'])) * 100
print(f"Bollinger Band Position: {bb_position:.1f}% (0%=lower band, 100%=upper band)")

# Create visualization
fig, axes = plt.subplots(4, 1, figsize=(16, 14), height_ratios=[3, 1, 1, 1])

# Use last 500 days for clarity
recent = df.tail(500).copy()

# Chart 1: Price with Moving Averages and Bollinger Bands
axes[0].plot(recent['Date'], recent['Close'], linewidth=2, color='black', label='Close', zorder=5)
axes[0].plot(recent['Date'], recent['SMA_50'], linewidth=1.5, color='blue', 
            label='50-day SMA', alpha=0.7)
axes[0].plot(recent['Date'], recent['SMA_200'], linewidth=1.5, color='red', 
            label='200-day SMA', alpha=0.7)
axes[0].plot(recent['Date'], recent['EMA_20'], linewidth=1.5, color='green', 
            label='20-day EMA', alpha=0.7, linestyle='--')

# Bollinger Bands
axes[0].plot(recent['Date'], recent['BB_Upper'], linewidth=1, color='gray', 
            linestyle='--', alpha=0.5)
axes[0].plot(recent['Date'], recent['BB_Lower'], linewidth=1, color='gray', 
            linestyle='--', alpha=0.5)
axes[0].fill_between(recent['Date'], recent['BB_Upper'], recent['BB_Lower'], 
                     alpha=0.1, color='gray', label='Bollinger Bands')

axes[0].set_title('Bank Nifty - Last 500 Days with Technical Indicators', 
                 fontsize=16, fontweight='bold')
axes[0].set_ylabel('Price (₹)', fontsize=12)
axes[0].legend(loc='upper left', fontsize=10)
axes[0].grid(True, alpha=0.3)

# Chart 2: RSI
axes[1].plot(recent['Date'], recent['RSI'], linewidth=1.5, color='purple', label='RSI(14)')
axes[1].axhline(y=70, color='red', linestyle='--', linewidth=1, alpha=0.7, label='Overbought')
axes[1].axhline(y=30, color='green', linestyle='--', linewidth=1, alpha=0.7, label='Oversold')
axes[1].fill_between(recent['Date'], 30, 70, alpha=0.1, color='yellow')
axes[1].set_title('RSI Indicator', fontsize=14, fontweight='bold')
axes[1].set_ylabel('RSI', fontsize=11)
axes[1].set_ylim(0, 100)
axes[1].legend(loc='upper left', fontsize=9)
axes[1].grid(True, alpha=0.3)

# Chart 3: MACD
axes[2].plot(recent['Date'], recent['MACD'], linewidth=1.5, color='blue', label='MACD')
axes[2].plot(recent['Date'], recent['MACD_Signal'], linewidth=1.5, color='red', label='Signal')
axes[2].axhline(y=0, color='black', linewidth=0.8)

# Color the area between MACD and Signal
axes[2].fill_between(recent['Date'], recent['MACD'], recent['MACD_Signal'],
                    where=recent['MACD'] >= recent['MACD_Signal'],
                    alpha=0.3, color='green', label='Bullish')
axes[2].fill_between(recent['Date'], recent['MACD'], recent['MACD_Signal'],
                    where=recent['MACD'] < recent['MACD_Signal'],
                    alpha=0.3, color='red', label='Bearish')

axes[2].set_title('MACD Indicator', fontsize=14, fontweight='bold')
axes[2].set_ylabel('MACD', fontsize=11)
axes[2].legend(loc='upper left', fontsize=9)
axes[2].grid(True, alpha=0.3)

# Chart 4: ATR (Volatility)
axes[3].plot(recent['Date'], recent['ATR'], linewidth=1.5, color='orange', label='ATR(14)')
axes[3].fill_between(recent['Date'], recent['ATR'], alpha=0.3, color='orange')
axes[3].set_title('ATR - Average True Range (Volatility)', fontsize=14, fontweight='bold')
axes[3].set_xlabel('Date', fontsize=12)
axes[3].set_ylabel('ATR (₹)', fontsize=11)
axes[3].legend(loc='upper left', fontsize=9)
axes[3].grid(True, alpha=0.3)

plt.tight_layout()

# Save chart
output_file = '../results/banknifty_technical_indicators.png'
plt.savefig(output_file, dpi=200, bbox_inches='tight')
print(f"\n✓ Chart saved to: {output_file}")

plt.show()

# Save data with indicators
output_csv = '../data/banknifty_with_indicators.csv'
df.to_csv(output_csv, index=False)
print(f"✓ Data with indicators saved to: {output_csv}")

print("\n" + "="*70)
print("INDICATOR EXPLANATIONS")
print("="*70)
print("""
SMA (Simple Moving Average): Average price over N days
  - Price > SMA = Uptrend
  - Price < SMA = Downtrend

RSI (Relative Strength Index): Momentum oscillator (0-100)
  - >70 = Overbought (potential sell signal)
  - <30 = Oversold (potential buy signal)

MACD (Moving Average Convergence Divergence): Trend-following indicator
  - MACD > Signal = Bullish
  - MACD < Signal = Bearish

Bollinger Bands: Volatility bands
  - Price near upper band = Potentially overbought
  - Price near lower band = Potentially oversold

ATR (Average True Range): Measures volatility
  - Higher ATR = More volatility (wider stops needed)
  - Lower ATR = Less volatility (tighter stops possible)
""")

print("="*70)
print("You now understand the technical indicators institutions use!")
print("="*70)
