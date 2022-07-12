import time
from function import *
from paho.mqtt import client as mqtt_client


broker = '192.168.1.100'
port = 1883
topic = "dakon/monitor"
setTopic = topic + "/set"
# generate client ID with pub prefix randomly
client_id = "DakonMonitor"
username = ''
password = ''


client = connect_mqtt(client_id,username,password,broker,port)
client.loop_start()
subscribe(client,setTopic)
while True:
    #subscribe(client,setTopic)
    publish(client,topic)
    #client.loop_forever()
    


