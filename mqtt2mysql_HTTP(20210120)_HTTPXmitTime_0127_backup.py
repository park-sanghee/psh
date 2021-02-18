import paho.mqtt.client as mqtt
import http.client, urllib.parse
import html
import pymysql
import numpy
from parse import *
import threading
import time
host = "localhost"
target_IP = "172.30.41.11"
portNum = 2010

from datetime import datetime
from datetime import timedelta
#import time
import cryption
from cryptography.fernet import Fernet # symmetric encryption
import socket

nonce = 0

# def run():
#     global sock

#     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock :
#         sock.settimeout(5)
        
#         sock.settimeout(None)
#         print("connedted")
        
            
#         while(True):
#             data = sock.recv(80)
#             print("loooooding.........")
#                 #연결 끊기면 재접속 시도
#             if not data:
#                 break
#             print("lllllll")
#             sock.close()

#             print('disconnected......')
           

class SimpleEnDecrypt:
    def __init__(self, key=None):
        if key is None: 
            key = Fernet.generate_key() 
        self.key = key
        self.f   = Fernet(self.key)

    def encrypt(self, data, is_out_string=True):
        if isinstance(data, bytes):
            ou = self.f.encrypt(data) 
        else:
            ou = self.f.encrypt(data.encode('utf-8')) 
        if is_out_string is True:
            return ou.decode('utf-8') 
        else:
            return ou

    def decrypt(self, data, is_out_string=True):
        if isinstance(data, bytes):
            ou = self.f.decrypt(data) 
        else:
            ou = self.f.decrypt(data.encode('utf-8')) 
        if is_out_string is True:
            return ou.decode('utf-8') 
        else:
            return ou

def enc_msg(msg):
    #global SampleCNT
    rcv_str = msg
    #print("RCV_STR :", rcv_str)

    enc_str = cryption.MyCipher().encrypt_str(rcv_str)
    print("SHA256 ENC:",enc_str)
    #print("SHA256 DEC:",cryption.MyCipher().decrypt_str(enc_str))

    return enc_str


#MQTT define
def on_connect(client, userdata, flags, rc):
   
    if rc == 0:
        print("connected OK")
    else:
        print("Bad connection Returned code=", rc)


def on_disconnect(client, userdata, flags, rc=0):
    print("MQTT disconnect")
    print(str(rc))


def on_subscribe(client, userdata, mid, granted_qos):
    print("subscribed: " + str(mid) + " " + str(granted_qos))

# + casting func : string to none/int/float
# num type is string
def casting_string(num):
    if num == '':
        return 'NULL'
    elif int(float(num))==float(num):
        return int(float(num))   
    else:
        return float(num)


def convert_zero(num):
    if num == 'NULL' or num == None :
        return 0
    else:
        return num    
#MQTT message Parse & write to MongoDB

