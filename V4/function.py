from logging import exception
from tridy import *
from function import *
import globals
def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")

def porovnej_crc(input):
   import crcmod
   import crcmod.predefined
   if ( input == ""):
      return
   if ( input == " "):
      return
   # zkratim rezetec o konec vysilani a crc
   remotecrc = input[len(input)-4:len(input)]
   input2 =  input.split("0218")
   input =input[0:len(input)-8]
   STX = bytes.fromhex('0226')
   ETX = bytes.fromhex('0218')
   data = bytes.fromhex(input)
   message = data 
   crc16 = crcmod.predefined.Crc('crc-16-mcrf4xx')
   crc16.update(message)
   calcrc = crc16.hexdigest()
   if ( int(remotecrc,16) == int(calcrc,16)):
         return True
   else: 
         return False


def cal_crc(hexdata):
   import crcmod
   import crcmod.predefined
   if ( hexdata == ""):
      return
   if ( hexdata == " "):
      return
   # zkratim rezetec o konec vysilani a crc
   STX = bytes.fromhex('0226')
   ETX = bytes.fromhex('0218')
   tempdata = hexdata.split("0218")
   hexdata = tempdata[0]
   data = bytes.fromhex(hexdata)
   message = data
   crc16 = crcmod.predefined.Crc('crc-16-mcrf4xx')
   crc16.update(message)
   calcrc = crc16.hexdigest()
   #print ("calcrc: ",calcrc)
   return calcrc


def mess_for_send(CMDPAR,VALPAR):
        PARVALDEC = int(VALPAR)
        PARVALBYT = PARVALDEC.to_bytes(2,'big')
        STX = "0226"
        ETX = "0218"
        FOR = "FFF4"
        PARVAL = PARVALBYT.hex()
        PARVAL = PARVAL.upper()
        CRC = ""
        message = STX + FOR + CMDPAR + PARVAL + ETX + CRC
        CRC = cal_crc(message)
        data = message + CRC
        data = bytes.fromhex(data)
        return data

def load_dz_data(urlcmd,parametr):
         import urllib.request as ur
         import urllib.parse as par
         import json
         html = ur.urlopen(urlcmd).read()
         dzdata = json.loads(html.decode('utf-8'))
        # print ("dzdata: ", dzdata)
         resultData = dzdata["result"][0][parametr]
         if (parametr == "SetPoint"):
            resultData = resultData.split(".")
            resultData =resultData[0]
         if (parametr == "Level"):
            if (resultData == 0):
               resultData = 3
            if (resultData == 10):
               resultData = 2
            if (resultData == 20):
               resultData = 1
            if (resultData == 30):
               resultData = 0

        # print ("TV temp:",resultData)
         return resultData

def send_data_to_domoticz(cmdurl):
           import urllib.request as ur
           import urllib.parse as par
           cmd = cmdurl
           print ("posilam data do domoticz", cmd)
           try:
               page = ur.urlopen(cmd)
           except ur.HTTPError as err:
                if err.code == 404:
                    print ("Page not found!")
                elif err.code == 403:
                    print ("Access denied!")
                else:
                    print("Neco se pokazilo! Error code:", err.code)
           except ur.URLError as err:
                  print ("chyba v pristupu k Domoticz", err.reason)
                  return

def LoadDataFromString(streamdata, pozice,seznam):
   #nactu zarizeni z dat z kotle
   _para = streamdata[pozice:pozice+4]
   dt = seznam[streamdata[pozice:pozice+4]]
   dt = dt.split(",")
   _pop = dt[0]
   _typ = dt[1]
   _idx = dt[2]
   _sndTo = dt[3]
   _dzload = ""
   return (_para,_pop,_typ,_idx,_sndTo,_dzload)

def writeFile(filepatch,data):
   f = open(filepatch, "a")
   f.write(data)
   f.close()

