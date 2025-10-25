"""
Generate Complete Dashboard Data
"""

import json
from datetime import datetime
import sys
import os
import backtrader as bt

# Add parent to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from strategies.simple_ma_crossover import SimpleMAStrategy
from improved_data_downloader import get_bank_nifty_data

print("="*70)
print("GENERATING DASHBOARD DATA")
print("="*70)

# Get data
df = get_bank_nifty_data(lookback_days=90)

if df is None or len(df) < 60:
    print("Using backup data...")
    import pandas as pd
    df = pd.read_csv('../data/banknifty_scaled_backtest.csv')
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.set_index('Date')
    df = df.tail(90)
    df['Adj Close'] = df['Close']

print(f"✓ Data loaded: {len(df)} days")

# Run backtrader to get exact position
cerebro = bt.Cerebro()

# Ensure DataFrame has proper column names
if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.droplevel(1)
df.columns = [str(col).strip() for col in df.columns]

# Create data feed
data = bt.feeds.PandasData(dataname=df)
cerebro.adddata(data)

cerebro.addstrategy(SimpleMAStrategy, fast_period=25, slow_period=60, stop_loss_pct=0.02)

INITIAL_CAPITAL = 100000.0
cerebro.broker.setcash(INITIAL_CAPITAL)
cerebro.broker.setcommission(commission=0.0001)

# Add analyzers
cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')

# Run
initial_value = cerebro.broker.getvalue()
results = cerebro.run()
strat = results[0]
final_value = cerebro.broker.getvalue()

# Extract analysis
total_return = ((final_value / initial_value) - 1) * 100
trades_analysis = strat.analyzers.trades.get_analysis()
drawdown_analysis = strat.analyzers.drawdown.get_analysis()
returns_analysis = strat.analyzers.returns.get_analysis()

# Get trade stats
total_trades = 0
won_trades = 0
lost_trades = 0
if hasattr(trades_analysis, 'total') and hasattr(trades_analysis.total, 'total'):
    total_trades = trades_analysis.total.total

if total_trades > 0:
    try:
        if hasattr(trades_analysis, 'won'):
            won_trades = trades_analysis.won.total if hasattr(trades_analysis.won, 'total') else 0
        if hasattr(trades_analysis, 'lost'):
            lost_trades = trades_analysis.lost.total if hasattr(trades_analysis.lost, 'total') else 0
    except:
        pass

# Calculate current position
latest = df.iloc[-1]
ma25 = float(df['Close'].rolling(25).mean().iloc[-1])
ma60 = float(df['Close'].rolling(60).mean().iloc[-1])
in_position = ma25 > ma60

# Determine position details
position_entry = None
position_price = None
stop_loss = None
current_pnl = 0
days_in_trade = 0

if in_position:
    # Find entry point (when MA25 crossed above MA60)
    df['MA25'] = df['Close'].rolling(25).mean()
    df['MA60'] = df['Close'].rolling(60).mean()
    
    # Look backwards for crossover
    for i in range(len(df)-1, 0, -1):
        if df['MA25'].iloc[i] > df['MA60'].iloc[i] and df['MA25'].iloc[i-1] <= df['MA60'].iloc[i-1]:
            position_entry = df.index[i].strftime('%Y-%m-%d')
            position_price = float(df['Close'].iloc[i])
            stop_loss = position_price * 0.98  # 2% stop loss
            current_pnl = ((latest['Close'] / position_price) - 1) * 100
            days_in_trade = (df.index[-1] - df.index[i]).days
            break

# Create manual trade history
manual_trades = []

# Trade 1: Apr 1 - Aug 13, 2025
manual_trades.append({
    'trade_num': 1,
    'entry_date': '2025-04-01',
    'entry_price': 508.27,
    'exit_date': '2025-08-13',
    'exit_price': 551.81,
    'quantity': 186,
    'entry_value': 508.27 * 186,
    'exit_value': 551.81 * 186,
    'pnl': (551.81 - 508.27) * 186,
    'pnl_pct': ((551.81 / 508.27) - 1) * 100,
    'days_held': 134,
    'result': 'WIN'
})

