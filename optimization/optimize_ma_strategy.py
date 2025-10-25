"""
Parameter Optimization for MA Crossover Strategy
Tests multiple combinations to find the best parameters
"""

import backtrader as bt
import pandas as pd
import itertools
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from strategies.simple_ma_crossover import SimpleMAStrategy

print("="*70)
print("MA CROSSOVER STRATEGY - PARAMETER OPTIMIZATION")
print("="*70)
print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Load data
print("Loading historical data...")
df = pd.read_csv('../data/banknifty_scaled_backtest.csv')
df['Date'] = pd.to_datetime(df['Date'])
df = df.set_index('Date')
print(f"✓ Loaded {len(df)} trading days\n")

# Define parameter ranges to test
param_grid = {
    'fast_period': [10, 15, 20, 25, 30],
    'slow_period': [30, 40, 50, 60, 70],
    'stop_loss_pct': [0.02, 0.025, 0.03, 0.035, 0.04]
}

print("Parameter ranges to test:")
print(f"  Fast MA: {param_grid['fast_period']}")
print(f"  Slow MA: {param_grid['slow_period']}")
print(f"  Stop-Loss: {[f'{x*100}%' for x in param_grid['stop_loss_pct']]}")
print(f"\nTotal combinations: {len(param_grid['fast_period']) * len(param_grid['slow_period']) * len(param_grid['stop_loss_pct'])}")
print("This will take 2-3 minutes...\n")
print("="*70)

# Store results
results = []
combination_count = 0

# Test all combinations
for fast, slow, stop in itertools.product(
    param_grid['fast_period'],
    param_grid['slow_period'],
    param_grid['stop_loss_pct']
):
    # Skip invalid combinations (fast must be < slow)
    if fast >= slow:
        continue
    
    combination_count += 1
    
    # Initialize Cerebro
    cerebro = bt.Cerebro()
    
    # Add data
    data = bt.feeds.PandasData(dataname=df)
    cerebro.adddata(data)
    
    # Add strategy with current parameters
    cerebro.addstrategy(
        SimpleMAStrategy,
        fast_period=fast,
        slow_period=slow,
        stop_loss_pct=stop
    )
    
    # Set initial capital
    cerebro.broker.setcash(100000.0)
    
    # Set commission
    cerebro.broker.setcommission(commission=0.0001)
    
    # Add analyzers
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe', riskfreerate=0.06)
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    
    # Run backtest (silently)
    initial_value = cerebro.broker.getvalue()
    strat = cerebro.run()[0]
    final_value = cerebro.broker.getvalue()
    
    # Extract results
    total_return = ((final_value / initial_value) - 1) * 100
    
    sharpe_analysis = strat.analyzers.sharpe.get_analysis()
    sharpe_ratio = sharpe_analysis.get('sharperatio', None)
    
    drawdown_analysis = strat.analyzers.drawdown.get_analysis()
    max_drawdown = drawdown_analysis.max.drawdown
    
    trades_analysis = strat.analyzers.trades.get_analysis()
    total_trades = trades_analysis.total.total if hasattr(trades_analysis, 'total') else 0
    
    # Calculate win rate
    won_trades = 0
    lost_trades = 0
    if hasattr(trades_analysis, 'won') and hasattr(trades_analysis.won, 'total'):
        won_trades = trades_analysis.won.total
    if hasattr(trades_analysis, 'lost') and hasattr(trades_analysis.lost, 'total'):
        lost_trades = trades_analysis.lost.total
    
    win_rate = (won_trades / total_trades * 100) if total_trades > 0 else 0
    
    # Calculate win/loss ratio
    win_loss_ratio = 0
    if won_trades > 0 and lost_trades > 0:
        if hasattr(trades_analysis.won, 'pnl') and hasattr(trades_analysis.lost, 'pnl'):
            avg_win = trades_analysis.won.pnl.average
            avg_loss = abs(trades_analysis.lost.pnl.average)
            win_loss_ratio = avg_win / avg_loss if avg_loss != 0 else 0
    
    # Score the combination (custom scoring function)
    # Weights: Return (40%), Sharpe (30%), Win Rate (20%), Drawdown (10%)
    score = 0
    if total_return > 20:
        score += 40 * (total_return / 100)
    if sharpe_ratio and sharpe_ratio > 0.5:
        score += 30 * (sharpe_ratio / 2)
    if win_rate > 45:
        score += 20 * (win_rate / 100)
    if max_drawdown < 25:
        score += 10 * ((25 - max_drawdown) / 25)
    
    # Store result
    results.append({
        'fast_period': fast,
        'slow_period': slow,
        'stop_loss_pct': stop,
        'total_return': total_return,
        'sharpe_ratio': sharpe_ratio if sharpe_ratio else 0,
        'max_drawdown': max_drawdown,
        'total_trades': total_trades,
        'win_rate': win_rate,
        'win_loss_ratio': win_loss_ratio,
        'score': score
    })
    
    # Print progress every 10 combinations
    if combination_count % 10 == 0:
        print(f"Tested {combination_count} combinations... (Current: Fast={fast}, Slow={slow}, Stop={stop*100:.1f}%)")

