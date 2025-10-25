print("="*60)
print("ALGO BOT SETUP TEST")
print("="*60)

# Test 1: Basic Python
print("\n✓ Python 3.11 is working")

# Test 2: Data libraries
try:
    import pandas as pd
    import numpy as np
    print(f"✓ Pandas {pd.__version__} installed")
    print(f"✓ NumPy {np.__version__} installed")
except ImportError as e:
    print(f"✗ Error importing data libraries: {e}")

# Test 3: Plotting
try:
    import matplotlib.pyplot as plt
    print("✓ Matplotlib installed")
except ImportError as e:
    print(f"✗ Error importing matplotlib: {e}")

# Test 4: Yahoo Finance
try:
    import yfinance as yf
    print("✓ yfinance installed (data source ready)")
except ImportError as e:
    print(f"✗ Error importing yfinance: {e}")

# Test 5: Backtrader
try:
    import backtrader as bt
    print("✓ Backtrader installed (backtesting engine ready)")
except ImportError as e:
    print(f"✗ Error importing backtrader: {e}")

# Test 6: Technical Indicators Library
try:
    import ta
    print("✓ ta library installed (technical indicators ready)")
except ImportError as e:
    print(f"✗ Error importing ta library: {e}")


# Test 7: Additional libraries
try:
    import schedule
    import websocket
    import requests
    print("✓ Schedule, WebSocket, Requests installed")
except ImportError as e:
    print(f"✗ Error importing utility libraries: {e}")

# Test 8: Folder structure
import os
folders = ['data', 'strategies', 'backtests', 'results', 'logs']
for folder in folders:
    if os.path.exists(folder):
        print(f"✓ Folder '{folder}/' exists")
    else:
        print(f"✗ Folder '{folder}/' missing")

print("\n" + "="*60)
print("SETUP TEST COMPLETE")
print("="*60)
print("\nIf all items show ✓, you're ready for Day 2!")
print("If any show ✗, review that step above.")
