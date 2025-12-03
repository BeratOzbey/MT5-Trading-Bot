from tkinter import Label, Entry, Button
from tkinter.ttk import Combobox

import MetaTrader5 as mt5
from MetaTrader5 import TIMEFRAME_M1, TRADE_RETCODE_DONE, TIMEFRAME_M2, TIMEFRAME_M3, TIMEFRAME_M15, TIMEFRAME_D1, \
    TIMEFRAME_H1, TIMEFRAME_W1, TIMEFRAME_M4, TIMEFRAME_M5, TIMEFRAME_M6, TIMEFRAME_H2, TIMEFRAME_M10, TIMEFRAME_M12, \
    TIMEFRAME_H12, TIMEFRAME_M20, TIMEFRAME_M30, TIMEFRAME_H3, TIMEFRAME_MN1, TIMEFRAME_H4, TIMEFRAME_H6, TIMEFRAME_H8
import tkinter as tk

import ctypes

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

ekran = tk.Tk()
ekran.title("MetaTrader 5 Stochastic + RSI Trading Bot / Berat Ozbey")
ekran.geometry("1000x1100+400+200")
k_value_text = Label(text="%K", font=("Verdena", 40, "bold"), fg="green")
d_value_text = Label(text="%D", font=("Verdena", 40, "bold"), fg="red")
rsi_value_text = Label(text="RSI", font=("Verdena", 40, "bold"), fg="purple")
trade_count = Label(text="Trade Count : 0", font=("Verdena", 40, "bold"), fg="blue")
price_text = Label(text="Price : ", font=("Verdena", 40, "bold"))

print("Meta Trader trading bot by Berat Özbey (with RSI Filter)")

if mt5.initialize():
    print("Successfully Connected to Terminal")
else:
    print("Connection Failed")

k_value = None
d_value = None
rsi_value = None
Price = 0
Total_trades_made = 0
trading_symbol = None
currency_text = Label(text=f"{trading_symbol}", font=("Verdena", 40, "bold"))
trading_time_frame = None
trading_lot_miktari = None
alis_pozisyonu_kac_alti_value = None
satis_pozisyonu_kac_ustu_value = None
take_profit_pip = None
stop_loss_pip = None
trading_spread = None
rsi_alis_seviyesi = None
rsi_satis_seviyesi = None

timeframes = {"1 Minute": TIMEFRAME_M1, "2 Minute": TIMEFRAME_M2, "3 Minute": TIMEFRAME_M3, "4 Minute": TIMEFRAME_M4,
              "5 Minute": TIMEFRAME_M5, "6 Minute": TIMEFRAME_M6, "10 Minute": TIMEFRAME_M10,
              "12 Minute": TIMEFRAME_M12, "15 Minute": TIMEFRAME_M15, "20 Minute": TIMEFRAME_M20,
              "30 Minute": TIMEFRAME_M30,
              "1 Hour": TIMEFRAME_H1, "2 Hour": TIMEFRAME_H2, "3 Hour": TIMEFRAME_H3, "4 Hour": TIMEFRAME_H4,
              "6 Hour": TIMEFRAME_H6, "8 Hour": TIMEFRAME_H8, "12 Hour": TIMEFRAME_H12,
              "1 Day": TIMEFRAME_D1,
              "1 Week": TIMEFRAME_W1,
              "1 Month": TIMEFRAME_MN1}
timeframes_yazilari_listesi = [*timeframes]


