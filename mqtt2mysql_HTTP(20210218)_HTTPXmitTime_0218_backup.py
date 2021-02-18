import paho.mqtt.client as mqtt
import http.client, urllib.parse
import html
import pymysql
import numpy
from parse import *
import threading
import time
from datetime import datetime
from datetime import timedelta
#import time
import cryption
from cryptography.fernet import Fernet # symmetric encryption
import socket

MQTT_host = 'localhost'
DB_host = "localhost"
HTTP_target_IP = "172.30.41.11"
HTTP_port = 2010 # HTTP
DB_port = 3306 # MYSQL
MQTT_port = 1883 # MQTT

DB_name = 'seo_cheon'
DB_user = 'root'
DB_passwd = 'root'

nonce = 0 #tranfer number

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


def calcSaturatedVaporPressure(AirTemperature): #온도로 포화수증기압 산출 (mb)

    es = 6.11*pow(10,(7.5*AirTemperature)/(237.3+AirTemperature))
    return es


def calcAbsHumidity(RHumidity,AirTemperature): #mmhg g/m3(질량기준)

    d = (RHumidity/100)*(804/(1+0.00366*AirTemperature))*(calcSaturatedVaporPressure(AirTemperature)/1013.250)

    return d


def enc_msg(msg):
    #global SampleCNT
    rcv_str = msg
    #print("RCV_STR :", rcv_str)

    enc_str = cryption.MyCipher().encrypt_str(rcv_str)
    print("SHA256 ENC:",enc_str)
    #print("SHA256 DEC:",cryption.MyCipher().decrypt_str(enc_str))

    return enc_str


# connect define
def on_connect(client, userdata, flags, rc):
   
    if rc == 0:
        print("connected OK")
    else:
        print("Bad connection Returned code=", rc)


def on_disconnect(client, userdata, flags, rc=0):
    print(" disconnect")
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
# message Parse & write to DB

def on_message(client, userdata, msg):
    global connSql

    #encryption
    enc_str = str(msg.payload.decode("utf-8"))

    print("original:"+enc_str)
    rcv_str=cryption.MyCipher().decrypt_str(enc_str) #decryption

    result1 = rcv_str.split(':') #parse

    # string -> None/int/float
    SensorID          = str(result1[0])
    WindDirection     = convert_zero(casting_string(result1[1]))
    WindSpeed         = convert_zero(casting_string(result1[2]))
    AirTemperature    = casting_string(result1[3])
    AirPressure       = casting_string(result1[4])
    RHumidity         = casting_string(result1[5])
    absHumidity       = casting_string(result1[6])
    Lux               = casting_string(result1[7])
    tVOC              = convert_zero(casting_string(result1[8]))
    eCO2              = casting_string(result1[9])
    rawH2             = casting_string(result1[10])
    rawEthanol        = casting_string(result1[11])
    tVOC_base         = casting_string(result1[12])
    eCO2_base         = casting_string(result1[13])
    WHeightTop        = casting_string(result1[14])
    WHeightBottom     = casting_string(result1[15])
    WHeightMean     = 0
    WDepth            = casting_string(result1[17])
    WTemp             = casting_string(result1[18])
    mc1p0             = casting_string(result1[19])
    mc2p5             = casting_string(result1[20])
    mc4p0             = casting_string(result1[21])
    mc10p0            = casting_string(result1[22])
    nc0p5             = casting_string(result1[23])
    nc1p0             = casting_string(result1[24])
    nc2p5             = casting_string(result1[25])
    nc4p0             = casting_string(result1[26])
    nc10p0            = casting_string(result1[27])
    typPsize          = casting_string(result1[28])
    VBat              = casting_string(result1[29])
    IBat              = casting_string(result1[30])
    RSSI              = casting_string(result1[31])
    

    absHumidity=round(calcAbsHumidity(RHumidity,AirTemperature),2) # Calculate absHumidity-> second decimal place

    # DB insert
    sql = 'insert into PIER_ENV (SensorID,WindDirection, WindSpeed, AirTemperature, AirPressure,RHumidity, absHumidity,Lux,tVOC,eCO2,rawH2,rawEthanol,tVOC_base,eCO2_base,WHeightTop,WHeightBottom,WHeightMean,WDepth,WTemp,mc1p0,mc2p5,mc4p0,mc10p0,nc0p5,nc1p0,nc2p5,nc4p0,nc10p0,typPsize,VBat, IBat,RSSI, RCVTime) values( %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, utc_timestamp() )'\
                % ( ("'"+SensorID+"'"), WindDirection, WindSpeed, AirTemperature, AirPressure, RHumidity, absHumidity, Lux, tVOC, eCO2, rawH2, rawEthanol, eCO2_base, tVOC_base, WHeightTop, WHeightBottom, WHeightMean, WDepth, WTemp, mc1p0, mc2p5, mc4p0, mc10p0, nc0p5, nc1p0, nc2p5, nc4p0, nc10p0, typPsize, VBat, IBat, RSSI)

    print(sql)
    connSql = pymysql.connect(host=DB_host,user=DB_user,password=DB_passwd,db=DB_name,charset='utf8',port=DB_port) #connect DB
    # DB connect

    try:
        with connSql.cursor() as curs:  
            curs.execute(sql)
            
            connSql.commit()
            print("insert success")
    finally:
        pass 
    # MYSQL INSERT