def on_message(client, userdata, msg):
    global connSql
    print("onmasage")
    enc_str = str(msg.payload.decode("utf-8"))

    print("original::"+enc_str)
    rcv_str=cryption.MyCipher().decrypt_str(enc_str)
    #print("SHA256 DEC:",rcv_str)

    result1 = rcv_str.split(':')

    SensorID          = str(result1[0])
    #print (SensorID)

    WindDirection     = convert_zero(casting_string(result1[1]))
    WindSpeed         = convert_zero(casting_string(result1[2]))
    #print (WindDirection, WindSpeed)

    AirTemperature    = casting_string(result1[3])
    AirPressure       = casting_string(result1[4])
    # print (AirTemperature, AirPressure)

    RHumidity         = casting_string(result1[5])
    absHumidity       = casting_string(result1[6])
    # print (RHumidity, absHumidity)

    Lux               = casting_string(result1[7])
    # print (Lux)

    tVOC              = convert_zero(casting_string(result1[8]))
    eCO2              = casting_string(result1[9])
    rawH2             = casting_string(result1[10])
    rawEthanol        = casting_string(result1[11])
    tVOC_base         = casting_string(result1[12])
    eCO2_base          = casting_string(result1[13])
    # print (tVOC, eCO2, rawH2, rawEthanol, tVOC_base, eCO2_base)

    WHeightTop        = casting_string(result1[14])
    WHeightBottom     = casting_string(result1[15])
    WHeightMean     = 0
    WDepth            = casting_string(result1[17])
    WTemp             = casting_string(result1[18])
    # print (WHeightTop, WHeightBottom, WDepth, WTemp)

    mc1p0             = casting_string(result1[19])
    mc2p5             = casting_string(result1[20])
    mc4p0             = casting_string(result1[21])
    mc10p0            = casting_string(result1[22])
    #print (mc1p0, mc2p5,mc4p0, mc10p0)

    nc0p5             = casting_string(result1[23])
    nc1p0             = casting_string(result1[24])
    nc2p5             = casting_string(result1[25])
    nc4p0             = casting_string(result1[26])
    nc10p0            = casting_string(result1[27])
    typPsize          = casting_string(result1[28])
    VBat              = casting_string(result1[29])
    IBat              = casting_string(result1[30])
    RSSI              = casting_string(result1[31])
    #print (VBat, IBat)

    #print (SensorID,WindDirection, WindSpeed, AirTemperature, AirPressure,RHumidity, absHumidity,Lux,tVOC,eCO2,rawH2,rawEthanol,tVOC_base,eCO2_base,WHeightTop,WHeightBottom,WDepth,WTemp,mc1p0,mc2p5,mc4p0,mc10p0,nc0p5,nc1p0,nc2p5,nc4p0,nc10p0,typPsize,VBat, IBat)
    
    sql = 'insert into PIER_ENV (SensorID,WindDirection, WindSpeed, AirTemperature, AirPressure,RHumidity, absHumidity,Lux,tVOC,eCO2,rawH2,rawEthanol,tVOC_base,eCO2_base,WHeightTop,WHeightBottom,WHeightMean,WDepth,WTemp,mc1p0,mc2p5,mc4p0,mc10p0,nc0p5,nc1p0,nc2p5,nc4p0,nc10p0,typPsize,VBat, IBat,RSSI, RCVTime) values( %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, utc_timestamp() )'\
                % ( ("'"+SensorID+"'"), WindDirection, WindSpeed, AirTemperature, AirPressure, RHumidity, absHumidity, Lux, tVOC, eCO2, rawH2, rawEthanol, eCO2_base, tVOC_base, WHeightTop, WHeightBottom, WHeightMean, WDepth, WTemp, mc1p0, mc2p5, mc4p0, mc10p0, nc0p5, nc1p0, nc2p5, nc4p0, nc10p0, typPsize, VBat, IBat, RSSI)

    #sprintf(msg, "%d", rcv_str , s_time)
    print(sql)
    # conn = pymysql.connect(host='localhost',user='root',password='keti',db='YUNG_HUNG',charset='utf8')
    connSql = pymysql.connect(host='localhost',user='root',password='root',db='seo_cheon',charset='utf8',port=3306)
    #print(2)

    try:
        with connSql.cursor() as curs:  
            curs.execute(sql)
            
            connSql.commit()
            print("insert success")
            #print("MySQL Write Done")
    finally:

        pass #connSql.close()    
    # MYSQL INSERT



