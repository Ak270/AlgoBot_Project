import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

print("Loading data...")
df = pd.read_csv('../data/banknifty_daily_10y.csv')
df['Date'] = pd.to_datetime(df['Date'])

print(f"Loaded {len(df)} trading days")
print(f"Date range: {df['Date'].min().strftime('%Y-%m-%d')} to {df['Date'].max().strftime('%Y-%m-%d')}")

# Create comprehensive visualization
fig = plt.figure(figsize=(16, 12))
gs = fig.add_gridspec(4, 1, height_ratios=[3, 1, 1, 1], hspace=0.3)

# Chart 1: Price with High-Low Range
ax1 = fig.add_subplot(gs[0])
ax1.plot(df['Date'], df['Close'], linewidth=1.5, color='#2E86C1', label='Close Price', zorder=3)
ax1.fill_between(df['Date'], df['Low'], df['High'], alpha=0.15, color='gray', label='Daily Range')

# Highlight major events
# COVID Crash (March 2020)
covid_period = df[(df['Date'] >= '2020-03-01') & (df['Date'] <= '2020-04-30')]
if len(covid_period) > 0:
    ax1.axvspan(covid_period['Date'].min(), covid_period['Date'].max(), 
                alpha=0.2, color='red', label='COVID Crash')

# Mark highest and lowest prices
max_idx = df['Close'].idxmax()
min_idx = df['Close'].idxmin()

ax1.scatter(df.loc[max_idx, 'Date'], df.loc[max_idx, 'Close'], 
           s=100, c='green', marker='^', zorder=5)
ax1.annotate(f"ALL-TIME HIGH\n₹{df['Close'].max():,.0f}\n{df.loc[max_idx, 'Date'].strftime('%Y-%m-%d')}",
            xy=(df.loc[max_idx, 'Date'], df.loc[max_idx, 'Close']),
            xytext=(10, 20), textcoords='offset points',
            bbox=dict(boxstyle='round,pad=0.5', fc='green', alpha=0.8),
            fontsize=9, color='white', fontweight='bold',
            arrowprops=dict(arrowstyle='->', color='green', lw=1.5))

ax1.scatter(df.loc[min_idx, 'Date'], df.loc[min_idx, 'Close'], 
           s=100, c='red', marker='v', zorder=5)
ax1.annotate(f"LOWEST POINT\n₹{df['Close'].min():,.0f}\n{df.loc[min_idx, 'Date'].strftime('%Y-%m-%d')}",
            xy=(df.loc[min_idx, 'Date'], df.loc[min_idx, 'Close']),
            xytext=(10, -40), textcoords='offset points',
            bbox=dict(boxstyle='round,pad=0.5', fc='red', alpha=0.8),
            fontsize=9, color='white', fontweight='bold',
            arrowprops=dict(arrowstyle='->', color='red', lw=1.5))

ax1.set_title('Bank Nifty - Complete Price History (2015-2025)', 
             fontsize=18, fontweight='bold', pad=20)
ax1.set_ylabel('Price (₹)', fontsize=12, fontweight='bold')
ax1.grid(True, alpha=0.3, linestyle='--')
ax1.legend(loc='upper left', fontsize=10)
ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'₹{x:,.0f}'))

# Chart 2: Daily Returns (% Change)
ax2 = fig.add_subplot(gs[1])
df['Daily_Return'] = df['Close'].pct_change() * 100
colors = ['green' if x > 0 else 'red' for x in df['Daily_Return']]
ax2.bar(df['Date'], df['Daily_Return'], color=colors, alpha=0.6, width=1)
ax2.axhline(y=0, color='black', linewidth=0.8)
ax2.set_title('Daily Returns (%)', fontsize=14, fontweight='bold')
ax2.set_ylabel('% Change', fontsize=11)
ax2.grid(True, alpha=0.3, axis='y')

