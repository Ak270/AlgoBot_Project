The Two Strategies We Built

##STRATEGY 1: Momentum Breakout (The Failure)##

    What it does (in simple terms):
        Imagine you’re at a party. You notice when suddenly EVERYONE rushes to the snack table. That’s momentum - when lots of people (money) suddenly moves in one direction.
    Our bot tried to do this:
        1.	Watch for breakout: “Is Bank Nifty price going higher than it has in the last 30 days?”
        2.	Check volume: “Are lots of people buying right now?” (like lots of people rushing to that snack table)
        3.	Check trend: “Has the price been generally going up for 100 days?”
        4.	Check RSI: “Is the market not too crazy-high already?”
    If ALL 4 are TRUE → BUY!
    The exit rules:
        •	If price drops 2% → SELL (stop-loss, like “okay, I was wrong, get out!”)
        •	If price rises 6% → SELL (take profit, like “yay, I made money!”)
        •	If 7 days pass → SELL (don’t let money sit doing nothing)
    Why it FAILED:
        •	Win rate: Only won 30% of trades (lost 70%!)
        •	Big problem: When it won, it made small money (₹379 average). When it lost, it lost BIG money (₹523 average).
        •	Result: Lost ₹3,490 overall (-3.5%)
    WHY did this fail?
        Real-world example: Imagine Bank Nifty is like a big ship with 12 banks. If one bank (HDFC) shoots up 10%, but another bank (ICICI) drops 8%, the overall index (ship) barely moves. So “momentum breakouts” don’t work well on indices - they’re too stable!
    Where THIS strategy WORKS:
        •	Individual stocks (like Tesla, which can jump 20% on news)
        •	Commodities (like Gold, which trends for months)
        •	NOT on diversified indices like Bank Nifty

##STRATEGY 2: Moving Average Crossover (The Winner!)##

    What it does (in simple terms):
        Imagine you’re tracking temperature over time:
        •	Fast average: Temperature of last 20 days
        •	Slow average: Temperature of last 50 days
        When the 20-day average crosses ABOVE the 50-day average, it means “things are heating up!” → BUY
        When the 20-day average crosses BELOW the 50-day average, it means “things are cooling down” → SELL
    In stock market terms:
        •	20-day MA (Moving Average): Recent trend (short-term mood)
        •	50-day MA: Longer trend (long-term mood)
        When 20-MA crosses above 50-MA: Market sentiment is turning POSITIVE → BUY
        When 20-MA crosses below 50-MA: Market sentiment is turning NEGATIVE → SELL
    The magic sauce:
        •	Stop-loss at 3%: If you’re wrong, lose only 3% (small loss)
        •	Hold until crossover: If you’re right, hold for months and make 10%, 20%, even 65%! (BIG wins)
    Why it WORKED:
        •	Win rate: Won 46% of trades (almost half!)
        •	Big wins, small losses: When it won, made ₹16,564 average. When it lost, only lost ₹5,676.
        •	Result: Made ₹71,190 profit (+71.19%!)
    WHY did this work?
    Real-world example:
        Think of Bank Nifty like ocean waves. They go up, then down, then up again (mean-reversion). MA crossover catches the BIG waves (trends lasting months) and gets you out before the crash.
    The FIRST trade was perfect:
        •	Entered: June 22, 2020 (right after COVID crash, when market was recovering)
        •	Exited: November 29, 2021 (held for 525 DAYS!)
        •	Profit: +65.73% (₹62,351 on ONE trade!)
    That ONE trade made more money than your entire year’s target!
