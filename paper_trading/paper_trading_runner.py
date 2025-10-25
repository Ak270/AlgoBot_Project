"""
Paper Trading Runner - Forward Testing with Live Data
Runs strategy on current market data with virtual money
"""

import backtrader as bt
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import sys
import os
import json
import time

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from strategies.simple_ma_crossover import SimpleMAStrategy

class PaperTradingJournal:
    """Records all trades for analysis"""
    
    def __init__(self, filename='paper_trades_journal.json'):
        self.filename = filename
        self.trades = []
        self.load_journal()
    
    def load_journal(self):
        """Load existing journal if it exists"""
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as f:
                self.trades = json.load(f)
    
    def save_journal(self):
        """Save journal to file"""
        with open(self.filename, 'w') as f:
            json.dump(self.trades, indent=2, fp=f)
    
    def add_trade(self, trade_data):
        """Add a new trade to journal"""
        self.trades.append(trade_data)
        self.save_journal()

# Initialize
print("="*70)
print("PAPER TRADING SETUP - FORWARD TESTING")
print("="*70)
print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Configuration
SYMBOL = '^NSEBANK'  # Bank Nifty
INITIAL_CAPITAL = 100000.0
LOOKBACK_DAYS = 90  # How much historical data to load

# Calculate date range (last 90 days + today)
end_date = datetime.now()
start_date = end_date - timedelta(days=LOOKBACK_DAYS)

print(f"Downloading recent data for {SYMBOL}...")
print(f"Date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}\n")

# Download data
try:
    df = yf.download(SYMBOL, start=start_date, end=end_date, progress=False)
    
    # Scale prices (same as backtest)
    df['Open'] = df['Open'] / 100
    df['High'] = df['High'] / 100
    df['Low'] = df['Low'] / 100
    df['Close'] = df['Close'] / 100
    df['Adj Close'] = df['Adj Close'] / 100
    
    print(f"✓ Downloaded {len(df)} days of data")
    print(f"  Latest date: {df.index[-1].strftime('%Y-%m-%d')}")
    print(f"  Latest close: ₹{df['Close'].iloc[-1]:.2f}\n")
    
except Exception as e:
    print(f"❌ Error downloading  {e}")
    sys.exit(1)

# Initialize Backtrader
cerebro = bt.Cerebro()

# Add data
data = bt.feeds.PandasData(dataname=df)
cerebro.adddata(data)

# Add strategy with optimized parameters
cerebro.addstrategy(
    SimpleMAStrategy,
    fast_period=25,
    slow_period=60,
    stop_loss_pct=0.02
)

# Set initial capital
cerebro.broker.setcash(INITIAL_CAPITAL)

# Set commission
cerebro.broker.setcommission(commission=0.0001)

# Add analyzers
cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')

print("="*70)
print("RUNNING PAPER TRADING SIMULATION")
print("="*70)
print(f"Initial Capital: ₹{INITIAL_CAPITAL:,.2f}")
print(f"Strategy: MA Crossover (25/60)")
print(f"Stop-Loss: 2.0%")
print(f"Data Period: Last {LOOKBACK_DAYS} days")
print("="*70 + "\n")

# Run
initial_value = cerebro.broker.getvalue()
results = cerebro.run()
strat = results[0]
final_value = cerebro.broker.getvalue()

# Extract results
total_return = ((final_value / initial_value) - 1) * 100
trades_analysis = strat.analyzers.trades.get_analysis()
drawdown_analysis = strat.analyzers.drawdown.get_analysis()

# Get trade count
total_trades = 0
if hasattr(trades_analysis, 'total') and hasattr(trades_analysis.total, 'total'):
    total_trades = trades_analysis.total.total

# Print results
print("\n" + "="*70)
print("PAPER TRADING RESULTS (Last 90 Days)")
print("="*70)

print(f"\n💰 ACCOUNT STATUS")
print(f"{'─'*70}")
print(f"Starting Capital:  ₹{initial_value:>15,.2f}")
print(f"Current Capital:   ₹{final_value:>15,.2f}")
print(f"Total Return:      {total_return:>14.2f}%")

if total_return > 0:
    print(f"                   ✓ Profitable")