def loadSetupFile(filepatch):
   try: 
      f = open(filepatch,"r")
   except:
      print("soubor:",filepatch,"nelze otevrit")
      exit()
   return f.read()

def zobrazData(odkud):
  for i in odkud:
      fi = i.dzCmdUrl()
      val = str(i.value)
      lastval = str(i.LastValue)
      print (i.para,"-value-",val.ljust(7),"-Last Value-",lastval.ljust(7),"-", i.popis,)

def posliDataPriZmene(co):
   for i in co:
      if (i.send == "True"):
         if (i.LastValue != i.value):
            tmpdata = i.dzCmdUrl()
            #print ("posilam data:", tmpdata)
            send_data_to_domoticz(tmpdata)
            i.LastValue = i.value

def posliDataMQTTPriZmene(client,topic,msg):
            sendtopic = topic + "/state"
            publish(client,sendtopic,msg)

def posliDzMQTTPriZmene(co,client,topic):
   for i in co:
      if (i.send == "True"):
         if (i.LastValue != i.value):
            msg = i.dzMqttCmd()
            publish(client,topic,msg)
            i.LastValue = i.value

def create_json_str (co):
   data = {}
   for i in co:
      if (i.send == "True"):
         send_data = i.value
         if (i.type == "switch"):
            if (i.value == 0 ):
               send_data = "Off"
            if (i.value == 1 ):
               send_data = "On"
         if (i.para == "15CD"):
            if (i.value == 3):
               send_data  = "leto"
            if (i.value == 2):
               send_data  = "paralelni cerpadla"
            if (i.value == 1):
               send_data  = "Priorita bojler"
            if (i.value == 0):
               send_data = "vytapeni domu"
         if (i.para == "157C"):
            if (i.value == 2):
               send_data = "Topeni"
            elif (i.value == 130):
               send_data = "Dohled"
            elif (i.value == 80):
               send_data = "Udrzovani"
            elif (i.value == 82):
               send_data = "Dohled"
            elif (i.value == 9):
               send_data = "Alarm_Teplota_Neroste"
            elif (i.value == 14):
               send_data = "Alarm:vadny_Snimac_CO"
            elif (i.value == 10):
               send_data = "Alarm:vadny_snimac_podavace" 
            elif (i.value == 49):
               send_data = "Roztopeni"  
            elif (i.value == 39):
               send_data = "Alarm 27"
            elif (i.value == 41):
               send_data = "Alarm 29"  
            elif (i.value == 33):
               send_data = "Dohorely"  
            else:
               send_data = "Alarm: "  + str(i.value)
         data[i.name] = send_data
         
   #json_data = json.dumps(data)
   data = str(data)
   data = data.replace("\'", "\"")
   return data

def upravData(odkud,datahex,hexpara):
   for i in odkud:
      if (i.para == hexpara):
         if (i.para == "157C"):
            data_ven = int(datahex,16)
         elif (i.para == "15A7"):
            if (datahex == "0016"):
               data_ven = "ST-730zPID / ST-755 zPid / ST-450 STALMARK? bez PID? / ST-500"
            elif (datahex == "0007"):
               data_ven = "AG LUX (bez PID) / K1PRv4PZ / ST-755 / K1PRv2"
            elif (datahex == "0013"):
               data_ven = "ST-450zPID"
            elif (datahex == "0015"):
               data_ven = "ST-480"
            elif (datahex == "0009"):
               data_ven = "ST-37rs"
            elif (datahex == "0008"):
               data_ven = "ST-709"
            elif (datahex == "0020"):
               data_ven = "ST-402"
            elif (datahex == "002C"):
               data_ven = "ST?"
            elif (datahex == "0005"):
               data_ven = "ST-48"
            elif (datahex == "0006"):
               data_ven = "TECH / AG LUX"
            elif (datahex == "000A"):
               data_ven = "TECH i3"
         elif (i.para == "159B"):
            data_ven = int(datahex,16)   
         elif (i.para == "16F8" or i.para == "15B7" or i.para == "157D" or i.para == "166E") :
            dataDec = int(datahex,16)
            data_ven = dataDec/10
         elif (i.type != "stav"):
            data_ven = int(datahex,16)
         else:
            data_ven = int(datahex,16)
         i.value = data_ven
         #return ()
         #print (i.para,"-",i.popis,"-",i.value,"-",i.send,"-",i.LastValue,"-", i.idx)