# Trade 2: Oct 14 - Present (ACTIVE)
if position_entry and position_price:
    trade2_quantity = 181  # From bot output
    manual_trades.append({
        'trade_num': 2,
        'entry_date': position_entry,
        'entry_price': position_price,
        'exit_date': 'ACTIVE',
        'exit_price': 'ACTIVE',
        'quantity': trade2_quantity,
        'entry_value': position_price * trade2_quantity,
        'exit_value': 'ACTIVE',
        'pnl': final_value - (initial_value + manual_trades[0]['pnl']),
        'pnl_pct': current_pnl,
        'days_held': days_in_trade,
        'result': 'ACTIVE'
    })

# Build dashboard data
dashboard = {
    'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S IST'),
    
    # Market Data
    'market': {
        'symbol': 'Bank Nifty',
        'current_price': float(latest['Close']),
        'ma25': ma25,
        'ma60': ma60,
        'latest_date': latest.name.strftime('%Y-%m-%d'),
        'data_days': int(len(df))
    },
    
    # Signal
    'signal': {
        'status': 'HOLD' if in_position else 'WAITING',
        'trend': 'BULLISH' if ma25 > ma60 else 'BEARISH',
        'description': 'MA25 above MA60' if ma25 > ma60 else 'MA25 below MA60'
    },
    
    # Position (if in trade)
    'position': {
        'active': in_position,
        'entry_date': position_entry,
        'entry_price': position_price,
        'current_price': float(latest['Close']) if in_position else None,
        'stop_loss': stop_loss,
        'target': 'MA Crossover (Dynamic)',
        'days_held': days_in_trade,
        'unrealized_pnl_pct': round(current_pnl, 2) if in_position else 0,
        'unrealized_pnl_value': round((final_value - initial_value), 2) if in_position else 0
    },
    
    # Account
    'account': {
        'initial_capital': initial_value,
        'current_value': final_value,
        'total_return_pct': round(total_return, 2),
        'total_profit': round(final_value - initial_value, 2),
        'cash': round(cerebro.broker.getcash(), 2)
    },
    
    # Stats
    'stats': {
        'total_trades': total_trades,
        'winning_trades': won_trades,
        'losing_trades': lost_trades,
        'win_rate': round((won_trades / total_trades * 100), 1) if total_trades > 0 else 0,
        'max_drawdown': round(drawdown_analysis.max.drawdown, 2),
        'avg_return': round(returns_analysis.rnorm100, 2) if hasattr(returns_analysis, 'rnorm100') else 0
    },
    
    # Strategy Info
    'strategy': {
        'name': 'MA Crossover',
        'fast_ma': 25,
        'slow_ma': 60,
        'stop_loss_pct': 2.0,
        'position_size': '95% of capital',
        'backtest_return': 110.0,
        'backtest_sharpe': 0.76
    },
    
    # Trade History
    'trade_history': manual_trades
}

# Save
os.makedirs('../dashboard', exist_ok=True)
with open('../dashboard/data.json', 'w') as f:
    json.dump(dashboard, f, indent=2)

print(f"\n✓ Dashboard data generated!")
print(f"  Current Price: ₹{dashboard['market']['current_price']:.2f}")
print(f"  Signal: {dashboard['signal']['status']}")
print(f"  Trend: {dashboard['signal']['trend']}")
print(f"  Position: {'ACTIVE' if dashboard['position']['active'] else 'NONE'}")
if dashboard['position']['active']:
    print(f"  Entry: {dashboard['position']['entry_date']} @ ₹{dashboard['position']['entry_price']:.2f}")
    print(f"  P&L: ₹{dashboard['position']['unrealized_pnl_value']:+,.2f} ({dashboard['position']['unrealized_pnl_pct']:+.2f}%)")
print(f"  Account: ₹{dashboard['account']['current_value']:,.2f} ({dashboard['account']['total_return_pct']:+.2f}%)")
print(f"  Trades in history: {len(manual_trades)}")
print("="*70)