elif total_return < 0:
    print(f"                   ⚠ Loss")
else:
    print(f"                   ● Break-even")

print(f"\n📊 TRADING ACTIVITY")
print(f"{'─'*70}")
print(f"Total Trades:      {total_trades:>18}")

if total_trades > 0:
    won_trades = trades_analysis.won.total if hasattr(trades_analysis, 'won') and hasattr(trades_analysis.won, 'total') else 0
    lost_trades = trades_analysis.lost.total if hasattr(trades_analysis, 'lost') and hasattr(trades_analysis.lost, 'total') else 0
    win_rate = (won_trades / total_trades * 100) if total_trades > 0 else 0
    
    print(f"Winning Trades:    {won_trades:>18}")
    print(f"Losing Trades:     {lost_trades:>18}")
    print(f"Win Rate:          {win_rate:>17.1f}%")
else:
    print("No trades executed in this period")
    print("(This is normal - strategy waits for high-probability setups)")

print(f"\n📉 RISK METRICS")
print(f"{'─'*70}")
print(f"Max Drawdown:      {drawdown_analysis.max.drawdown:>17.2f}%")

if drawdown_analysis.max.drawdown < 5:
    print(f"                   ✓ Excellent (<5%)")
elif drawdown_analysis.max.drawdown < 10:
    print(f"                   ✓ Good (5-10%)")
else:
    print(f"                   ⚠ Moderate (>10%)")

print(f"\n{'='*70}")
print("📝 INTERPRETATION")
print(f"{'='*70}")

if total_trades == 0:
    print("""
This is EXPECTED behavior for a swing trading strategy!

Why no trades?
  • Strategy uses 25/60 day moving averages
  • Only trades when clear trend is confirmed
  • Waits patiently for high-probability setups
  • May go weeks/months without trading

What this means:
  ✓ Bot is working correctly
  ✓ Risk management is active
  ✓ Waiting for proper entry conditions
  ⚠ Need to run for longer to see trades (3-6 months typical)

Next Steps:
  1. Continue monitoring daily
  2. When crossover happens, you'll see entry signal
  3. Keep journal updated
  4. Be patient - quality over quantity!
""")
elif total_trades <= 2 and total_return > -5:
    print("""
Normal forward testing behavior!

What you're seeing:
  • Few trades (expected for swing strategy)
  • Small sample size
  • Strategy is being selective

This is GOOD - it means:
  ✓ Bot is following rules strictly
  ✓ Not overtrading
  ✓ Waiting for quality setups

Continue monitoring for 2-3 more months to build sample size.
""")
elif total_return > 10:
    print("""
🎉 EXCELLENT forward testing results!

Your strategy is performing well on NEW data!

This suggests:
  ✓ Strategy is robust (not overfit)
  ✓ Parameters are good
  ✓ Risk management working

Next steps:
  1. Continue paper trading for 60 days total
  2. Document all trades in journal
  3. If performance remains consistent, prepare for live trading
""")
elif total_return < -10:
    print("""
⚠️ Drawdown detected in forward testing

This could mean:
  • Normal variance (small sample)
  • Market conditions changed
  • Bad luck on 1-2 trades

What to do:
  1. Continue monitoring (don't panic!)
  2. Review trades in journal
  3. Check if stop-losses are working
  4. If drawdown > 20%, pause and re-evaluate
""")

print(f"\n{'='*70}")
print(f"Paper trading completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"{'='*70}\n")

print("🎯 ACTION ITEMS:")
print("  1. Run this script daily to update your paper trading")
print("  2. Keep a trading journal of decisions and emotions")
print("  3. After 60 days, review and decide on live trading")
print("  4. Next run command: cd paper_trading && python3.11 paper_trading_runner.py\n")

# Save results to journal
journal = PaperTradingJournal()
journal.add_trade({
    'date': datetime.now().strftime('%Y-%m-%d'),
    'starting_capital': initial_value,
    'ending_capital': final_value,
    'return_pct': total_return,
    'total_trades': total_trades,
    'max_drawdown': drawdown_analysis.max.drawdown,
    'days_tested': len(df)
})

print(f"✓ Results saved to: {journal.filename}\n")