def posli_data_5m(akt_time,last_send_time,time_send,co):
   time_diff = int(akt_time) - int(last_send_time)
   if (time_diff >= time_send):
      for i in co:
         if (i.send == "True"):
            tmpdata = i.dzCmdUrl()
            print ("posilam data:", tmpdata)
            #send_data_to_domoticz(tmpdata)
            i.LastValue = i.value
      last_send_time = akt_time
   return last_send_time

def posli_mqtt_data_5m(akt_time,last_send_time,time_send,topic,client,msg):
   time_diff = int(akt_time) - int(last_send_time)
   if (time_diff >= time_send):
      sendtopic = topic + "/state"
      publish(client,sendtopic,msg)
      last_send_time = akt_time
   return last_send_time

def posli_dz_mqtt_data_5m(akt_time,last_send_time,time_send,co,client,topic):
   time_diff = int(akt_time) - int(last_send_time)
   if (time_diff >= time_send):
      for i in co:
         if (i.send == "True"):
            msg = i.dzMqttCmd()
            publish(client,topic,msg)
      last_send_time = akt_time
   return last_send_time

def dz_online(dzurl):
   import urllib.request as ur
   dzonline = True
   try:
      page = ur.urlopen(dzurl+"json.htm")
   except ur.HTTPError as err:
      if err.code == 404:
         print("stranka nenalezena!")
         dzonline = False
      elif err.code == 403:
         print("pristup odepren!")
         dzonline = False
      elif err.code == 401:
         print("neopravneny pristup!")
         dzonline = False
      else:
         print("Neco je spatne! Error code: ", err.code)
         dzonline = False
   except ur.URLError as err:
      print("Domoticz neni dostupny", err.reason)
      dzonline = False
   return dzonline
      
def loadDzdevice(dzurl):
   print ()

def LastIdxInDomoticz(dzurl):
   import json
   import urllib.request, urllib.error, urllib.parse
   devidx = []
   domoticzurl = dzurl + "json.htm?type=command&param=devices_list"
   request = urllib.request.Request(domoticzurl)
   response = urllib.request.urlopen(request)
   test = response.read()
   json_object = json.loads(test)
   if json_object["status"] == "OK":
      for i in range(len(json_object["result"])):
         idx = json_object["result"][i]["value"]
         devidx.append(int(idx))
   devidx.sort(reverse=True)
   return devidx[0]

