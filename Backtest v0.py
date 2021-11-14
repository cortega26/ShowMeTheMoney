import pandas as pd
import numpy as np
import datetime
import ssl  # we need to import this library and tweak one setting due to fact we use HTTPS certificate(s)

filepath = "https://www.cryptodatadownload.com/cdd/Binance_ETHUSDT_minute.csv"

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
# inv: amount invested
# stc: safety trades count
# tp: target profit %
# ip: initial price
# pd: price deviation to open safety orders (% from initial order)

def Backtest(tp,bos,fsos,sovs,pd,stc):
    ip = 0 #initial price
    fp = 0 #Final profit for the Backtest Strategy
    stu = 0 #Safety trades used
    #count = 0
    for i in reversed(data):    
        #print(i[1])
        if float(i[5]) > 0 and float(i[6]) > 0:
            low = float(i[5]) #highest price in the interval
            high = float(i[6]) #lowest price in the interval
            cdate = datetime.date(int(i[1][0:4]),int(i[1][5:7]),int(i[1][8:10]))
            ctime = datetime.time(int(i[1][11:13]),int(i[1][14:16]),int(i[1][17:19]))
            cdatetime = datetime.datetime.combine(cdate,ctime)
        else:
            print("Missing values or equal to zero. Program terminated.")
            break
        if ip == 0: #first order
            ip = (low + high) / 2
            inv = bos
            dca = ip
            crypto = bos / ip
            csos = fsos
            date1 = datetime.date(int(i[1][0:4]),int(i[1][5:7]),int(i[1][8:10]))
            time1 = datetime.time(int(i[1][11:13]),int(i[1][14:16]),int(i[1][17:19]))
            datetime1 = datetime.datetime.combine(date1,time1)
            print("Starting date:",datetime1)
        elif high >= dca * ((100 + tp) / 100): #Condition to take profits
            fp += tp/100 * inv
            #print("take profit:",tp/100*inv)
            dca = dca * ((100 + tp) / 100)
            #print("New current DCA:",dca)
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
    elapsed = datetime2 - datetime1
    elapsed_float = elapsed.total_seconds()/86400
    #print(elapsed_float)
    print("Latest date:",datetime2)
    print("Elapsed time:",datetime2-datetime1)
    print("Safe Trades Used in current deal:",stu)
    print("Money currently invested:",inv)
    print("Current DCA:",round(dca,2))
    print("Total profit for the period:",round(fp,2))
    print("Aprox. earnings/day:",round(fp/elapsed_float,2))
    #print(count)


Backtest(2,10,10,1.05,2,30)
