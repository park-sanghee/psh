import sqlite3
import serial
from datetime import datetime
import signal
import threading
import sys
#import pysqlite3
import time
import datetime
from datetime import datetime
import random
#import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt

import json

from parse import *
import cryption
from cryptography.fernet import Fernet # symmetric encryption

#SampleCNT   = 0

MQTT_targetIP = '10.0.0.79'
MQTT_port = 1883
line = [] 

serial_port = '/dev/ttySAC0' 
serial_baud = 115200 

exitThread = False  

SensorID = ""
WindDirection = 0.0
WindSpeed = 0
AirTemperature = 00.00
AirPressure = 00.00
RHumidity = 00.00
absHumidity = 00.00
Lux = 0
tVOC = 0
eCO2 = 0
rawH2 = 0
rawEthanol = 0
tVOC_base = 0
eCO2_base = 0
WHeightTop = 0
WHeightBottom = 0
WHeightMean = 00.00
WDepth = 0
WTemp = 00.00
mc1p0 = 00.00
mc2p5 = 00.00
mc4p0 = 00.00
mc10p0 = 00.00
nc0p5 = 00.00
nc1p0 = 00.00
nc2p5 = 00.00
nc4p0 = 00.00
nc10p0 = 00.00
typPsize = 00.00
Vbat = 00.00
Ibat = 00.00
rssi = 0
timestamp = ""


class SimpleEnDecrypt:
    def __init__(self, key=None):
        if key is None: # 
            key = Fernet.generate_key() #
        self.key = key
        self.f   = Fernet(self.key)

    def encrypt(self, data, is_out_string=True):
        if isinstance(data, bytes):
            ou = self.f.encrypt(data) # 
        else:
            ou = self.f.encrypt(data.encode('utf-8')) 
        if is_out_string is True:
            return ou.decode('utf-8') #  ▒~X▒~Y~X
        else:
            return ou

    def decrypt(self, data, is_out_string=True):
        if isinstance(data, bytes):
            ou = self.f.decrypt(data) #
        else:
            ou = self.f.decrypt(data.encode('utf-8')) # ▒~
        if is_out_string is True:
            return ou.decode('utf-8') #  
        else:
            return ou

def create_table(): #
    pass

    #

def data_entry(): 
    c1.execute("INSERT INTO sensor8data VALUES('Id2004', '0', '100','11.11', '11.11', '11.11', '11.11', '1000', '1000', '1000', '1000', '1000', '1000', '1000', '1000', '1000', '1000','22.22', '22.22', '22.22', '22.22', '22.22', '22.22', '22.22', '22.22', '22.22', '22.22', '22.22', '22.22', '22.22', '')")
    conn.commit() 
    c1.close()
    conn.close()
    print("sample data input : success")

def drop_table(c1): 
    c1.execute('DROP TABLE sensor8data')
    conn.commit()
    c1.close()
    conn.close()



def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("connected OK")
    else:
        print("Bad connection Returned code=", rc)


def on_disconnect(client, userdata, flags, rc=0):
    print(str(rc))


def on_publish(client, userdata, mid):
    print("In on_pub callback mid= ", mid)


#
def handler(signum, frame):
     exitThread = True

# + casting func : string to none/int/float
# num type is string
def casting_string(num):
    if num == '':
        return ''
    elif int(float(num))==float(num):
        return int(float(num))
    else:
        return float(num)

def enc_msg(msg):
    #global SampleCNT
    rcv_str = msg
    print("RCV_STR :", rcv_str)

    enc_str = cryption.MyCipher().encrypt_str(rcv_str)
    print("SHA256 ENC:",enc_str)
    #print("SHA256 DEC:",cryption.MyCipher().decrypt_str(enc_str))

    return enc_str

def parsing_data(data):
    global SensorID
    global WindDirection
    global WindSpeed
    global AirTemperature
    global AirPressure
    global RHumidity
    global absHumidity
    global Lux
    global tVOC
    global eCO2
    global rawH2
    global rawEthanol
    global tVOC_base
    global eCO2_base
    global WHeightTop
    global WHeightBottom
    global WHeightMean
    global WDepth
    global WTemp
    global mc1p0
    global mc2p5
    global mc4p0
    global mc10p0
    global nc0p5
    global nc1p0
    global nc2p5
    global nc4p0
    global nc10p0
    global typPsize
    global Vbat
    global Ibat
    global rssi
    global timestamp

    global c1
    #print(data)
    result2 = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
    #total -> 30

    now = datetime.now()
    data.remove('\r')
    data.remove('\n')

    tmp ="".join(data)
    print(tmp)
 

    result1 = tmp.split(":")

    print(result1)

    j=0
    for i in result1 :
        result2[j]=i
        j+=1



    SensorID = result2[0]


    if SensorID[2:3] == 'C': 
    

        result1[1].replace('\r','')
        result1[1].replace('\x00','')
        result1[1].replace('\0','')


        result1[3].replace('\x00','')
        result1[3].replace(' ','')
        result1[3].replace('\0','')


        WindDirection = casting_string(result1[1])
        WindSpeed = casting_string(result1[2]) #NULL
        AirTemperature = casting_string(result1[3])
        AirPressure = casting_string(result1[4])
        RHumidity = casting_string(result1[5])
        absHumidity = casting_string(result1[6])
        Lux = casting_string(result1[7])
        tVOC = casting_string(result1[8]) #NULL
        eCO2 = casting_string(result1[9])
        rawH2 = casting_string(result1[10])
        rawEthanol = casting_string(result1[11])
        tVOC_base = casting_string(result1[12])
        eCO2_base = casting_string(result1[13])
        WHeightTop = casting_string(result1[14])
        WHeightBottom = casting_string(result1[15])
        WDepth = casting_string(result1[16])
        WTemp = casting_string(result1[17])
        mc1p0 = casting_string(result1[18])
        mc2p5 = casting_string(result1[19])
        mc4p0 = casting_string(result1[20])
        mc10p0 = casting_string(result1[21])
        nc0p5 = casting_string(result1[22])
        nc1p0 = casting_string(result1[23])
        nc2p5 = casting_string(result1[24])
        nc4p0 = casting_string(result1[25])
        nc10p0 = casting_string(result1[26])
        typPsize = casting_string(result1[27])
        Vbat = casting_string(result1[28])
        Ibat = casting_string(result1[29])
        rssi = casting_string(result1[30])
        timestamp = now
        WHeightMean = None

        mqtt_msg1='{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}'.format(SensorID, WindDirection, WindSpeed, AirTemperature, AirPressure, RHumidity, absHumidity, Lux, tVOC, eCO2, rawH2, rawEthanol, tVOC_base, eCO2_base, WHeightTop, WHeightBottom,WHeightMean, WDepth, WTemp, mc1p0, mc2p5, mc4p0, mc10p0, nc0p5, nc1p0, nc2p5, nc4p0, nc10p0, typPsize, Vbat, Ibat, rssi)

        print('\n')
        #print(mqtt_msg1)

        enc_mqtt_msg1=enc_msg(mqtt_msg1)

        client.publish('SSC00000', enc_mqtt_msg1)#topic : IDY000~3
        #client.publish('SSC00000', "hello")#topic : IDY000~3


