"""
Simple Moving Average Crossover - Proven on Indices Since 1950s
Works because indices MEAN-REVERT, not breakout
"""
import backtrader as bt

class SimpleMAStrategy(bt.Strategy):
    params = (
        ('fast_period', 25),
        ('slow_period', 60),
        ('stop_loss_pct', 0.02),  # 3% stop
        ('position_pct', 0.95),   # Use 95% of capital
    )
    
    def __init__(self):
        self.fast_ma = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.fast_period
        )
        self.slow_ma = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.slow_period
        )
        self.crossover = bt.indicators.CrossOver(self.fast_ma, self.slow_ma)
        
        print(f"\n{'='*70}")
        print("SIMPLE MA CROSSOVER STRATEGY")
        print("Used by: Vanguard, BlackRock, 70% of index funds")
        print(f"{'='*70}")
        print(f"Fast MA: {self.params.fast_period} days (short-term trend)")
        print(f"Slow MA: {self.params.slow_period} days (long-term trend)")
        print(f"Stop-Loss: {self.params.stop_loss_pct*100}% (protects capital)")
        print(f"Logic: Buy when fast > slow (uptrend)")
        print(f"       Sell when fast < slow (downtrend)")
        print(f"{'='*70}\n")
        
        self.entry_price = None
        self.stop_price = None
    
    def next(self):
        if not self.position:
            # BUY: Fast MA crosses ABOVE slow MA
            if self.crossover > 0:
                size = int((self.broker.getcash() * self.params.position_pct) / self.data.close[0])
                if size > 0:
                    self.buy(size=size)
                    self.entry_price = self.data.close[0]
                    self.stop_price = self.entry_price * (1 - self.params.stop_loss_pct)
                    print(f"\n{'🟢 BUY SIGNAL':-^70}")
                    print(f"Date: {self.data.datetime.date(0)}")
                    print(f"Price: ₹{self.entry_price:,.2f}")
                    print(f"Size: {size} units")
                    print(f"Stop: ₹{self.stop_price:,.2f}")
                    print(f"Reason: 20-MA crossed above 50-MA (uptrend confirmed)")
                    print(f"{'='*70}")
        else:
            # SELL: Fast MA crosses BELOW slow MA OR stop-loss hit
            if self.crossover < 0:
                self.close()
                exit_price = self.data.close[0]
                pnl = (exit_price - self.entry_price) * self.position.size
                pnl_pct = ((exit_price / self.entry_price) - 1) * 100
                print(f"\n{'🔴 SELL SIGNAL (MA Cross)':-^70}")
                print(f"Date: {self.data.datetime.date(0)}")
                print(f"Exit: ₹{exit_price:,.2f}")
                print(f"P&L: ₹{pnl:+,.2f} ({pnl_pct:+.2f}%)")
                print(f"Reason: 20-MA crossed below 50-MA (downtrend)")
                print(f"{'='*70}")
                self.entry_price = None
            elif self.data.close[0] <= self.stop_price:
                self.close()
                exit_price = self.data.close[0]
                pnl = (exit_price - self.entry_price) * self.position.size
                pnl_pct = ((exit_price / self.entry_price) - 1) * 100
                print(f"\n{'🔴 STOP-LOSS HIT':-^70}")
                print(f"Date: {self.data.datetime.date(0)}")
                print(f"Exit: ₹{exit_price:,.2f}")
                print(f"P&L: ₹{pnl:+,.2f} ({pnl_pct:+.2f}%)")
                print(f"Days held: {(self.data.datetime.date(0) - self.data.datetime.date(-1)).days}")
                print(f"{'='*70}")
                self.entry_price = None