def createDomoticzDevice(dzurl,senzorname,sensotype):
   #/json.htm?type=createvirtualsensor&idx=HWIDX&sensorname=SENSORNAME&sensortype=SENSORTYPE
   #http://localhost:1080/json.htm?type=createdevice&idx=2&sensorname=urltestvgrt&devicetype=244&devicesubtype=73&Switchtype=2
   #http://127.0.0.1:1080/json.htm?addjvalue=0&addjvalue2=0&customimage=0&description=&idx=3&name=urltestvgrt&options=&protected=false&strparam1=&strparam2=&switchtype=2&type=setused&used=true
   #http://127.0.0.1:1080/json.htm?addjvalue=0&addjvalue2=0&customimage=0&description=&idx=1&name=urlte+stvgrt&options=TGV2ZWxOYW1lczpsZXRvfFBhcmFsZWxuaSDEjGVycGFkbGF8cHJpb3JpdGEgYm9qbGVyfHZ5dGFwxJtuaSBkb211O0xldmVsQWN0aW9uczp8fHw7U2VsZWN0b3JTdHlsZToxO0xldmVsT2ZmSGlkZGVuOmZhbHNl&protected=false&strparam1=&strparam2=&switchtype=18&type=setused&used=true
   import json
   import urllib.request, urllib.error, urllib.parse
   HWIdx = searchHWIdx(dzurl)
   senzorname = "DKM " + senzorname
   htmlsenzorname = senzorname.replace(" ", "%20")
   if (sensotype == "temp"):
      senstyp = "80"
      domoticzurl = dzurl + "json.htm?type=createvirtualsensor&idx="+ str(HWIdx) +"&sensorname=" + htmlsenzorname + "&sensortype=" + str(senstyp)
   elif (sensotype == "switch"):
      senstyp = "244"
      subtype = "73"
      domoticzurl = dzurl + "json.htm?type=createdevice&idx="+ str(HWIdx) +"&sensorname=" + htmlsenzorname + "&devicetype=" + str(senstyp) + "&devicesubtype=" + subtype
   elif (sensotype == "selswitch"):
      senstyp = "244"
      subtype = "62"
      domoticzurl = dzurl + "json.htm?type=createdevice&idx="+ str(HWIdx) +"&sensorname=" + htmlsenzorname + "&devicetype=" + str(senstyp) + "&devicesubtype=" + subtype
   elif (sensotype == "stav"):
      senstyp = "243"
      subtype = "19"
      domoticzurl = dzurl + "json.htm?type=createdevice&idx="+ str(HWIdx) +"&sensorname=" + htmlsenzorname + "&devicetype=" + str(senstyp) + "&devicesubtype=" + subtype
   elif (sensotype == "proc"):
      senstyp = "243"
      subtype = "6"
      domoticzurl = dzurl + "json.htm?type=createdevice&idx="+ str(HWIdx) +"&sensorname=" + htmlsenzorname + "&devicetype=" + str(senstyp) + "&devicesubtype=" + subtype
   elif (sensotype == "text"):
      senstyp = "243"
      subtype = "19"
      domoticzurl = dzurl + "json.htm?type=createdevice&idx="+ str(HWIdx) +"&sensorname=" + htmlsenzorname + "&devicetype=" + str(senstyp) + "&devicesubtype=" + subtype
   elif (sensotype == "settemp"):
      senstyp = "242"
      subtype = "1"
      domoticzurl = dzurl + "json.htm?type=createdevice&idx="+ str(HWIdx) +"&sensorname=" + htmlsenzorname + "&devicetype=" + str(senstyp) + "&devicesubtype=" + subtype
   request = urllib.request.Request(domoticzurl)
   response = urllib.request.urlopen(request)
   data = response.read()
   data = json.loads(data)
   #print (data)
   #print (data["idx"])
  
   if (response.status == 200):
      print ("zarizeni:", senzorname,"vytvořeno s idx:", data["idx"])
   if (sensotype == "switch"):
      dotaz = dzurl + "json.htm?addjvalue=0&addjvalue2=0&customimage=0&description=&idx=" + data["idx"] + "&name=" + htmlsenzorname + "&options=&protected=false&strparam1=&strparam2=&switchtype=2&type=setused&used=true"
      request = urllib.request.Request(dotaz)
      response = urllib.request.urlopen(request)
   if (sensotype == "selswitch"):
      dotaz = dzurl + "json.htm?addjvalue=0&addjvalue2=0&customimage=0&description=&idx=" + data["idx"] + "&name=" + htmlsenzorname + "&options=TGV2ZWxOYW1lczpsZXRvfFBhcmFsZWxuaSDEjGVycGFkbGF8cHJpb3JpdGEgYm9qbGVyfHZ5dGFwxJtuaSBkb211O0xldmVsQWN0aW9uczp8fHw7U2VsZWN0b3JTdHlsZToxO0xldmVsT2ZmSGlkZGVuOmZhbHNl&protected=false&strparam1=&strparam2=&switchtype=18&type=setused&used=true"
      request = urllib.request.Request(dotaz)
      response = urllib.request.urlopen(request)
   return data["idx"]

