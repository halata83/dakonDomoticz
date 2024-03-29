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
   input = input2[0]
   #remotecrc = input[len(input)]
   STX = bytes.fromhex('0226')
   ETX = bytes.fromhex('0218')
   data = bytes.fromhex(input)
   message = data 
   crc16 = crcmod.predefined.Crc('crc-16-mcrf4xx')
   crc16.update(message)
   calcrc = crc16.hexdigest()
   #print ("localcrc: ",calcrc)
   if ( int(remotecrc,16) == int(calcrc,16)):
         #print ("je to tam")
         return True
   else: 
         #print ("neni")
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
           print ("posilam data do domoticz")
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

def publish(client,topic):
   import time
   msg_count = 0
   while True:
      time.sleep(1)
      msg = f"messages: {msg_count}"
      result = client.publish(topic, msg)
      # result: [0, 1]
      status = result[0]
      if status == 0:
         print(f"Send `{msg}` to topic `{topic}`")
      else:
         print(f"Failed to send message to topic {topic}")
      msg_count += 1

def subscribe(client: mqtt_client,setTopic):
    def on_message(client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")

    client.subscribe(setTopic)
    client.on_message = on_message
#----------------------------------------------------------------------------