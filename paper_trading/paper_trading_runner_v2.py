"""
Paper Trading Runner V2 - With Multiple Data Sources
"""

import backtrader as bt
import pandas as pd
from datetime import datetime
import sys
import os
import json

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from strategies.simple_ma_crossover import SimpleMAStrategy

# Import our improved downloader
from improved_data_downloader import get_bank_nifty_data

print("="*70)
print("PAPER TRADING - FORWARD TESTING V2")
print("="*70)
print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Get data using improved downloader
df = get_bank_nifty_data(lookback_days=90)

if df is None or len(df) < 60:
    print("\n❌ CRITICAL ERROR: Could not get sufficient data")
    print("\n🔧 WORKAROUND: Using last backtest data for demonstration")
    print("   (In real trading, you'd wait for data source to work)\n")
    
    # Load last backtest data as emergency fallback
    try:
        df = pd.read_csv('../data/banknifty_scaled_backtest.csv')
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.set_index('Date')
        df = df.tail(90)  # Last 90 days
        df['Adj Close'] = df['Close']
        print(f"✓ Emergency fallback data loaded: {len(df)} days")
    except Exception as e:
        print(f"❌ Emergency fallback also failed: {e}")
        sys.exit(1)

print(f"\n✓ Using  {len(df)} days")
print(f"  Date range: {df.index[0].strftime('%Y-%m-%d')} to {df.index[-1].strftime('%Y-%m-%d')}")
print(f"  Latest close: ₹{df['Close'].iloc[-1]:.2f}\n")

# Initialize Backtrader
cerebro = bt.Cerebro()

# Add data
data = bt.feeds.PandasData(dataname=df)
cerebro.adddata(data)

# Add strategy
cerebro.addstrategy(
    SimpleMAStrategy,
    fast_period=25,
    slow_period=60,
    stop_loss_pct=0.02
)

# Set initial capital
INITIAL_CAPITAL = 100000.0
cerebro.broker.setcash(INITIAL_CAPITAL)
cerebro.broker.setcommission(commission=0.0001)

# Add analyzers
cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')

print("="*70)
print("RUNNING SIMULATION")
print("="*70)
print(f"Initial Capital: ₹{INITIAL_CAPITAL:,.2f}")
print(f"Strategy: MA Crossover (25/60)")
print(f"Stop-Loss: 2.0%")
print(f"Data Period: {len(df)} days")
print("="*70 + "\n")

# Run
initial_value = cerebro.broker.getvalue()
results = cerebro.run()
strat = results[0]
final_value = cerebro.broker.getvalue()

# Results
total_return = ((final_value / initial_value) - 1) * 100
trades_analysis = strat.analyzers.trades.get_analysis()
drawdown_analysis = strat.analyzers.drawdown.get_analysis()

total_trades = 0
if hasattr(trades_analysis, 'total') and hasattr(trades_analysis.total, 'total'):
    total_trades = trades_analysis.total.total

print("\n" + "="*70)
print("PAPER TRADING RESULTS")
print("="*70)

print(f"\n💰 ACCOUNT STATUS")
print(f"{'─'*70}")
print(f"Starting Capital:  ₹{initial_value:>15,.2f}")
print(f"Current Capital:   ₹{final_value:>15,.2f}")
print(f"Total Return:      {total_return:>14.2f}%")

print(f"\n📊 TRADING ACTIVITY")
print(f"{'─'*70}")
print(f"Total Trades:      {total_trades:>18}")

if total_trades > 0:
    won = trades_analysis.won.total if hasattr(trades_analysis, 'won') else 0
    lost = trades_analysis.lost.total if hasattr(trades_analysis, 'lost') else 0
    win_rate = (won / total_trades * 100) if total_trades > 0 else 0
    print(f"Winning Trades:    {won:>18}")
    print(f"Losing Trades:     {lost:>18}")
    print(f"Win Rate:          {win_rate:>17.1f}%")
else:
    print("\nNo trades in this period (NORMAL for swing strategy)")
    print("Strategy is waiting for clear trend signals")

print(f"\n📉 RISK")
print(f"{'─'*70}")
print(f"Max Drawdown:      {drawdown_analysis.max.drawdown:>17.2f}%")

print(f"\n{'='*70}")
print("📝 NOTES")
print(f"{'='*70}")

if total_trades == 0:
    print("""
✓ Normal behavior - swing strategies wait for quality setups
✓ May go weeks without trading
✓ Continue monitoring daily
✓ When MA crossover happens, you'll see BUY signal
""")
elif total_return > 5:
    print("""
🎉 Positive returns! Strategy is performing well.
✓ Continue monitoring
✓ Keep journal updated
""")

print(f"\n✓ Paper trading updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*70 + "\n")

print("🎯 NEXT STEPS:")
print("  1. Run this daily: python3.11 paper_trading_runner_v2.py")
print("  2. Keep trading journal")
print("  3. Monitor for 60 days")
print()