def readThread(ser):
    global line
    global exitThread
    global c1
    global SensorID
    global WindDirection
    global WindSpeed
    global AirTemperature
    global AirPressure
    global RHumidity
    global absHumidity
    global Lux
    global tVOC
    global eCO2
    global rawH2
    global rawEthanol
    global tVOC_base
    global eCO2_base
    global WHeightTop
    global WHeightBottom
    global WHeightMean
    global WDepth
    global WTemp
    global mc1p0
    global mc2p5
    global mc4p0
    global mc10p0
    global nc0p5
    global nc1p0
    global nc2p5
    global nc4p0
    global nc10p0
    global typPsize
    global Vbat
    global Ibat
    global timestamp
    global rssi

    conn = sqlite3.connect("sensor8data.db")
    c1 = conn.cursor() #cursor

    c1.execute('CREATE TABLE IF NOT EXISTS sensor8data(SensorID TEXT, WindDirection REAL DEFAULT NULL, WindSpeed INT DEFAULT NULL, AirTemperature REAL DEFAULT NULL, AirPressure REAL DEFAULT NULL, RHumidity REAL DEFAULT NULL, absHumidity REAL DEFAULT NULL, Lux INT DEFAULT NULL, tVOC INT DEFAULT NULL, eCO2 INT DEFAULT NULL, rawH2 INT DEFAULT NULL, rawEthanol INT DEFAULT NULL, tVOC_base INT DEFAULT NULL, eCO2_base INT DEFAULT NULL, WHeightTop INT DEFAULT NULL, WHeightBottom INT DEFAULT NULL,WHeightMean REAL DEFAULT NULL, WDepth INT DEFAULT NULL, WTemp REAL DEFAULT NULL, mc1p0 REAL DEFAULT NULL, mc2p5 REAL DEFAULT NULL, mc4p0 REAL DEFAULT NULL, mc10p0 REAL DEFAULT NULL, nc0p5 REAL DEFAULT NULL, nc1p0 REAL DEFAULT NULL, nc2p5 REAL DEFAULT NULL, nc4p0 REAL DEFAULT NULL, nc10p0 REAL DEFAULT NULL, typPsize REAL DEFAULT NULL, Vbat REAL DEFAULT NULL, Ibat REAL DEFAULT NULL, rssi REAL DEFAULT NULL, timestamp TEXT)')

    while not exitThread:

        for c in ser.read():
            
            line.append(chr(c))

            if c == 10: 
                
                parsing_data(line)
#                print(line)
                
                del line[:]

                c1.execute("INSERT INTO sensor8data(SensorID, WindDirection, WindSpeed, AirTemperature, AirPressure, RHumidity, absHumidity, Lux, tVOC, eCO2, rawH2, rawEthanol, tVOC_base, eCO2_base, WHeightTop, WHeightBottom,WHeightMean, WDepth, WTemp, mc1p0, mc2p5, mc4p0, mc10p0, nc0p5, nc1p0, nc2p5, nc4p0, nc10p0, typPsize, Vbat, Ibat, rssi, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (SensorID, WindDirection, WindSpeed, AirTemperature, AirPressure, RHumidity, absHumidity, Lux, tVOC, eCO2, rawH2, rawEthanol, tVOC_base, eCO2_base, WHeightTop, WHeightBottom,WHeightMean, WDepth, WTemp, mc1p0, mc2p5, mc4p0, mc10p0, nc0p5, nc1p0, nc2p5, nc4p0, nc10p0, typPsize, Vbat, Ibat, rssi, timestamp))

                conn.commit()
                print("all done")
                print("\n")


if __name__ == "__main__":

    #time.sleep(15)  -> When running automatically
    ser = serial.Serial(serial_port, serial_baud, timeout=1)
    thread = threading.Thread(target=readThread, args=(ser,))

    thread.start()

    #c.close()
    #conn.close()

#------------------------------------Main---------------------------------------


simpleEnDecrypt = SimpleEnDecrypt()
#-------MQTT-------

client = mqtt.Client()

client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_publish = on_publish


#client.connect('192.168.0.20', 1883)
client.connect(MQTT_targetIP, MQTT_port) 
#network only, not wifi
client.loop_start()

#client.loop_stop()

#client.disconnect()



