"""
Backtest Runner for Momentum Breakout Strategy
-----------------------------------------------
Loads historical data, runs strategy, analyzes performance
"""

import backtrader as bt
import pandas as pd
from datetime import datetime
import sys
import os

# Add parent directory to path so we can import strategy
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from strategies.momentum_breakout_strategy import MomentumBreakoutStrategy
from strategies.simple_ma_crossover import SimpleMAStrategy

print("="*70)
print("BACKTESTING: SIMPLE MA STRATEGY")
print("="*70)
print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Load data
print("Loading historical data...")
df = pd.read_csv('../data/banknifty_scaled_backtest.csv')
df['Date'] = pd.to_datetime(df['Date'])
df = df.set_index('Date')

print(f"✓ Loaded {len(df)} trading days")
print(f"  Date Range: {df.index[0].strftime('%Y-%m-%d')} to {df.index[-1].strftime('%Y-%m-%d')}\n")

# Initialize Backtrader
cerebro = bt.Cerebro()

# Convert pandas DataFrame to Backtrader data feed
data = bt.feeds.PandasData(dataname=df)
cerebro.adddata(data)

# Add our strategy
cerebro.addstrategy(SimpleMAStrategy) # old parameter: MomentumBreakoutStrategy

# Set initial capital
initial_capital = 100000.0  # ₹1 lakh
cerebro.broker.setcash(initial_capital)

# Set commission (realistic Indian brokerage)
# ₹20 per trade + 0.01% STT on sell side
cerebro.broker.setcommission(
    commission=0.0001,  # 0.01% for simplicity
    mult=1.0,
    margin=None
)

# Add analyzers for performance metrics
cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe', riskfreerate=0.06)
cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
cerebro.addanalyzer(bt.analyzers.SQN, _name='sqn')  # System Quality Number

# Print starting conditions
print(f"{'='*70}")
print("BACKTEST CONFIGURATION")
print(f"{'='*70}")
print(f"Initial Capital: ₹{initial_capital:,.2f}")
print(f"Commission: 0.01% per trade + ₹20 fixed")
print(f"Data Period: {len(df)} days ({len(df)/252:.1f} years)")
print(f"{'='*70}\n")

# Run backtest
print("Running backtest... (this may take 30-60 seconds)\n")
results = cerebro.run()
strat = results[0]

# Get final portfolio value
final_value = cerebro.broker.getvalue()
total_return = ((final_value / initial_capital) - 1) * 100

# Extract analyzer results
sharpe_ratio = strat.analyzers.sharpe.get_analysis()
drawdown = strat.analyzers.drawdown.get_analysis()
trades = strat.analyzers.trades.get_analysis()
returns = strat.analyzers.returns.get_analysis()
sqn = strat.analyzers.sqn.get_analysis()

# Print results
print("\n" + "="*70)
print("BACKTEST RESULTS")
print("="*70)

print(f"\n💰 PORTFOLIO PERFORMANCE")
print(f"{'─'*70}")
print(f"Starting Capital:  ₹{initial_capital:>15,.2f}")
print(f"Ending Capital:    ₹{final_value:>15,.2f}")
print(f"Total Return:      {total_return:>14.2f}%")
print(f"Annual Return:     {(total_return / (len(df)/252)):>14.2f}%")

print(f"\n📊 RISK METRICS")
print(f"{'─'*70}")
sharpe_value = sharpe_ratio.get('sharperatio', None)
if sharpe_value:
    print(f"Sharpe Ratio:      {sharpe_value:>18.2f}")
    if sharpe_value > 1.0:
        print(f"                   {'✓ Excellent (>1.0)':>28}")
    elif sharpe_value > 0.5:
        print(f"                   {'✓ Good (0.5-1.0)':>28}")
    else:
        print(f"                   {'⚠ Poor (<0.5)':>28}")
else:
    print(f"Sharpe Ratio:      {'N/A':>18}")

print(f"Max Drawdown:      {drawdown.max.drawdown:>17.2f}%")
if drawdown.max.drawdown < 15:
    print(f"                   {'✓ Excellent (<15%)':>28}")
elif drawdown.max.drawdown < 25:
    print(f"                   {'✓ Good (15-25%)':>28}")
else:
    print(f"                   {'⚠ High (>25%)':>28}")

# System Quality Number
sqn_value = sqn.sqn
print(f"SQN (Quality):     {sqn_value:>18.2f}")
if sqn_value > 3.0:
    print(f"                   {'✓ Excellent (>3.0)':>28}")
elif sqn_value > 1.9:
    print(f"                   {'✓ Good (1.9-3.0)':>28}")
