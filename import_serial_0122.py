#!/usr/bin/env python
# https://www.thepoorengineer.com/en/arduino-python-plot/

from threading import Thread, Timer
import serial
import threading
import collections
import matplotlib.pyplot as plt
import matplotlib.animation as animation
#import struct
#import pandas as pd
import numpy as np
from scipy import fftpack
#import math
#from datetime import timedelta
from datetime import datetime
import time

import paho.mqtt.client as mqtt

import pymysql

from parse import *
host = "localhost"


    
wv_min = 0
wv_max = 0
wv_avr = 0

def casting_string(num):
    if num == '':
        return 'None'
    elif int(float(num))==float(num):
        return int(float(num))   
    else:
        return float(num)

def convert_zero(num):
    if num == 'NULL' or num == None :
        return 0
    else:
        return num 

def WAV2MySQL():
    global wv_min, wv_max, wv_avr
    print (datetime.now(),"     - min:",wv_min,"  MAX:", wv_max,"  AVERAGE:", wv_avr)
    
    SensorID          = 'None'
    #print (SensorID)

    WindDirection     = 'NULL'
    WindSpeed         = 'NULL'
    #print (WindDirection, WindSpeed)

    AirTemperature    = 'NULL'
    AirPressure       = 'NULL'
    # print (AirTemperature, AirPressure)

    RHumidity         = 'NULL'
    absHumidity       = 'NULL'
    # print (RHumidity, absHumidity)

    Lux               = 'NULL'
    # print (Lux)

    tVOC              = 'NULL'
    eCO2              = 'NULL'
    rawH2             = 'NULL'
    rawEthanol        = 'NULL'
    tVOC_base         = 'NULL'
    eCO2_base          = 'NULL'
    # print (tVOC, eCO2, rawH2, rawEthanol, tVOC_base, eCO2_base)

    WHeightTop        = casting_string(wv_max)
    WHeightBottom     = casting_string(wv_min)
    WHeightMean       = casting_string(wv_avr)
    WDepth            = 'NULL'
    WTemp             = 'NULL'
    # print (WHeightTop, WHeightBottom, WDepth, WTemp)

    mc1p0             = 'NULL'
    mc2p5             = 'NULL'
    mc4p0             = 'NULL'
    mc10p0            = 'NULL'
    #print (mc1p0, mc2p5,mc4p0, mc10p0)

    nc0p5             = 'NULL'
    nc1p0             = 'NULL'
    nc2p5             = 'NULL'
    nc4p0             = 'NULL'
    nc10p0            = 'NULL'
    typPsize          = 'NULL'
    VBat              = 'NULL'
    IBat              = 'NULL'
    RSSI              = 'NULL'
    #print (VBat, IBat)


    conn = pymysql.connect(host='localhost',user='root',password='root',db='seo_cheon',charset='utf8',port=3306)
    try:
        with conn.cursor() as curs:
                print("----------")
                sql = 'insert into PIER_ENV (SensorID,WindDirection, WindSpeed, AirTemperature, AirPressure,RHumidity, absHumidity,Lux,tVOC,eCO2,rawH2,rawEthanol,tVOC_base,eCO2_base,WHeightTop,WHeightBottom,WHeightMean,WDepth,WTemp,mc1p0,mc2p5,mc4p0,mc10p0,nc0p5,nc1p0,nc2p5,nc4p0,nc10p0,typPsize,VBat, IBat,RSSI, RCVTime) values( %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, utc_timestamp() )'\
                            % ( ("'"+SensorID+"'"), WindDirection, WindSpeed, AirTemperature, AirPressure, RHumidity, absHumidity, Lux, tVOC, eCO2, rawH2, rawEthanol, eCO2_base, tVOC_base, WHeightTop, WHeightBottom,WHeightMean, WDepth, WTemp, mc1p0, mc2p5, mc4p0, mc10p0, nc0p5, nc1p0, nc2p5, nc4p0, nc10p0, typPsize, VBat, IBat, RSSI)

                #print(sql)
                curs.execute(sql)
                conn.commit()
    finally:
        conn.close()
    

class PeriodicTask(object):
    def __init__(self, interval, callback, daemon=True, **kwargs):
        self.interval = interval
        self.callback = callback
        self.daemon   = daemon
        self.kwargs   = kwargs

    def run(self):
        self.callback(**self.kwargs)
        t = Timer(self.interval, self.run)
        t.daemon = self.daemon
        t.start()