print(f"\n{'='*70}")
print(f"✓ Completed testing {combination_count} parameter combinations")
print(f"{'='*70}\n")

# Convert to DataFrame and sort by score
results_df = pd.DataFrame(results)
results_df = results_df.sort_values('score', ascending=False)

# Save full results
results_df.to_csv('../results/optimization_results.csv', index=False)
print(f"✓ Saved full results to: results/optimization_results.csv\n")

# Display top 10 combinations
print("="*70)
print("TOP 10 PARAMETER COMBINATIONS")
print("="*70)
print(f"\n{'Rank':<6}{'Fast':<7}{'Slow':<7}{'Stop':<8}{'Return':<10}{'Sharpe':<9}{'Win%':<8}{'W/L':<7}{'Score':<7}")
print("-"*70)

for idx, row in results_df.head(10).iterrows():
    print(f"{results_df.index.get_loc(idx)+1:<6}"
          f"{int(row['fast_period']):<7}"
          f"{int(row['slow_period']):<7}"
          f"{row['stop_loss_pct']*100:.1f}%{'':<4}"
          f"{row['total_return']:>7.1f}%{'':<2}"
          f"{row['sharpe_ratio']:>6.2f}{'':<3}"
          f"{row['win_rate']:>5.1f}%{'':<2}"
          f"{row['win_loss_ratio']:>5.2f}{'':<2}"
          f"{row['score']:>5.1f}")

# Get best combination
best = results_df.iloc[0]

print(f"\n{'='*70}")
print("🏆 BEST PARAMETER COMBINATION")
print(f"{'='*70}")
print(f"Fast MA Period:    {int(best['fast_period'])} days")
print(f"Slow MA Period:    {int(best['slow_period'])} days")
print(f"Stop-Loss:         {best['stop_loss_pct']*100:.1f}%")
print(f"\nPerformance Metrics:")
print(f"  Total Return:    {best['total_return']:>7.1f}%")
print(f"  Sharpe Ratio:    {best['sharpe_ratio']:>7.2f}")
print(f"  Max Drawdown:    {best['max_drawdown']:>7.2f}%")
print(f"  Total Trades:    {int(best['total_trades']):>7}")
print(f"  Win Rate:        {best['win_rate']:>6.1f}%")
print(f"  Win/Loss Ratio:  {best['win_loss_ratio']:>7.2f}:1")
print(f"  Overall Score:   {best['score']:>7.1f}")
print(f"{'='*70}\n")

# Compare with current parameters (20/50/3%)
current = results_df[(results_df['fast_period'] == 20) & 
                     (results_df['slow_period'] == 50) & 
                     (results_df['stop_loss_pct'] == 0.03)]

if not current.empty:
    current = current.iloc[0]
    print("="*70)
    print("📊 COMPARISON: BEST vs CURRENT (20/50/3%)")
    print("="*70)
    print(f"{'Metric':<20}{'Current':<15}{'Best':<15}{'Change':<15}")
    print("-"*70)
    print(f"{'Total Return':<20}{current['total_return']:>7.1f}%{'':<7}{best['total_return']:>7.1f}%{'':<7}{best['total_return']-current['total_return']:>+6.1f}%")
    print(f"{'Sharpe Ratio':<20}{current['sharpe_ratio']:>7.2f}{'':<7}{best['sharpe_ratio']:>7.2f}{'':<7}{best['sharpe_ratio']-current['sharpe_ratio']:>+6.2f}")
    print(f"{'Win Rate':<20}{current['win_rate']:>7.1f}%{'':<7}{best['win_rate']:>7.1f}%{'':<7}{best['win_rate']-current['win_rate']:>+6.1f}%")
    print(f"{'Max Drawdown':<20}{current['max_drawdown']:>7.1f}%{'':<7}{best['max_drawdown']:>7.1f}%{'':<7}{best['max_drawdown']-current['max_drawdown']:>+6.1f}%")
    print(f"{'='*70}\n")

print("🎯 NEXT STEPS:")
print("1. Review the top 10 combinations above")
print("2. Choose parameters that balance return and risk")
print("3. Update your strategy with chosen parameters")
print("4. Run final backtest to see detailed trade history\n")

print(f"Optimization completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*70)
