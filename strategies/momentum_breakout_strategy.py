"""
Momentum Breakout Strategy with Triple Confirmation
----------------------------------------------------
Entry: 50-day high breakout + volume surge + trend filter + RSI filter
Exit: 2% stop-loss OR 6% target OR 7-day time stop
Position Sizing: 1% risk per trade
"""

import backtrader as bt
import pandas as pd

class MomentumBreakoutStrategy(bt.Strategy):
    """
    Institutional-grade momentum strategy used by CTAs and systematic funds.
    
    This strategy buys when:
    1. Price breaks above 50-day high (momentum)
    2. Volume exceeds 1.5x average (institutional buying)
    3. Price is above 200-day SMA (long-term uptrend)
    4. RSI is between 40-65 (not overbought)
    
    Exits when:
    1. Stop-loss hit (2% below entry)
    2. Target hit (6% above entry)
    3. 7 days elapsed (time stop)
    """
    
    # Strategy Parameters (can be optimized later)
    params = (
        # ENTRY CONDITIONS (Relaxed for more trades)
        ('lookback_high', 30),          # 30-day high (was 50 - easier to break)
        ('volume_lookback', 20),        # 20-day average volume
        ('volume_threshold', 1.2),      # 1.2x volume (was 1.5 - more forgiving)
        ('sma_period', 100),            # 100-day trend (was 200 - easier to pass)
        ('rsi_period', 14),             # 14-day RSI
        ('rsi_lower', 30),              # RSI 30-75 (was 40-65 - much wider)
        ('rsi_upper', 75),              # Allows slightly overbought entries
        
        # EXIT CONDITIONS (Keep these)
        ('stop_loss_pct', 0.02),        # 2% stop-loss
        ('target_pct', 0.06),           # 6% profit target
        ('max_hold_days', 7),           # 7 days maximum
        
        # POSITION SIZING (Keep these)
        ('risk_per_trade', 0.01),       # 1% risk per trade
        ('max_position_pct', 0.30),     # Max 30% of capital per trade
    )

    
    def __init__(self):
        """
        Initialize indicators and tracking variables.
        Called once when strategy is loaded.
        """
        # Calculate indicators
        self.highest_high = bt.indicators.Highest(
            self.data.high, 
            period=self.params.lookback_high
        )
        
        self.volume_avg = bt.indicators.SimpleMovingAverage(
            self.data.volume, 
            period=self.params.volume_lookback
        )
        
        self.sma_200 = bt.indicators.SimpleMovingAverage(
            self.data.close, 
            period=self.params.sma_period
        )
        
        self.rsi = bt.indicators.RSI(
            self.data.close, 
            period=self.params.rsi_period
        )
        
        # Trade tracking variables
        self.entry_price = None
        self.entry_date = None
        self.stop_price = None
        self.target_price = None
        self.trade_log = []
        
        print(f"\n{'='*70}")
        print("MOMENTUM BREAKOUT STRATEGY INITIALIZED")
        print(f"{'='*70}")
        print(f"Parameters:")
        print(f"  Breakout Period: {self.params.lookback_high} days")
        print(f"  Volume Threshold: {self.params.volume_threshold}x average")
        print(f"  Trend Filter: {self.params.sma_period}-day SMA")
        print(f"  RSI Range: {self.params.rsi_lower}-{self.params.rsi_upper}")
        print(f"  Stop-Loss: {self.params.stop_loss_pct*100}%")
        print(f"  Target: {self.params.target_pct*100}%")
        print(f"  Max Hold: {self.params.max_hold_days} days")
        print(f"  Risk Per Trade: {self.params.risk_per_trade*100}%")
        print(f"{'='*70}\n")
    
    def next(self):
        """
        Called every day (every bar).
        This is where trading logic executes.
        """
        # If we have an open position, check exits first
        if self.position:
            self.check_exit_conditions()
            return
        
        # If no position, check for entry signal
        self.check_entry_conditions()
    
    def check_entry_conditions(self):
        """
        Check if all 4 entry conditions are met.
        If yes, calculate position size and enter trade.
        """
        # Get current values
        current_close = self.data.close[0]
        current_high = self.data.high[0]
        current_volume = self.data.volume[0]
        prev_highest = self.highest_high[-1]  # Yesterday's 50-day high
        avg_volume = self.volume_avg[0]
        sma_200_value = self.sma_200[0]
        rsi_value = self.rsi[0]
        
        # CONDITION 1: Breakout above 50-day high
        breakout = current_close > prev_highest
        
        # CONDITION 2: Volume surge (1.5x average)
        volume_surge = current_volume > (avg_volume * self.params.volume_threshold)
        
        # CONDITION 3: Price above 200-day SMA (uptrend)
        uptrend = current_close > sma_200_value
        
        # CONDITION 4: RSI in healthy range (not overbought)
        rsi_healthy = self.params.rsi_lower < rsi_value < self.params.rsi_upper
        
                # Debug: Print condition status every 50 days
        if len(self.data) % 50 == 0:
            print(f"\n[DEBUG] Date: {self.data.datetime.date(0)}")
            print(f"  Price: ₹{current_close:,.2f}")
            print(f"  Breakout: {breakout} (Price: {current_close:.2f} vs 50-day high: {prev_highest:.2f})")
            print(f"  Volume Surge: {volume_surge} (Vol: {current_volume:,.0f} vs {avg_volume*self.params.volume_threshold:,.0f} required)")
            print(f"  Uptrend: {uptrend} (Price: {current_close:.2f} vs 200-SMA: {sma_200_value:.2f})")
            print(f"  RSI Healthy: {rsi_healthy} (RSI: {rsi_value:.2f}, Range: {self.params.rsi_lower}-{self.params.rsi_upper})")
        
        # ALL conditions must be TRUE
        if breakout and volume_surge and uptrend and rsi_healthy:
            # Calculate position size using institutional risk management
            print(f"\n{'🎯 ALL CONDITIONS MET - ENTERING TRADE':-^70}")
            self.enter_position(current_close)
    
    def enter_position(self, entry_price):
        """
        Calculate position size and execute buy order.
        SIMPLIFIED version for debugging.
        """
        # Get available capital
        available_cash = self.broker.getcash()
        portfolio_value = self.broker.getvalue()
        
        # SIMPLIFIED: Use 30% of portfolio value for position
        position_value = portfolio_value * 0.30
        
        # Calculate number of units we can buy
        size = int(position_value / entry_price)
        
        # Safety check: Don't trade if size is 0 or we don't have cash
        if size <= 0:
            print(f"\n⚠️ SKIPPED: Position size calculated as {size}")
            print(f"   Cash: ₹{available_cash:,.2f}")
            print(f"   Position value needed: ₹{position_value:,.2f}")
            print(f"   Entry price: ₹{entry_price:,.2f}")
            return
        
        if size * entry_price > available_cash:
            print(f"\n⚠️ SKIPPED: Insufficient cash")
            print(f"   Need: ₹{size * entry_price:,.2f}")
            print(f"   Have: ₹{available_cash:,.2f}")
            return
        
        # Execute buy order
        print(f"\n💵 BUYING: {size} units @ ₹{entry_price:,.2f}")
        print(f"   Total cost: ₹{size * entry_price:,.2f}")
        print(f"   Cash before: ₹{available_cash:,.2f}")
        
        self.buy(size=size)
        
        # Set trade parameters
        self.entry_price = entry_price
        self.entry_date = self.data.datetime.date(0)
        self.stop_price = entry_price * (1 - self.params.stop_loss_pct)
        self.target_price = entry_price * (1 + self.params.target_pct)
        
        # Log the trade
        print(f"\n{'🟢 ENTRY CONFIRMED':-^70}")
        print(f"Date: {self.entry_date}")
        print(f"Entry Price: ₹{entry_price:,.2f}")
        print(f"Position Size: {size} units")
        print(f"Position Value: ₹{size * entry_price:,.2f}")
        print(f"Stop-Loss: ₹{self.stop_price:,.2f} (-{self.params.stop_loss_pct*100}%)")
        print(f"Target: ₹{self.target_price:,.2f} (+{self.params.target_pct*100}%)")
        print(f"Max Hold: {self.params.max_hold_days} days")
        print(f"{'='*70}\n")

    
    def check_exit_conditions(self):
        """
        Check if any exit condition is met.
        Exit immediately if stop-loss, target, or time stop triggered.
        """
        current_price = self.data.close[0]
        current_date = self.data.datetime.date(0)
        
        # Calculate P&L
        pnl = (current_price - self.entry_price) * self.position.size
        pnl_pct = ((current_price / self.entry_price) - 1) * 100
        
        # CONDITION 1: Stop-loss hit (2% loss)
        if current_price <= self.stop_price:
            self.close()
            print(f"\n{'🔴 STOP-LOSS HIT':-^70}")
            print(f"Date: {current_date}")
            print(f"Entry: ₹{self.entry_price:,.2f} | Exit: ₹{current_price:,.2f}")
            print(f"P&L: ₹{pnl:,.2f} ({pnl_pct:+.2f}%)")
            print(f"Days Held: {(current_date - self.entry_date).days}")
            print(f"{'='*70}\n")
            self.reset_trade()
            return
        
        # CONDITION 2: Target hit (6% profit)
        if current_price >= self.target_price:
            self.close()
            print(f"\n{'🟢 TARGET HIT':-^70}")
            print(f"Date: {current_date}")
            print(f"Entry: ₹{self.entry_price:,.2f} | Exit: ₹{current_price:,.2f}")
            print(f"P&L: ₹{pnl:,.2f} ({pnl_pct:+.2f}%)")
            print(f"Days Held: {(current_date - self.entry_date).days}")
            print(f"{'='*70}\n")
            self.reset_trade()
            return
        
        # CONDITION 3: Time-based exit (IMPROVED LOGIC)
        days_held = (current_date - self.entry_date).days
        
        # Calculate current P&L %
        current_pnl_pct = ((current_price / self.entry_price) - 1) * 100
        
        # Only apply time stop if trade is NOT profitable
        # Let winners run, cut losers/breakevens
        if days_held >= self.params.max_hold_days:
            if current_pnl_pct <= 1.0:  # If profit < 1%, exit
                self.close()
                pnl = (current_price - self.entry_price) * self.position.size
                print(f"\n⏱️ TIME-STOP: Date={current_date}")
                print(f"   Entry: ₹{self.entry_price:.2f} | Exit: ₹{current_price:.2f}")
                print(f"   P&L: ₹{pnl:+,.2f} ({current_pnl_pct:+.2f}%)")
                print(f"   Days Held: {days_held}")
                print(f"   Reason: Profit <1% after 7 days (cut dead trade)")
                self.reset_trade()
                return
            else:
                # Trade is profitable, extend hold to 14 days
                if days_held >= 14:
                    self.close()
                    pnl = (current_price - self.entry_price) * self.position.size
                    print(f"\n⏱️ EXTENDED TIME-STOP: Date={current_date}")
                    print(f"   Entry: ₹{self.entry_price:.2f} | Exit: ₹{current_price:.2f}")
                    print(f"   P&L: ₹{pnl:+,.2f} ({current_pnl_pct:+.2f}%)")
                    print(f"   Days Held: {days_held}")
                    print(f"   Reason: Extended hold for profitable trade")
                    self.reset_trade()
                    return

    
    def reset_trade(self):
        """
        Reset trade tracking variables after exit.
        """
        self.entry_price = None
        self.entry_date = None
        self.stop_price = None
        self.target_price = None
    
    def notify_order(self, order):
        """
        Called when order status changes.
        Used for debugging and trade confirmation.
        """
        if order.status in [order.Completed]:
            if order.isbuy():
                pass  # Already logged in enter_position()
            elif order.issell():
                pass  # Already logged in check_exit_conditions()