def searchIdx(dzurl, findidx):
   import json
   import urllib.request, urllib.error, urllib.parse
   searchidx = False
   devidx = []
   domoticzurl = dzurl + "json.htm?type=command&param=devices_list"
   request = urllib.request.Request(domoticzurl)
   response = urllib.request.urlopen(request)
   test = response.read()
   json_object = json.loads(test)
   if json_object["status"] == "OK":
      for i in range(len(json_object["result"])):
         idx = json_object["result"][i]["value"]
         devidx.append(int(idx))
   devidx.sort(reverse=True)
   for i in range(len(devidx)):
      if (devidx[i] == findidx):
         searchidx = True
   return searchidx
def searchHWIdx(dzurl):
   import json
   import urllib.request, urllib.error, urllib.parse
   dotaz = "json.htm?type=hardware"
   request = urllib.request.Request(dzurl + dotaz)
   response = urllib.request.urlopen(request)
   test = response.read()
   json_object = json.loads(test)
   if (json_object["status"] == "OK"):
      for i in range(len(json_object["result"])):
         if (json_object["result"][i]["Type"] == 15):
            idx = json_object["result"][i]["idx"]
   return idx

def loadDataFromSerial(seru):
   i = seru.readline()
   a = i.hex()
   a = a.upper()
   a.strip()
   print (a)
   return a

# ---------------- mqtt function -------------------------------------------
from paho.mqtt import client as mqtt_client
def connect_mqtt(client_id,username,password,broker,port):
   #from paho.mqtt import client as mqtt_client
   def on_connect(client, userdata, flags, rc):
      if rc == 0:
         print("Connected to MQTT Broker!")
      else:
         print("Failed to connect, return code %d\n", rc)

   client = mqtt_client.Client(client_id)
   if (username != "") or (password != ""):
      client.username_pw_set(username, password)
   client.on_connect = on_connect
   client.connect(broker, port)
   return client

def publish(client,topic,msg):
   result = client.publish(topic, msg)
   # result: [0, 1]
   status = result[0]
   if status == 0:
      print(f"Send `{msg}` to topic `{topic}`")
   else:
      print(f"Failed to send message to topic {topic}")
   

def subscribe(client: mqtt_client,setTopic):
   client.subscribe(setTopic)
   client.on_message = on_message

def on_message(client, userdata, msg):
   print("Received", msg.payload.decode(), "from" ,msg.topic, "topic")
   globals.mqtt_sub_msg = msg.payload.decode()
    
#----------------------------------------------------------------------------
def zpracuj_prijatou_Mqtt_zpravu(zprava,co):
   import json
   if (zprava != ""):
      data = json.loads(zprava)
      for i in co:
         if (i.name in data):
            print (data[i.name])
            try:
               i.value = int(data[i.name])
            except ValueError as verr:
               print ("prijata zprava nejde prevezt na int!", data[i.name], verr)
            except Exception as ex:
               print ("data nelze prevezt na int")
               

def zpracuj_prijatou_DzMqtt_zpravu(zprava,co):
   import json
   if (zprava != ""):
      data = json.loads(zprava)
      idx = str(data["idx"])
      for i in co:
         if (i.idx == idx):
            print (data["name"])
            if (data["stype"] == "Selector Switch"):
               if (data["svalue1"] == "0"):
                  data["svalue1"] = 3
               if (data["svalue1"] == "10"):
                  data["svalue1"] = 2
               if (data["svalue1"] == "20"):
                  data["svalue1"] = 1
               if (data["svalue1"] == "30"):
                  data["svalue1"] = 0   
                  
            if (data["stype"] == "SetPoint"):
               data["svalue1"] = float(data["svalue1"])
               data["svalue1"] = int(data["svalue1"])         
            i.value = data["svalue1"]
            print (i.value)