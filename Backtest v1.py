import pandas as pd
import numpy as np
import datetime
import statistics
import ssl  # we need to import this library and tweak one setting due to fact we use HTTPS certificate(s)

filepath = "https://www.cryptodatadownload.com/cdd/Binance_LTCUSDT_minute.csv"

ssl._create_default_https_context = ssl._create_unverified_context

# Now we want to create a dataframe and use Pandas' to_csv function to read in our file
data = pd.read_csv(filepath, skiprows=1)  # we use skiprows parameter because first row contains our web address

# Finally we convert the dataframe into an array in order to easily iterate thru it
data = np.array(data)


# LABELS
# bos: base order size
# fsos: first safety order size
# csos: current safety order size
# sovs: safety order volume scale
# inv: amount invested + locked safety trade
# stc: safety trades count
# stu: safety trades used
# tp: target profit %
# ip: initial price
# pd: price deviation to open safety orders (% from initial order)
# fp: Total profit for the Backtest Strategy

def Backtest(tp,bos,fsos,sovs,pd,stc,tdays):
    ip = 0 
    fp = 0
    stu = 0
    tm = 0
    count = 0
    tmins = tdays * 60 * 24
    volatility = []
    for i in reversed(data):
        count += 1
        if float(i[5]) > 0 and float(i[6]) > 0 and count >= len(data) - tmins:
            low = float(i[5])  #lowest price in the interval
            high = float(i[6]) #highest price in the interval
            if ip == 0: #first order
                ip = (low + high) / 2
                inv = bos
                dca = ip
                crypto = bos / ip
                csos = fsos
                date1 = datetime.date(int(i[1][0:4]),int(i[1][5:7]),int(i[1][8:10]))
                time1 = datetime.time(int(i[1][11:13]),int(i[1][14:16]),int(i[1][17:19]))
                datetime1 = datetime.datetime.combine(date1,time1)
                datetime3 = datetime1
            elif high >= dca * ((100 + tp) / 100): #Condition to take profits
                fp += tp/100 * inv
                dca *= (100 + tp) / 100
                inv = bos
                crypto = bos / dca
                stu = 0
                ip = dca
                csos = fsos
            elif low <= ip * ((100 - pd * (1 + stu)) / 100) and stu < stc: #Condition to activate safety trade
                crypto += csos / (ip * ((100 - pd * (1 + stu)) / 100))
                inv += csos
                csos *= sovs
                stu += 1
                dca = inv / crypto
            else: #in any other case do nothing
                pass
            date2 = datetime.date(int(i[1][0:4]),int(i[1][5:7]),int(i[1][8:10]))
            time2 = datetime.time(int(i[1][11:13]),int(i[1][14:16]),int(i[1][17:19]))
            datetime2 = datetime.datetime.combine(date2,time2)
            tm += inv
            elapsed2 = datetime2 - datetime1
            if elapsed2.total_seconds() % 86400 == 0:
                low2 = float(i[5])
                high2 = float(i[6])
                #print(time2)
                #print(time2-time1)
            elif int((elapsed2.total_seconds()) + 60) % 86400 == 0:
                diff = round((high2 - low2) / high2 * 100, 2)
                volatility.append(diff)
            else:
                if float(i[5]) < low2:
                    low2 = float(i[5])
                elif float(i[6]) > high2:
                    high2 = float(i[5])
        else:
            print("Missing values or equal to zero. Program terminated.")
            break
            
            
    elapsed = datetime2 - datetime1
    elapsed_float = elapsed.total_seconds() / 86400
    #print(elapsed_float)
    print("Starting date:",datetime1)
    print("Latest date:",datetime2)
    print("Days of Backtesting:",elapsed)
    print("Safe Trades Used in current deal:",stu)
    print("Money currently invested:",round(inv,2))
    print("Current DCA:",round(dca,2))
    print("Total profit for the period:",round(fp,2))
    print("Aprox. earnings/day:",round(fp/elapsed_float,2))
    print("Average money invested:",round(tm/(elapsed_float*24*60),2))
    print("Daily profitability vs. Average money invested: " + str(round((24 * 60 * 100 * fp / tm),2)) + "%")
    #print(volatility)
    print("Mean of daily volatility:", str(round(statistics.mean(volatility),2)) + "%")
    print("")
    
def automate():
    tp=0
    for i in range(1,51):
        tp = float(i/10)
        print("Take profit:",str(tp)+"%")
        Backtest(tp,10,20,1.05,2,30)

Backtest(2,10,10,1.05,2,30,30)

    
#automate()