# Chart 3: Volume
ax3 = fig.add_subplot(gs[2])
ax3.bar(df['Date'], df['Volume'], color='teal', alpha=0.6, width=1)
ax3.set_title('Trading Volume', fontsize=14, fontweight='bold')
ax3.set_ylabel('Volume', fontsize=11)
ax3.ticklabel_format(style='plain', axis='y')
ax3.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1e6:.1f}M'))
ax3.grid(True, alpha=0.3, axis='y')

# Chart 4: Price Distribution (Histogram)
ax4 = fig.add_subplot(gs[3])
ax4.hist(df['Close'], bins=50, color='#2E86C1', alpha=0.7, edgecolor='black')
ax4.axvline(df['Close'].mean(), color='red', linestyle='--', linewidth=2, label='Mean')
ax4.axvline(df['Close'].median(), color='green', linestyle='--', linewidth=2, label='Median')
ax4.set_title('Price Distribution', fontsize=14, fontweight='bold')
ax4.set_xlabel('Price (₹)', fontsize=11)
ax4.set_ylabel('Frequency', fontsize=11)
ax4.legend()
ax4.grid(True, alpha=0.3, axis='y')

plt.tight_layout()

# Save chart
output_file = '../results/banknifty_complete_analysis.png'
plt.savefig(output_file, dpi=200, bbox_inches='tight')
print(f"\n✓ Chart saved to: {output_file}")

plt.show()

# Print statistics
print("\n" + "="*70)
print("MARKET STATISTICS")
print("="*70)

print(f"\nPrice Analysis:")
print(f"  Current Price: ₹{df['Close'].iloc[-1]:,.2f}")
print(f"  All-Time High: ₹{df['Close'].max():,.2f} (on {df.loc[max_idx, 'Date'].strftime('%Y-%m-%d')})")
print(f"  All-Time Low: ₹{df['Close'].min():,.2f} (on {df.loc[min_idx, 'Date'].strftime('%Y-%m-%d')})")
print(f"  Price Range: ₹{df['Close'].max() - df['Close'].min():,.2f}")
print(f"  Average Price: ₹{df['Close'].mean():,.2f}")
print(f"  Median Price: ₹{df['Close'].median():,.2f}")

# Calculate total return
total_return = ((df['Close'].iloc[-1] / df['Close'].iloc[0]) - 1) * 100
print(f"\nTotal Return ({df['Date'].iloc[0].strftime('%Y-%m-%d')} to {df['Date'].iloc[-1].strftime('%Y-%m-%d')}): {total_return:+.2f}%")

# Volatility
daily_volatility = df['Daily_Return'].std()
annual_volatility = daily_volatility * (252 ** 0.5)  # Annualized
print(f"\nVolatility:")
print(f"  Daily Volatility: {daily_volatility:.2f}%")
print(f"  Annual Volatility: {annual_volatility:.2f}%")

# Best and worst days
best_day = df.loc[df['Daily_Return'].idxmax()]
worst_day = df.loc[df['Daily_Return'].idxmin()]
print(f"\nExtreme Days:")
print(f"  Best Day: {best_day['Date'].strftime('%Y-%m-%d')} (+{best_day['Daily_Return']:.2f}%)")
print(f"  Worst Day: {worst_day['Date'].strftime('%Y-%m-%d')} ({worst_day['Daily_Return']:.2f}%)")

# Winning days
winning_days = (df['Daily_Return'] > 0).sum()
total_days = len(df) - 1  # Exclude first day (no return)
win_rate = (winning_days / total_days) * 100
print(f"\nWinning Days: {winning_days}/{total_days} ({win_rate:.1f}%)")

print("\n" + "="*70)
print("Key Observations:")
print("1. Identify the COVID crash (March 2020) - Sharp drop visible")
print("2. Notice the recovery and bull run (2020-2024)")
print("3. Daily returns show volatility (green/red bars)")
print("4. Volume spikes during major events")
print("5. Price distribution shows most trading around ₹40,000-45,000")
print("="*70)