else:
    print(f"                   {'⚠ Poor (<1.9)':>28}")

print(f"\n📈 TRADING STATISTICS")
print(f"{'─'*70}")
# Safely extract trade counts
total_trades = trades.total.total if hasattr(trades, 'total') and hasattr(trades.total, 'total') else 0
won_trades = trades.won.total if hasattr(trades, 'won') and hasattr(trades.won, 'total') else 0
lost_trades = trades.lost.total if hasattr(trades, 'lost') and hasattr(trades.lost, 'total') else 0
win_rate = (won_trades / total_trades * 100) if total_trades > 0 else 0

print(f"Total Trades:      {total_trades:>18}")
print(f"Winning Trades:    {won_trades:>18}")
print(f"Losing Trades:     {lost_trades:>18}")
print(f"Win Rate:          {win_rate:>17.1f}%")

if win_rate >= 50:
    print(f"                   {'✓ Good (≥50%)':>28}")
else:
    print(f"                   {'⚠ Below 50%':>28}")

if won_trades > 0 and hasattr(trades.won, 'pnl') and hasattr(trades.won.pnl, 'average'):
    avg_win = trades.won.pnl.average
    print(f"Avg Win:           ₹{avg_win:>16,.2f}")
else:
    avg_win = 0
    print(f"Avg Win:           {'N/A':>18}")

if lost_trades > 0 and hasattr(trades.lost, 'pnl') and hasattr(trades.lost.pnl, 'average'):
    avg_loss = trades.lost.pnl.average
    print(f"Avg Loss:          ₹{avg_loss:>16,.2f}")
    
    if won_trades > 0 and avg_win > 0:
        win_loss_ratio = abs(avg_win / avg_loss)
        print(f"Win/Loss Ratio:    {win_loss_ratio:>18.2f}:1")
        if win_loss_ratio >= 2.0:
            print(f"                   {'✓ Excellent (≥2:1)':>28}")
        elif win_loss_ratio >= 1.5:
            print(f"                   {'✓ Good (1.5-2:1)':>28}")
        else:
            print(f"                   {'⚠ Low (<1.5:1)':>28}")
else:
    avg_loss = 0
    print(f"Avg Loss:          {'N/A':>18}")


# Trading frequency
trades_per_year = total_trades / (len(df) / 252)
print(f"Trades Per Year:   {trades_per_year:>18.1f}")

print(f"\n🎯 DECISION CRITERIA")
print(f"{'─'*70}")

# Check if strategy passes institutional standards
criteria_met = 0
criteria_total = 5

if total_return > 20:  # >20% total return over test period
    print("✓ Profitability: PASS (Total return >20%)")
    criteria_met += 1
else:
    print("✗ Profitability: FAIL (Total return <20%)")

if sharpe_value and sharpe_value > 0.5:
    print("✓ Risk-Adjusted Returns: PASS (Sharpe >0.5)")
    criteria_met += 1
else:
    print("✗ Risk-Adjusted Returns: FAIL (Sharpe <0.5)")

if drawdown.max.drawdown < 25:
    print("✓ Drawdown Control: PASS (Max DD <25%)")
    criteria_met += 1
else:
    print("✗ Drawdown Control: FAIL (Max DD >25%)")

if win_rate >= 45:
    print("✓ Win Rate: PASS (≥45%)")
    criteria_met += 1
else:
    print("✗ Win Rate: FAIL (<45%)")

if total_trades >= 20:
    print("✓ Sample Size: PASS (≥20 trades)")
    criteria_met += 1
else:
    print("✗ Sample Size: FAIL (<20 trades)")

print(f"\n{'='*70}")
print(f"CRITERIA MET: {criteria_met}/{criteria_total}")
print(f"{'='*70}")

if criteria_met >= 4:
    print("\n✅ VERDICT: STRATEGY PASSES - Proceed to optimization")
    print("Next steps:")
    print("  1. Optimize parameters (lookback periods, thresholds)")
    print("  2. Run Monte Carlo simulation")
    print("  3. Walk-forward analysis")
elif criteria_met == 3:
    print("\n⚠️  VERDICT: MARGINAL - Needs optimization")
    print("Review failed criteria and adjust parameters")
else:
    print("\n❌ VERDICT: STRATEGY FAILS - Major revision needed")
    print("Consider:")
    print("  1. Different entry/exit logic")
    print("  2. Additional filters")
    print("  3. Different instruments")

print(f"\n{'='*70}")
print(f"Backtest completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"{'='*70}\n")

# Plot results (optional - shows equity curve)
print("Generating equity curve chart...")
cerebro.plot(style='candlestick', barup='green', bardown='red')
