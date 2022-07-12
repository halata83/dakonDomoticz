mqtt_sub_msg = "-------------------"
from posixpath import split
import time
import serial
import binascii
import urllib.request
import os
import urllib.request as ur
import urllib.parse as par
import json
import subprocess
import math
from datetime import datetime

from function import *
from tridy import *
from dict import *
import configparser
import globals 
zarizeni = []
last_dev_json_string = ""
globals.initialize()
dirname = os.path.dirname(__file__)
setupfile = os.path.join(dirname, 'setup.dat')
configfile = os.path.join(dirname, 'config.ini') 
config = configparser.ConfigParser()
config.read(configfile)
# ------------ load config file-------------------------------
dzurl = config["DEFAULT"]["domoticzurl"]
useDZhttp = str2bool(config["DEFAULT"]["useDomoticzHttpApi"])
useMQTT = str2bool(config["DEFAULT"]["usemqtt"])
test = str2bool(config["DEFAULT"]["test"])
useDZMqtt = str2bool(config["DEFAULT"]["useDomoticzMqtt"])
if (useMQTT == True) or (useDZMqtt == True):
    broker = config["MQTT"]["mqtt_server_ip"]
    port = int(config["MQTT"]["mqtt_server_port"])
    topic = config["MQTT"]["mqtt_topic"]
    setTopic = topic + "/set"
    dzTopic = config["MQTT"]["domoticz_mqtt_topic_in"]
    dzSetTopic = config["MQTT"]["domoticz_mqtt_topic_out"]
    client_id = "DakonMonitor"
    username = config["MQTT"]["mqtt_username"]
    password = config["MQTT"]["mqtt_password"]
    
#-------------------------------------------------------------

start_time = time.time()
last_time = start_time
last_mqtt_send_time = start_time
last_DZ_mqtt_send_time = start_time
tsend = 5
print ("RS reading started...")
# ------------------- set mqtt -------------------------------
if (useMQTT == True) or (useDZMqtt == True):
    client = connect_mqtt(client_id,username,password,broker,port)
    client.loop_start()
    if (useMQTT == True):
        mqttmsg = subscribe(client,setTopic)
    if (useDZMqtt == True):
        mqttmsg = subscribe(client,dzSetTopic)


#--------------------------------------------------------------
if (test == False):
    seru = serial.Serial('/dev/ttyS0', baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS, timeout = 1)

if os.path.isfile(setupfile):
    print ("setup.dat existuje, načítam zařizeni..")
    dev = loadSetupFile(setupfile)
    dev = dev.split("\n")
    for x in range(len(dev) -1 ):
        tmp = dev[x].split(",")
        stavy = device(tmp[1],tmp[2],tmp[0],dzurl) 
        stavy.send = tmp[4]
        stavy.idx = tmp[3]
        stavy.value_load_on_dz = tmp[5]
        zarizeni.append(stavy)
    print ("hotovo")
    
else:
    print("Setup.dat nebyl nalezen, spuste prosim setup.py v adresaři: ", os.getcwd())
    exit()



while True:
        now = time.time()
        akt_time = now
        if (test == False):
            i = seru.readline()
            a = i.hex()
            a = a.upper()
            a = a.strip()
        else:
            a = "0226FFFA169E572D169F4B28157C0021157D00D2157E0032166E02941616002D158B00001681F83015CD00021620022516210002158900001587000015880000159B000001F60000028E0000029800000299000002450000157F00011610000002FC000001F9000003110000031200000288000002183A22"
            a = a.upper()
            a = a.strip()
#---- otestuju dostupnost domoticz pokud neni pokracuju ve smyccse ----
        if (useDZhttp == True):
            dzonline = dz_online(dzurl)
            #print (dzonline)
            if (dzonline == False):
                continue
            for i in zarizeni:
                if (i.value_load_on_dz == "True"):
                    if (i.type == "settemp") and (useDZhttp == True):
                        i.value = load_dz_data(dzurl+"json.htm?type=devices&rid="+str(i.idx),"SetPoint")
                        i.mess_for_dz = mess_for_send(i.para,i.value)
                        if (i.LastValue != i.value):
                            i.LastValue = i.value
                            print ("odesilam data TV do kotle:", i.value)
                            if (test == False):
                                seru.write(i.mess_for_dz)
                    if (i.type == "selswitch") and (useDZhttp == True):
                        i.value = load_dz_data(dzurl+"json.htm?type=devices&rid="+str(i.idx),"Level")
                        i.mess_for_dz = mess_for_send(i.para,i.value)
                        if (i.LastValue != i.value):
                            i.LastValue = i.value
                            print ("odesilam data TV do kotle:", i.value)
                            if (test == False):
                                seru.write(i.mess_for_dz)
        crc_cajk = porovnej_crc(a)
        if ( crc_cajk != True ):
            print ("spatne crc")
            continue

        y = 0
        for x in range(len(a)):
            parametr = a[y:y+4]
            data = a[y+4:y+8]
            #dataDec = int(a[y+4:y+8],16)
            upravData(zarizeni,data,parametr)
            y = y + 8
            if (y >= len(a)):
                break
        #zobrazData(zarizeni)
        if (useDZhttp == True):
            posliDataPriZmene(zarizeni)
            last_time = posli_data_5m(akt_time,last_time,tsend,zarizeni)
        elif (useMQTT == True):
            dev_json_string = create_json_str(zarizeni)
            if (last_dev_json_string != dev_json_string):
                posliDataMQTTPriZmene(client,topic,dev_json_string)
                last_dev_json_string = dev_json_string
            last_mqtt_send_time = posli_mqtt_data_5m(akt_time,last_mqtt_send_time,tsend,topic,client,dev_json_string)
        elif (useDZMqtt == True):
            posliDzMQTTPriZmene(zarizeni,client,dzTopic)
            last_DZ_mqtt_send_time = posli_dz_mqtt_data_5m(akt_time,last_DZ_mqtt_send_time,tsend,zarizeni,client,dzTopic)
        else:
            zobrazData(zarizeni)
            
        print (globals.mqtt_sub_msg)
        if (useMQTT == True):
            zpracuj_prijatou_Mqtt_zpravu(globals.mqtt_sub_msg,zarizeni)
            globals.mqtt_sub_msg = ""    
        if (useDZMqtt == True):
            zpracuj_prijatou_DzMqtt_zpravu(globals.mqtt_sub_msg,zarizeni)
            globals.mqtt_sub_msg = ""
        time.sleep(1)
        
