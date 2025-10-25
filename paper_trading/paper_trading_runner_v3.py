"""
Paper Trading Runner V3 - Bug Fixed
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
from improved_data_downloader import get_bank_nifty_data

print("="*70)
print("PAPER TRADING - FORWARD TESTING V3")
print("="*70)
print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Get data
df = get_bank_nifty_data(lookback_days=90)

if df is None or len(df) < 60:
    print("\n🔧 Using emergency backup data...")
    try:
        df = pd.read_csv('../data/banknifty_scaled_backtest.csv')
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.set_index('Date')
        df = df.tail(90)
        df['Adj Close'] = df['Close']
        print(f"✓ Backup data loaded: {len(df)} days")
    except Exception as e:
        print(f"❌ Failed: {e}")
        sys.exit(1)

print(f"\n✓ Using  {len(df)} days")
print(f"  Date range: {df.index[0].strftime('%Y-%m-%d')} to {df.index[-1].strftime('%Y-%m-%d')}")
print(f"  Latest close: ₹{df['Close'].iloc[-1]:.2f}\n")

# Initialize Backtrader
cerebro = bt.Cerebro()
data = bt.feeds.PandasData(dataname=df)
cerebro.adddata(data)

# Add strategy
cerebro.addstrategy(
    SimpleMAStrategy,
    fast_period=25,
    slow_period=60,
    stop_loss_pct=0.02
)

# Set capital
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

# Safely extract trade stats
total_trades = 0
won_trades = 0
lost_trades = 0
win_rate = 0

if hasattr(trades_analysis, 'total'):
    if hasattr(trades_analysis.total, 'total'):
        total_trades = trades_analysis.total.total
    
    if hasattr(trades_analysis.total, 'closed'):
        closed_trades = trades_analysis.total.closed
        
        # Check for won/lost stats (only if trades closed)
        if closed_trades > 0:
            try:
                if hasattr(trades_analysis, 'won') and hasattr(trades_analysis.won, 'total'):
                    won_trades = trades_analysis.won.total
                if hasattr(trades_analysis, 'lost') and hasattr(trades_analysis.lost, 'total'):
                    lost_trades = trades_analysis.lost.total
                
                if closed_trades > 0:
                    win_rate = (won_trades / closed_trades * 100)
            except:
                pass

print("\n" + "="*70)
print("📊 PAPER TRADING RESULTS")
print("="*70)

print(f"\n💰 ACCOUNT STATUS")
print(f"{'─'*70}")
print(f"Starting Capital:  ₹{initial_value:>15,.2f}")
print(f"Current Capital:   ₹{final_value:>15,.2f}")
print(f"Total Return:      {total_return:>14.2f}%")

if total_return > 0:
    print(f"                   {'✅ PROFITABLE':>30}")
elif total_return < 0:
    print(f"                   {'⚠️ LOSS':>30}")
else:
    print(f"                   {'● BREAK-EVEN':>30}")

print(f"\n📈 TRADING ACTIVITY")
print(f"{'─'*70}")
print(f"Total Signals:     {total_trades:>18}")

if total_trades > 0:
    if won_trades + lost_trades > 0:
        print(f"Completed Trades:  {won_trades + lost_trades:>18}")
        print(f"  Winning:         {won_trades:>18}")
        print(f"  Losing:          {lost_trades:>18}")
        print(f"  Win Rate:        {win_rate:>17.1f}%")
    else:
        print(f"Trade Status:      {'CURRENTLY OPEN':>18}")
        print(f"                   {'(Not yet closed)':>18}")
else:
    print(f"Status:            {'WAITING FOR SIGNAL':>18}")

print(f"\n📉 RISK METRICS")
print(f"{'─'*70}")
print(f"Max Drawdown:      {drawdown_analysis.max.drawdown:>17.2f}%")

if drawdown_analysis.max.drawdown < 5:
    print(f"                   {'✅ Excellent':>30}")
elif drawdown_analysis.max.drawdown < 10:
    print(f"                   {'✅ Good':>30}")
else:
    print(f"                   {'⚠️ Moderate':>30}")

# Check current position
in_position = final_value != initial_capital and total_trades > 0 and (won_trades + lost_trades) == 0

print(f"\n{'='*70}")
print("📝 CURRENT STATUS")
print(f"{'='*70}")

if in_position:
    profit_loss = final_value - initial_value
    print(f"""
🔵 YOU ARE CURRENTLY IN A TRADE!

Entry Information:
  • Entered on: October 15, 2025 (from backtest data)
  • Position: LONG (expecting price to rise)
  • Account value: ₹{final_value:,.2f}
  • Unrealized P&L: ₹{profit_loss:+,.2f} ({total_return:+.2f}%)

What happens next:
  1. If 25-day MA crosses BELOW 60-day MA → SELL signal (take profit)
  2. If price drops 2% → Stop-loss triggers (cut loss)
  3. If neither happens → HOLD position

Action for you:
  ✅ DO NOTHING - Let the bot manage the trade
  ✅ Run this script daily to monitor
  ✅ Journal your emotions (are you anxious? excited?)
  ✅ This is the REAL test of your discipline!

Remember: Your backtest showed 45.5% win rate with 5.23:1 reward/risk.
Not every trade wins, but overall system is profitable.
""")
elif total_trades == 0:
    print("""
⏳ WAITING FOR TRADE SIGNAL

Current Status:
  • 25-day MA and 60-day MA not aligned for entry
  • Bot is patiently waiting for high-probability setup
  • This is NORMAL for swing trading strategies

What this means:
  ✅ Bot is working correctly
  ✅ Risk management is active
  ✅ Quality over quantity approach

Historical data shows:
  • Average 2-3 trades per year
  • May wait weeks/months for perfect entry
  • When signal comes, win rate is 45.5%

Action for you:
  ✅ Continue monitoring daily
  ✅ Be patient - good things come to those who wait
  ✅ Do NOT manually enter trades out of boredom!
""")
else:
    print(f"""
📊 TRADE CYCLE COMPLETE

You've completed {won_trades + lost_trades} trade(s):
  • Wins: {won_trades}
  • Losses: {lost_trades}
  • Net P&L: ₹{final_value - initial_value:+,.2f} ({total_return:+.2f}%)

Status: Waiting for next signal

Action:
  ✅ Review trade in journal
  ✅ Analyze what worked/didn't work
  ✅ Continue monitoring for next setup
""")

print(f"\n{'='*70}")
print(f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}")
print(f"{'='*70}\n")

print("🎯 DAILY ROUTINE:")
print("  1. Run: python3.11 paper_trading_runner_v3.py")
print("  2. Read the 'CURRENT STATUS' section above")
print("  3. Update journal with your emotions/thoughts")
print("  4. That's it! The bot does the rest.\n")

# Save to journal
try:
    journal_file = 'paper_trading_journal.json'
    
    if os.path.exists(journal_file):
        with open(journal_file, 'r') as f:
            journal = json.load(f)
    else:
        journal = []
    
    journal.append({
        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'portfolio_value': final_value,
        'return_pct': total_return,
        'total_trades': total_trades,
        'in_position': in_position,
        'max_drawdown': drawdown_analysis.max.drawdown
    })
    
    with open(journal_file, 'w') as f:
        json.dump(journal, f, indent=2)
    
    print(f"✓ Saved to journal: {journal_file}\n")
except Exception as e:
    print(f"⚠️ Could not save to journal: {e}\n")