def rsi_calculation(close_prices, period=14):
    if len(close_prices) < period + 1:
        return 50
    deltas = [close_prices[i] - close_prices[i - 1] for i in range(1, len(close_prices))]
    gains = [delta if delta > 0 else 0 for delta in deltas]
    losses = [-delta if delta < 0 else 0 for delta in deltas]
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def stochastic_calculation():
    global k_value, d_value, rsi_value, Price, Total_trades_made, trading_symbol, alis_pozisyonu_kac_alti_value, satis_pozisyonu_kac_ustu_value, trading_spread, trading_lot_miktari, trading_time_frame, stop_loss_pip, take_profit_pip, rsi_alis_seviyesi, rsi_satis_seviyesi
    Last_Rates = mt5.copy_rates_from_pos(trading_symbol, trading_time_frame, 0, 50)
    if Last_Rates is None or len(Last_Rates) < 50:
        k_value_text.configure(text="Waiting for MT5 data...")
        d_value_text.configure(text="")
        rsi_value_text.configure(text="")
        ekran.after(500, stochastic_calculation)
        return
    k_period = 14
    k_slowing = 3
    d_period = 3
    raw_k_values = []
    for i in range(len(Last_Rates) - k_period + 1):
        period_data = Last_Rates[i:i + k_period]
        highest_high = max([candle[2] for candle in period_data])
        lowest_low = min([candle[3] for candle in period_data])
        current_close = period_data[-1][4]
        if highest_high - lowest_low != 0:
            raw_k = ((current_close - lowest_low) / (highest_high - lowest_low)) * 100
        else:
            raw_k = 50

        raw_k_values.append(raw_k)
    slowed_k_values = []
    for i in range(len(raw_k_values) - k_slowing + 1):
        slowed_k = sum(raw_k_values[i:i + k_slowing]) / k_slowing
        slowed_k_values.append(slowed_k)
    d_values = []
    for i in range(len(slowed_k_values) - d_period + 1):
        d_val = sum(slowed_k_values[i:i + d_period]) / d_period
        d_values.append(d_val)
    if len(slowed_k_values) > 0 and len(d_values) > 0:
        k_value = slowed_k_values[-1]
        d_value = d_values[-1]
    else:
        k_value = 50
        d_value = 50
    Price = Last_Rates[-1][4]
    close_prices = [candle[4] for candle in Last_Rates]
    rsi_value = rsi_calculation(close_prices, period=14)
    k_value_text.configure(text=f"%K : {str(k_value)[:5]}")
    d_value_text.configure(text=f"%D : {str(d_value)[:5]}")
    rsi_value_text.configure(text=f"RSI : {str(rsi_value)[:5]}")
    price_text.configure(
        text=f"Buy : {str(mt5.symbol_info(trading_symbol).ask)[:7]}\nSell : {str(mt5.symbol_info(trading_symbol).bid)[:7]}")
    if mt5.positions_total() == 0:
        if (k_value >= satis_pozisyonu_kac_ustu_value and
                d_value >= satis_pozisyonu_kac_ustu_value and
                d_value - k_value > 3 and
                rsi_value >= rsi_satis_seviyesi):
            if mt5.symbol_info(trading_symbol).ask - mt5.symbol_info(trading_symbol).bid < trading_spread:
                sell_order = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": trading_symbol,
                    "volume": trading_lot_miktari,
                    "type": mt5.ORDER_TYPE_SELL,
                    "price": float(str(mt5.symbol_info(trading_symbol).bid)[:7]),
                    "magic": 656565,
                    "comment": "python script open",
                    "sl": float(str(mt5.symbol_info(trading_symbol).bid + stop_loss_pip)[:7]),
                    "tp": float(str(mt5.symbol_info(trading_symbol).bid - take_profit_pip)[:7]),
                    "deviation": 10
                }
                trade = mt5.order_send(sell_order)

                if trade is not None:
                    if trade.retcode == TRADE_RETCODE_DONE:
                        print("Successfully Traded")
                        Total_trades_made += 1
                    else:
                        print(f"Failed to Trade, retcode: {trade.retcode}")
                else:
                    print("Failed to send order - order_send returned None")
                    print(f"Last error: {mt5.last_error()}")

        elif (k_value <= alis_pozisyonu_kac_alti_value and
              d_value <= alis_pozisyonu_kac_alti_value and
              k_value - d_value > 3 and
              rsi_value <= rsi_alis_seviyesi):

            if mt5.symbol_info(trading_symbol).ask - mt5.symbol_info(trading_symbol).bid < trading_spread:
                buy_order = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": trading_symbol,
                    "volume": trading_lot_miktari,
                    "type": mt5.ORDER_TYPE_BUY,
                    "price": float(str(mt5.symbol_info(trading_symbol).ask)[:7]),
                    "magic": 656565,
                    "comment": "python script open",
                    "sl": float(str(mt5.symbol_info(trading_symbol).ask - stop_loss_pip)[:7]),
                    "tp": float(str(mt5.symbol_info(trading_symbol).ask + take_profit_pip)[:7]),
                    "deviation": 10
                }
                trade = mt5.order_send(buy_order)

                if trade is not None:
                    if trade.retcode == TRADE_RETCODE_DONE:
                        print("Successfully Traded")
                        Total_trades_made += 1
                    else:
                        print(f"Failed to Trade, retcode: {trade.retcode}")
                else:
                    print("Failed to send order - order_send returned None")
                    print(f"Last error: {mt5.last_error()}")

    trade_count.configure(text=f"Trade Count : {Total_trades_made}")
    ekran.after(16, stochastic_calculation)