def DBMonitoringHTTPXtime():
    global nonce #Transfer number

    while True:
        connSql = pymysql.connect(host=DB_host,user=DB_user,password=DB_passwd,db=DB_name,charset='utf8',port=DB_port) #mysql connect
        sql = "SELECT * FROM PIER_ENV WHERE RCVTime >= NOW() - INTERVAL 1 DAY AND XMITTime IS NULL ORDER BY RCVTime Asc" # Query : Select data with rcvTime one day ago and XMITTime IS NULL
        try:
            with connSql.cursor() as curs:  
                curs.execute(sql) #excute : Select data with rcvTime one day ago and XMITTime IS NULL
                record = curs.fetchone()  #select one by one               
                
                if record == None: # if no data with rcvTime one day ago and XMITTime IS NULL 
                    print("There is no data to update...sleep") 
                    time.sleep(30) #sleep untill next data inserted
                else :
                    # convert time format to transport
                    logdate = datetime.strptime(str(record[31]),'%Y-%m-%d %H:%M:%S') - timedelta(hours = -9) 
                    logdate.strftime('%Y%m%d%H%M%S')

                    connSql.commit()
                    # make http massage format 
                    httpMsg="{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}".format(record[0],record[1],record[2],record[3],record[4],record[5],record[6],record[7],
                    record[8],record[9],record[10],record[11],record[12],record[13],record[14],record[15],record[16],record[17],record[18],record[19],record[20],record[21],record[22],record[23],record[24],record[25],
                    record[26],record[27],record[28],record[29],record[30],logdate.strftime('%Y%m%d%H%M%S'),'None',record[33]) 
                                      
                    print(httpMsg) 


                    #encryption 
                    enc_str=enc_msg(httpMsg)
                    while True: # break only HTTP succefully transmitted
                        try:
                            nonce=nonce+1 # transfer number 
                            params = urllib.parse.urlencode({'nonce':nonce,'enc':enc_str})
                            headers = {"Content-type": "application/x-www-form-urlencoded",
                                "Accept": "text/plain"}
                            
                            conn.request("POST", "/cgi-bin/query", params, headers) # tranfer 
                            response = conn.getresponse() 
                          
                            if response.status == 200:  # if transport success(200) 
                                print("HTTP transmit success") 
                                updateXmitTimeSql = "UPDATE PIER_ENV SET XMITTime = NOW() WHERE RCVTime = '{}'".format(record[31])  # Query : update( XMITTime NULL -> now )                      
                                curs.execute(updateXmitTimeSql)                       
                                connSql.commit()
                                print("XMITTime update success"+updateXmitTimeSql) 
                                break 
                            elif response.status == 500: # Internal Server error : 10 times transmission attempts                        
                                print("invaild packet")
                                cnt = 0 # reset transmission attempt count
                                while cnt < 10: #  if transmission attempt is less than 10 times .. try Retransmission
                                    cnt = cnt +1 #transmission attempt count increase
                                    params = urllib.parse.urlencode({'nonce':nonce,'enc':enc_str})
                                    headers = {"Content-type": "application/x-www-form-urlencoded",
                                    "Accept": "text/plain"}
                                    conn.request("POST", "/cgi-bin/query", params, headers) # tranfer 
                                    response = conn.getresponse() 
                                    print("try resend..."+str(cnt))
                                    print(response.status)
                                    if response.status == 200: # if transport success(200) 
                                        print("vaild packet successfully transmitted") 
                                        break
                            else :
                                print(response.status, response.reason)                  
                        except: # When http communication fails
                            print("HTTP disconnected..........................")   
                            conn = http.client.HTTPConnection(HTTP_target_IP,port=HTTP_port) # Connection reset
                            
                        finally:
                            conn.close()
                
                  
        finally:
            pass

    #fetch record(one by one) - get rcv time
    #HTTP tansmit
    #receive 200 -> find rcv time and update XmitTime



# Main routine -------------------------------------------------------------------------------------

# DB connect
#connSql = pymysql.connect(host=DB_host,user=DB_user,password=DB_passwd,db=DB_name,charset='utf8',port=DB_port)
#print("mysql connect")

'''
sql = "SELECT * FROM PIER_ENV WHERE RCVTime >= NOW() - INTERVAL 1 DAY AND XMITTime IS NOT NULL ORDER BY RCVTime Asc"
updateXmitTimeSql = "UPDATE PIER_ENV SET XMITTime = NULL WHERE XMITTime IS NOT NULL AND RCVTime >= NOW() - INTERVAL 1 HOUR ORDER BY RCVTime Asc"
with connSql.cursor() as curs: 
    curs.execute(updateXmitTimeSql)   
    connSql.commit()
print("NULL DONE")
'''

# MQTT client function
client = mqtt.Client()
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_subscribe = on_subscribe
client.on_message = on_message

# MQTT : localhost 
client.connect(MQTT_host, MQTT_port)

# MQTT subscribe
client.subscribe('SSC00000', 1)
print("connect")

'''
while True: # break: When the connection is successful
    try:
        conn = http.client.HTTPConnection(HTTP_target_IP,port=HTTP_port) # Connection settings
        conn.request("GET", "/index.html") #transfer
        r1 = conn.getresponse()
        if r1.status == 200: # if transport success(200) 
            print("HTTP connection success")
            break # When the connection is successful
    except:  # When http communication fails
        print("HTTP connection fail")    

print(r1.status, r1.reason) # print connection status

conn.request("GET", "/parrot.spam") #tranfer
r2 = conn.getresponse()

print(r2.status, r2.reason) # print connection status

conn.close()

t = threading.Thread(target=DBMonitoringHTTPXtime,) 
t.start()
'''
client.loop_forever()


