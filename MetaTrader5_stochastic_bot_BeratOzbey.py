from tkinter import Label

import MetaTrader5 as mt5
from MetaTrader5 import TIMEFRAME_M1, TRADE_RETCODE_DONE
import tkinter as tk

ekran = tk.Tk()
ekran.geometry("800x800+300+50")
k_value_text = Label(text="%K",font=("Verdena",40,"bold"),fg="green")
k_value_text.pack()
d_value_text = Label(text="%D",font=("Verdena",40,"bold"),fg="red")
d_value_text.pack()
trade_count = Label(text="Trade Count : 0",font=("Verdena",40,"bold"),fg="blue")
trade_count.pack()
price_text = Label(text="Price : ",font=("Verdena",40,"bold"))
price_text.pack()
klabel = Label(text="%K",font=("Verdena",40,"bold"),fg="green")
klabel.pack()
dlabel = Label(text="%D",font=("Verdena",40,"bold"),fg="red")
dlabel.pack()

print("Meta Trader trading bot by Berat Özbey")

if mt5.initialize() is True:
    print("Succesfully Connected to Terminal")


k_value = None
d_value = None
Price = 0
Total_trades_made = 0

def stochastic_calculation():
    global k_value,d_value,Price,Total_trades_made,k_value26,d_value26
    start_pos = -1
    raw_k_values = []
    for x in range(5):
        start_pos += 1

        #Getting the last 14 rate
        Last_14_Rates = mt5.copy_rates_from_pos("EURUSD",TIMEFRAME_M1,start_pos,14)

        #Getting the current price
        Price = Last_14_Rates[13][4]

        #Finding the Lowest price
        Low = 100000000

        for y in Last_14_Rates:
            if y[3] <= Low:
                Low = y[3]

        #Finding the highest price
        High = -1

        for z in Last_14_Rates:
            if z[2] >= High:
                High = z[2]

        k_value = (Price-Low)/(High-Low)
        k_value = k_value*100
        raw_k_values.append(k_value)
    slowed_k = (raw_k_values[0] + raw_k_values[1] + raw_k_values[2])/3
    slowed_k2 = (raw_k_values[1] + raw_k_values[2] + raw_k_values[3])/3
    slowed_k3 = (raw_k_values[2] + raw_k_values[3] + raw_k_values[4])/3
    d_value = (slowed_k+slowed_k2+slowed_k3)/3
    k_value = slowed_k
    k_value_text.configure(text=f"%K : {str(slowed_k)[:5]}")
    d_value_text.configure(text=f"%D : {str(d_value)[:5]}")
    Price = mt5.symbol_info_tick("EURUSD").bid
    price_text.configure(text=f"Buy : {str(mt5.symbol_info("EURUSD").ask)[:7]}\nSell : {str(mt5.symbol_info("EURUSD").bid)[:7]}")

    sto2699()

    if mt5.positions_total() == 0:
        #Sell Order
        if k_value >= 80 and d_value >= 80:
           # if k_value26 >= 80 and d_value26 >= 80:
            if k_value < d_value:
                if mt5.symbol_info("EURUSD").ask - mt5.symbol_info("EURUSD").bid < 30:
                    sell_order = {
                        "action": mt5.TRADE_ACTION_DEAL,
                        "symbol": "EURUSD",
                        "volume": 1,
                        "type": mt5.ORDER_TYPE_SELL,
                        "price": float(str(mt5.symbol_info("EURUSD").bid)[:7]),
                        "magic": 656565,
                        "comment": "python script open",
                        "sl":float(str(mt5.symbol_info("EURUSD").bid+0.00040)[:7]),
                        "tp":float(str(mt5.symbol_info("EURUSD").bid-0.00040)[:7]),
                        "deviation": 10}
                    trade = mt5.order_send(sell_order)
                    if trade.retcode == TRADE_RETCODE_DONE:
                        print("Successfully Traded")
                        Total_trades_made += 1
                    else:
                        print("Failed to Trade ",trade.retcode)
        #Buy Order
        elif k_value <= 20 and d_value <= 20:
            #if k_value26 <= 20 and d_value26 <= 20:
            if d_value < k_value:
                if mt5.symbol_info("EURUSD").ask - mt5.symbol_info("EURUSD").bid < 30:
                    buy_order = {
                        "action": mt5.TRADE_ACTION_DEAL,
                        "symbol": "EURUSD",
                        "volume": 1,
                        "type": mt5.ORDER_TYPE_BUY,
                        "price": float(str(mt5.symbol_info("EURUSD").ask)[:7]),
                        "magic": 656565,
                        "comment": "python script open",
                        "sl":float(str(mt5.symbol_info("EURUSD").ask-0.00040)[:7]),
                        "tp":float(str(mt5.symbol_info("EURUSD").ask+0.00040)[:7]),
                        "deviation": 10}
                    trade = mt5.order_send(buy_order)
                    if trade.retcode == TRADE_RETCODE_DONE:
                        print("Successfully Traded")
                        Total_trades_made+=1
                    else:
                        print("Failed to Trade ",trade.retcode)
    trade_count.configure(text=f"Trade Count : {Total_trades_made}")
    ekran.after(16, stochastic_calculation)
d_value26 = 0
k_value26 = 0

def sto2699():
    global k_value26, d_value26

    # %D için gereken toplam mum: 26 + 9 + 9 - 2 = 42
    bars_needed = 26 + 9 + 9 - 2
    rates = mt5.copy_rates_from_pos("EURUSD", TIMEFRAME_M1, 0, bars_needed)

    if rates is None or len(rates) < bars_needed:
        k_value26, d_value26 = 0, 0
        return

    # MT5'te en yeni mum en sonda, biz de hesaplamayı ona göre yapacağız
    highs = [r[2] for r in rates]
    lows = [r[3] for r in rates]
    closes = [r[4] for r in rates]

    raw_k_values = []
    # RAW %K (26 periyot)
    for i in range(len(closes) - 26 + 1):
        highest_high = max(highs[i:i + 26])
        lowest_low = min(lows[i:i + 26])
        close_price = closes[i + 25]
        if highest_high != lowest_low:
            k_raw = (close_price - lowest_low) / (highest_high - lowest_low) * 100
        else:
            k_raw = 0
        raw_k_values.append(k_raw)

    # %K_slow (9 periyot SMA)
    k_slow_values = []
    for i in range(len(raw_k_values) - 9 + 1):
        k_slow_values.append(sum(raw_k_values[i:i + 9]) / 9)

    # %D (9 periyot SMA)
    d_values = []
    for i in range(len(k_slow_values) - 9 + 1):
        d_values.append(sum(k_slow_values[i:i + 9]) / 9)

    # Son değerler
    k_value26 = k_slow_values[-1]
    d_value26 = d_values[-1]

    # Ekrana yaz
    klabel.configure(text=f"%K : {round(k_value26, 2)}")
    dlabel.configure(text=f"%D : {round(d_value26, 2)}")


stochastic_calculation()

ekran.mainloop()