def trade_session_baslat():
    global trading_symbol, alis_pozisyonu_kac_alti_value, satis_pozisyonu_kac_ustu_value, trading_spread, trading_lot_miktari, trading_time_frame, stop_loss_pip, take_profit_pip, rsi_alis_seviyesi, rsi_satis_seviyesi
    hatali_ayar = False
    if mt5.symbol_info(parite_entry.get()) is not None:
        trading_symbol = parite_entry.get()
    else:
        hatali_ayar = True
        print(f"Invalid symbol: {parite_entry.get()}")
    if int(alis_pozisyonu_minimum_level_entry_box.get()) > 0 or int(alis_pozisyonu_minimum_level_entry_box.get()) < 100:
        alis_pozisyonu_kac_alti_value = int(alis_pozisyonu_minimum_level_entry_box.get())
    else:
        hatali_ayar = True
    if int(satis_pozisyonu_minimum_level_entry_box.get()) > 0 or int(
            satis_pozisyonu_minimum_level_entry_box.get()) < 100:
        satis_pozisyonu_kac_ustu_value = int(satis_pozisyonu_minimum_level_entry_box.get())
    else:
        hatali_ayar = True
    if int(rsi_alis_entry.get()) > 0 and int(rsi_alis_entry.get()) < 100:
        rsi_alis_seviyesi = int(rsi_alis_entry.get())
    else:
        hatali_ayar = True
        print("Invalid RSI buy level")
    if int(rsi_satis_entry.get()) > 0 and int(rsi_satis_entry.get()) < 100:
        rsi_satis_seviyesi = int(rsi_satis_entry.get())
    else:
        hatali_ayar = True
        print("Invalid RSI sell level")
    if int(islem_icin_maks_spread_entry.get()) > 0:
        trading_spread = int(islem_icin_maks_spread_entry.get())
    else:
        hatali_ayar = True
    if float(lot_entry.get()) > 0:
        trading_lot_miktari = float(lot_entry.get())
    else:
        hatali_ayar = True
    if float(take_profit_entry.get()) > 0 and float(stop_loss_entry.get()) > 0:
        take_profit_pip = float(take_profit_entry.get())
        stop_loss_pip = float(stop_loss_entry.get())
    else:
        hatali_ayar = True
    trading_time_frame = timeframes[timeframe_belirleme_kutucugu.get()]
    if hatali_ayar:
        print("Invalid settings detected! Please check your inputs.")
        return
    stochastic_oscillator_yazisi.destroy()
    satis_pozisyonu_minimum_level_yazisi.destroy()
    satis_pozisyonu_minimum_level_entry_box.destroy()
    alis_pozisyonu_minimum_level_entry_box.destroy()
    alis_pozisyonu_minimum_level_yazisi.destroy()
    timeframe_belirleme_yazisi.destroy()
    timeframe_belirleme_kutucugu.destroy()
    islem_icin_maks_spread_entry.destroy()
    islem_icin_maks_spread_yazisi.destroy()
    take_profit_yazisi.destroy()
    take_profit_entry.destroy()
    stop_loss_yazisi.destroy()
    stop_loss_entry.destroy()
    lot_yazisi.destroy()
    lot_entry.destroy()
    botu_calistir_butonu.destroy()
    parite_yazisi.destroy()
    parite_entry.destroy()
    rsi_alis_yazisi.destroy()
    rsi_alis_entry.destroy()
    rsi_satis_yazisi.destroy()
    rsi_satis_entry.destroy()
    currency_text.configure(text=f"{trading_symbol}")
    currency_text.pack()
    k_value_text.pack()
    d_value_text.pack()
    rsi_value_text.pack()
    trade_count.pack()
    price_text.pack()
    stochastic_calculation()

stochastic_oscillator_yazisi = Label(text="Stochastic Oscillator (14,3,3) + RSI Filter", font=("Verdena", 23, "bold"))
stochastic_oscillator_yazisi.place(anchor="center", relx=0.5, rely=0.08)

satis_pozisyonu_minimum_level_entry_box = Entry(font=("Verdena", 15, "bold"))
satis_pozisyonu_minimum_level_entry_box.place(anchor="center", relx=0.3, rely=0.25, width=250, height=50)