def DBMonitoringHTTPXtime():
    global nonce

    #mysqlmonitering->null check
    #connSql = pymysql.connect(host='localhost',user='root',password='root',db='seo_cheon',charset='utf8',port=3306)
   
    while True:
        connSql = pymysql.connect(host='localhost',user='root',password='root',db='seo_cheon',charset='utf8',port=3306)
        sql = "SELECT * FROM PIER_ENV WHERE RCVTime >= NOW() - INTERVAL 1 DAY AND XMITTime IS NULL ORDER BY RCVTime Asc"
        try:
            with connSql.cursor() as curs:  
                curs.execute(sql)
                record = curs.fetchone()                
                
                if record == None:
                    print("There is no data to update...sleep")
                    time.sleep(30) #sleep untill next data insert
                else :
                    logdate = datetime.strptime(str(record[31]),'%Y-%m-%d %H:%M:%S') - timedelta(hours = -9)
                    logdate.strftime('%Y%m%d%H%M%S')
                    connSql.commit()
                    httpMsg="{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}".format(record[0],record[1],record[2],record[3],record[4],record[5],record[6],record[7],
                    record[8],record[9],record[10],record[11],record[12],record[13],record[14],record[15],record[16],record[17],record[18],record[19],record[20],record[21],record[22],record[23],record[24],record[25],
                    record[26],record[27],record[28],record[29],record[30],logdate.strftime('%Y%m%d%H%M%S'),'None',record[33])
                    #print(record[31].strftime('%Y%m%d%H%M%S')) 
                    #print(datetime(record[31],'+9 hours').strftime('%Y%m%d%H%M%S')) 
                                      
                    print(httpMsg) 


                    #encryption 
                    enc_str=enc_msg(httpMsg)
                    while True: # break only HTTP succefully transmitted
                        try:
                            nonce=nonce+1
                            params = urllib.parse.urlencode({'nonce':nonce,'enc':enc_str})
                            headers = {"Content-type": "application/x-www-form-urlencoded",
                                "Accept": "text/plain"}

                            #conn.request("POST", params)
                            conn.request("POST", "/cgi-bin/query", params, headers)
                            response = conn.getresponse()
                            #print(response.status, response.reason)
                            if response.status == 200:
                                print("HTTP transmit success")
                                updateXmitTimeSql = "UPDATE PIER_ENV SET XMITTime = NOW() WHERE RCVTime = '{}'".format(record[31])                       
                                curs.execute(updateXmitTimeSql)                       
                                connSql.commit()
                                print("XMITTime update success"+updateXmitTimeSql)
                                break 
                            elif response.status == 500: # try 10 times                               
                                print("invaild packet")
                                cnt = 0
                                while cnt < 10:
                                    cnt = cnt +1
                                    params = urllib.parse.urlencode({'nonce':nonce,'enc':enc_str})
                                    headers = {"Content-type": "application/x-www-form-urlencoded",
                                    "Accept": "text/plain"}

                                    #conn.request("POST", params)
                                    conn.request("POST", "/cgi-bin/query", params, headers)
                                    response = conn.getresponse()
                                    print("try resend..."+str(cnt))
                                    print(response.status)
                                    if response.status == 200:
                                        print("vaild packet successfully transmitted")
                                        break
                            else :
                                print(response.status, response.reason)                  
                        except:
                            print("HTTP disconnected..........................")   
                            conn = http.client.HTTPConnection(target_IP,port=portNum) #80
                            
                        finally:
                            conn.close()
                
                    #print("MySQL Write Done")
        finally:
            pass#connSql.close()

    #fetch record(one by one) - get rcv time
    #HTTP tansmit
    #receive 200 -> find rcv time and update XmitTime



# Main routine -------------------------------------------------------------------------------------
connSql = pymysql.connect(host='localhost',user='root',password='root',db='seo_cheon',charset='utf8',port=3306)
print("mysql connect")

'''
sql = "SELECT * FROM PIER_ENV WHERE RCVTime >= NOW() - INTERVAL 1 DAY AND XMITTime IS NOT NULL ORDER BY RCVTime Asc"
updateXmitTimeSql = "UPDATE PIER_ENV SET XMITTime = NULL WHERE XMITTime IS NOT NULL AND RCVTime >= NOW() - INTERVAL 1 HOUR ORDER BY RCVTime Asc"
with connSql.cursor() as curs: 
    curs.execute(updateXmitTimeSql)   
    connSql.commit()
print("NULL DONE")
'''

# link mqtt function

client = mqtt.Client()
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_subscribe = on_subscribe
client.on_message = on_message

client.connect('localhost', 1883)
client.subscribe('SSC00000', 1)
print("mqtt connect")


while True:
    try:
        conn = http.client.HTTPConnection(target_IP,port=portNum) #80
        conn.request("GET", "/index.html")
        r1 = conn.getresponse()
        if r1.status == 200:
            print("HTTP connection success")
            break
    except:
        print("HTTP connection fail")    

print(r1.status, r1.reason)
data1 = r1.read()

conn.request("GET", "/parrot.spam")
r2 = conn.getresponse()
print(r2.status, r2.reason)
data2 = r2.read()
conn.close()

t = threading.Thread(target=DBMonitoringHTTPXtime,)
t.start()
client.loop_forever()


