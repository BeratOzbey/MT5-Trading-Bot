# MT5 Trading Bot

Python-based automated trading bot for MetaTrader 5. Uses Stochastic Oscillator and RSI indicators to execute trades in forex and crypto markets.

## What Does It Do?

The bot basically does these things:
- Monitors the market in real-time
- Generates buy/sell signals based on Stochastic and RSI indicators
- Opens and closes positions automatically
- Sets stop loss and take profit levels on its own
- Easy to control with the GUI interface

## Requirements

```bash
pip install MetaTrader5
pip install pandas
pip install tkinter
```

You need to have MetaTrader 5 terminal installed on your computer.

## Installation

1. Clone the repo:
```bash
git clone https://github.com/BeratOzbey/MT5-Trading-Bot.git
cd MT5-Trading-Bot
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Open MT5 and enable automated trading (from settings)

4. Run the bot:
```bash
python trading_bot.py
```

## Usage

Through the GUI:
- Select symbols to trade (EURUSD, BTCUSD etc.)
- Adjust parameters (RSI period, Stochastic levels etc.)
- Hit the "Start" button
- The bot will start running and you'll be able to see its trades

## Parameters

Main parameters you can adjust on the bot:

- **RSI Period**: Number of bars used for RSI calculation
- **RSI Upper/Lower Bounds**: Overbought/oversold levels
- **Stochastic K/D Periods**: Stochastic indicator settings
- **Lot Size**: Amount to use per trade
- **SL/TP Points**: Stop loss and take profit distances

## Features

✅ Real-time data analysis  
✅ Technical indicator-based signal generation  
✅ Automatic risk management  
✅ User-friendly interface  
✅ Multi-symbol support  
✅ Adjustable parameters  

## Strategy Logic

The bot works simply like this:

1. Continuously calculates RSI and Stochastic values
2. RSI in oversold zone + Stochastic low → LONG position
3. RSI in overbought zone + Stochastic high → SHORT position
4. Automatically sets SL/TP for each position
5. Stays on standby if conditions aren't met

## Known Limitations

Before using this bot, you should know about these issues:

- **No position tracking after opening** - Once a trade is opened, the bot doesn't track it anymore. It relies entirely on MT5's SL/TP to close positions.
- **Very aggressive refresh rate** - Updates every 16ms (60+ times per second), which can cause unnecessary CPU load and potential MT5 connection issues.
- **Simple float truncation** - Prices are truncated with string slicing `[:7]` instead of proper rounding, which can cause order rejections on some brokers.
- **No error recovery** - If MT5 connection drops or an order fails, the bot doesn't retry or handle the error gracefully.
- **Fixed Stochastic settings** - K=14, K slowing=3, D=3 are hardcoded. Can't be changed without editing the code.
- **No backtesting** - You can't test the strategy on historical data before running it live.
- **Spread check timing** - Checks spread only at order time, not during signal detection.
- **No duplicate trade prevention** - If conditions stay met, it might try to open multiple positions (though MT5 usually prevents this).
- **Basic RSI implementation** - Uses simple RSI calculation without advanced smoothing.

## ⚠️ Important Warnings

- **This bot is for educational purposes.** Test it on a demo account before using it with real money.
- Forex and crypto trading is risky. Don't trade with money you can't afford to lose.
- Past performance doesn't guarantee future results.
- The bot doesn't manage open positions - it just opens them and lets SL/TP handle the rest.
- Watch out for high-frequency updates causing MT5 connection issues.
- Start with small lots at first, learn how the bot works.

## License

MIT License - you can use and develop it however you want.

## Contributing

Don't hesitate to send pull requests. For major changes, open an issue first so we can discuss.

## Contact

Open an issue for questions or get in touch with me.

---

**WARNING:** By using the bot, you accept all risks. I'm not responsible for financial losses. Use it wisely!