satis_pozisyonu_minimum_level_yazisi = Label(text="Sell when both values\n(K% and D%) are above :",
                                             font=("Verdena", 12, "bold"))
satis_pozisyonu_minimum_level_yazisi.place(anchor="center", relx=0.3, rely=0.18)

alis_pozisyonu_minimum_level_yazisi = Label(text="Buy when both values\n(K% and D%) are below :",
                                            font=("Verdena", 12, "bold"))
alis_pozisyonu_minimum_level_yazisi.place(anchor="center", relx=0.7, rely=0.18)

alis_pozisyonu_minimum_level_entry_box = Entry(font=("Verdena", 15, "bold"))
alis_pozisyonu_minimum_level_entry_box.place(anchor="center", relx=0.7, rely=0.25, width=250, height=50)

# RSI AYARLARI (EKLENDİ)
rsi_alis_yazisi = Label(text="RSI: Buy when below :", font=("Verdena", 12, "bold"))
rsi_alis_yazisi.place(anchor="center", relx=0.3, rely=0.35)

rsi_alis_entry = Entry(font=("Verdena", 15, "bold"))
rsi_alis_entry.place(anchor="center", relx=0.3, rely=0.42, width=250, height=50)
rsi_alis_entry.insert(0, "30")

rsi_satis_yazisi = Label(text="RSI: Sell when above :", font=("Verdena", 12, "bold"))
rsi_satis_yazisi.place(anchor="center", relx=0.7, rely=0.35)

rsi_satis_entry = Entry(font=("Verdena", 15, "bold"))
rsi_satis_entry.place(anchor="center", relx=0.7, rely=0.42, width=250, height=50)
rsi_satis_entry.insert(0, "70")

timeframe_belirleme_yazisi = Label(text="Time Frame :", font=("Verdena", 12, "bold"))
timeframe_belirleme_yazisi.place(anchor="center", relx=0.3, rely=0.52)

timeframe_belirleme_kutucugu = Combobox(ekran, font=("Verdena", 15, "bold"), state="readonly")
timeframe_belirleme_kutucugu.place(anchor="center", relx=0.3, rely=0.59, width=250, height=50)
timeframe_belirleme_kutucugu['values'] = timeframes_yazilari_listesi
timeframe_belirleme_kutucugu.current(0)

islem_icin_maks_spread_yazisi = Label(text="Max Spread :", font=("Verdena", 12, "bold"))
islem_icin_maks_spread_yazisi.place(anchor="center", relx=0.7, rely=0.82)

islem_icin_maks_spread_entry = Entry(font=("Verdena", 15, "bold"))
islem_icin_maks_spread_entry.place(anchor="center", relx=0.7, rely=0.89, width=250, height=50)

take_profit_yazisi = Label(text="Take Profit (In pips) :", font=("Verdena", 12, "bold"))
take_profit_yazisi.place(anchor="center", relx=0.3, rely=0.65, width=250, height=50)

take_profit_entry = Entry(font=("Verdena", 15, "bold"))
take_profit_entry.place(anchor="center", relx=0.3, rely=0.72, width=250, height=50)

stop_loss_yazisi = Label(text="Stop Loss (In pips) :", font=("Verdena", 12, "bold"))
stop_loss_yazisi.place(anchor="center", relx=0.7, rely=0.65, width=250, height=50)

stop_loss_entry = Entry(font=("Verdena", 15, "bold"))
stop_loss_entry.place(anchor="center", relx=0.7, rely=0.72, width=250, height=50)

lot_yazisi = Label(text="Lot :", font=("Verdena", 12, "bold"))
lot_yazisi.place(anchor="center", relx=0.3, rely=0.82, width=250, height=50)

lot_entry = Entry(font=("Verdena", 15, "bold"))
lot_entry.place(anchor="center", relx=0.3, rely=0.89, width=250, height=50)

botu_calistir_butonu = Button(bg="blue", font=("Verdena", 15, "bold"), text="Start the bot", fg="white",
                              command=lambda: trade_session_baslat())
botu_calistir_butonu.place(anchor="center", relx=0.5, rely=0.96, width=250, height=50)

parite_yazisi = Label(text="Currency :", font=("Verdena", 12, "bold"))
parite_yazisi.place(anchor="center", relx=0.7, rely=0.52)

parite_entry = Entry(font=("Verdena", 15, "bold"))
parite_entry.place(anchor="center", relx=0.7, rely=0.59, width=250, height=50)

ekran.mainloop()