class serialPlot:

    def __init__(self, serialPort = 'COM3', serialBaud = 115200, plotLength = 500, dataNumBytes = 9):
        self.port = serialPort
        self.baud = serialBaud
        self.plotMaxLength = plotLength
        self.dataNumBytes = 9 # YHKIM dataNumBytes
        self.rawData = bytearray(9) # YHKIM dataNumBytes)
        self.data = collections.deque([0] * plotLength, maxlen=plotLength)
        self.isRun = True
        self.isReceiving = False
        self.thread = None
        self.plotTimer = 0
        self.previousTimer = 0
        # self.csvData = []

        print('Trying to connect to: ' + str(serialPort) + ' at ' + str(serialBaud) + ' BAUD.')
        try:
            self.serialConnection = serial.Serial(serialPort, serialBaud, timeout=4)
            print('Connected to ' + str(serialPort) + ' at ' + str(serialBaud) + ' BAUD.')
        except:
            print("Failed to connect with " + str(serialPort) + ' at ' + str(serialBaud) + ' BAUD.')

    def readSerialStart(self):
        if self.thread == None:
            self.thread = Thread(target=self.backgroundThread)
            self.thread.start()
            # Block till we start receiving values
            while self.isReceiving != True:
                time.sleep(0.1)

    def getSerialData(self, frame, lines, lineValueText, lineLabel, MinMaxText):
        global wv_min, wv_max, wv_avr

        currentTimer = time.perf_counter()
        self.plotTimer = int((currentTimer - self.previousTimer) * 1000)     # the first reading will be erroneous
        self.previousTimer = currentTimer
        #value,  = struct.unpack('f', self.rawData)    # use 'h' for a 2 byte integer
        value1  = self.rawData[0]    # use 'h' for a 2 byte integer
        value2  = self.rawData[1]    # use 'h' for a 2 byte integer
        if(value1 == 89 and value2 == 89) :
            Dist_Total = (self.rawData[3] * 256) + (self.rawData[2])
            value = 0 - Dist_Total/100

        self.data.append(value)    # we get the latest data point and append it to our array
        x=np.array (self.data)
    
        #print(x.max(), x.min(), x.mean())
        wv_min = x.min()
        wv_max = x.max()
        wv_avr = x.mean()

        lines.set_data(range(self.plotMaxLength), self.data)
        lineValueText.set_text(lineLabel + str(value))
        MinMaxText.set_text('Max/Min : ' +  str(x.max()) + ' / '+ str(x.min()) )
        # self.csvData.append(self.data[-1])

    def backgroundThread(self):    # retrieve data
        time.sleep(1.0)  # give some buffer time for retrieving data
        self.serialConnection.reset_input_buffer()
        while (self.isRun):
            self.serialConnection.readinto(self.rawData)
            self.isReceiving = True

    def close(self):
        self.isRun = False
        self.thread.join()
        self.serialConnection.close()
        print('Disconnected...')
        # df = pd.DataFrame(self.csvData)
        # df.to_csv('/home/rikisenia/Desktop/data.csv')


def main():


    WAIT_TIME_SECONDS = 2
    ticker = threading.Event()

    # portName = 'COM5'     # for windows users
    portName = 'COM4'
    baudRate = 115200
    maxPlotLength = 500
    dataNumBytes = 9        # number of bytes of 1 data point

    s = serialPlot(portName, baudRate, maxPlotLength, dataNumBytes)   # initializes all required variables

    s.readSerialStart()                                               # starts background thread

    # plotting starts below
    pltInterval = 10    # Period at which the plot animation updates [ms]
    xmin = 0
    SampleRate = 5
    xmax = maxPlotLength
    ymin = -(25)
    ymax = 0
    fig = plt.figure()
    ax = plt.axes(xlim=(xmin, xmax), ylim=(float(ymin - (ymax - ymin) / 10), float(ymax + (ymax - ymin) / 10)))
    ax.set_title('Lidar Wave height Read')
    #ax.set_xlabel("time")
    ax.set_xlabel("Sample Count")
    ax.set_ylabel("Lidar Value")

    lineLabel = 'Height'
    MinMaxText = ax.text(0.50, 0.85, '', transform=ax.transAxes)
    lines = ax.plot([], [], label=lineLabel)[0]
    lineValueText = ax.text(0.50, 0.95, '', transform=ax.transAxes)

    anim = animation.FuncAnimation(fig, s.getSerialData, fargs=(lines, lineValueText, lineLabel, MinMaxText), interval=pltInterval)    # fargs has to be a tuple

    plt.legend(loc="upper left")
    plt.grid(True)

    plt.show()


    s.close()

if __name__ == '__main__':
    task = PeriodicTask(interval=30, callback=WAV2MySQL)
    task.run()
    main()
