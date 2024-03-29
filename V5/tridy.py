class device:
    def __init__(self,name,type,para,url):
        self.idx = 0
        self.name = name
        self.type = type
        self.send = False
        self.value = 0
        self.LastValue = 0
        self.popis = name
        self.para = para
        self.url = url
        self.value_load_on_dz = "NaN"
        self.LastMqttValue = 0
    def dzCmdUrl(self):
        request = ""
        if (self.type == "temp"):
            request = self.url + "json.htm?type=command&param=udevice&idx=" + str(self.idx) + "&nvalue=0&svalue="  + str(self.value)
        if (self.type == "settemp"):
            request = self.url + "json.htm?type=command&param=udevice&idx=" + str(self.idx) + "&nvalue=0&svalue="  + str(self.value)
        if (self.type == "proc"):
            request = self.url + "json.htm?type=command&param=udevice&idx=" + str(self.idx) + "&nvalue=0&svalue="  + str(self.value)
        if (self.type == "text"):
            request = self.url + "json.htm?type=command&param=udevice&idx=" + str(self.idx) + "&nvalue=0&svalue="  + str(self.value)
        if (self.type == "switch"):
            if (self.value == 0 ):
                cmdpar = "Off"
            if (self.value == 1 ):
                cmdpar = "On"
            request = self.url + "json.htm?type=command&param=switchlight&idx=" + str(self.idx) + "&switchcmd=" + cmdpar
        if (self.type == "stav"):
            request = self.url + "json.htm?type=command&param=switchlight&idx=" + str(self.idx) + "&switchcmd=" + str(self.value)
        if (self.para == "15CD"):
            if (self.value == 3):
                request = self.url + "json.htm?type=command&param=switchlight&idx=" +str(self.idx) + "&switchcmd=Set%20Level&level=0"
            if (self.value == 2):
                request = self.url + "json.htm?type=command&param=switchlight&idx=" +str(self.idx) + "&switchcmd=Set%20Level&level=10"
            if (self.value == 1):
                request = self.url + "json.htm?type=command&param=switchlight&idx=" +str(self.idx) + "&switchcmd=Set%20Level&level=20"
            if (self.value == 0):
                request = self.url + "json.htm?type=command&param=switchlight&idx=" +str(self.idx) + "&switchcmd=Set%20Level&level=30"
        if (self.para == "157C"):
            if (self.value == 2):
                request = self.url + "json.htm?type=command&param=udevice&idx=" + str(self.idx) + "&nvalue=0&svalue=Topeni"
            elif (self.value == 130):
                request = self.url + "json.htm?type=command&param=udevice&idx=" + str(self.idx) + "&nvalue=0&svalue=Dohled"
            elif (self.value == 80):
                request = self.url + "json.htm?type=command&param=udevice&idx=" + str(self.idx) + "&nvalue=0&svalue=Udrzovani"
            elif (self.value == 82):
                request = self.url + "json.htm?type=command&param=udevice&idx=" + str(self.idx) + "&nvalue=0&svalue=Dohled"
            elif (self.value == 9):
                request = self.url + "json.htm?type=command&param=udevice&idx=" + str(self.idx) + "&nvalue=0&svalue=Alarm_Teplota_Neroste"
            elif (self.value == 14):
                request = self.url + "json.htm?type=command&param=udevice&idx=" + str(self.idx) + "&nvalue=0&svalue=Alarm:vadny_Snimac_CO"
            elif (self.value == 10):
                request = self.url + "json.htm?type=command&param=udevice&idx=" + str(self.idx) + "&nvalue=0&svalue=Alarm:vadny_snimac_podavace" 
            elif (self.value == 49):
                request = self.url + "json.htm?type=command&param=udevice&idx=" + str(self.idx) + "&nvalue=0&svalue=Roztopeni"  
            elif (self.value == 39):
                request = self.url + "json.htm?type=command&param=udevice&idx=" + str(self.idx) + "&nvalue=0&svalue=Alarm 27"
            elif (self.value == 41):
                request = self.url + "json.htm?type=command&param=udevice&idx=" + str(self.idx) + "&nvalue=0&svalue=Alarm 29"  
            elif (self.value == 33):
                request = self.url + "json.htm?type=command&param=udevice&idx=" + str(self.idx) + "&nvalue=0&svalue=Dohorely"
              elif (self.value == 31):
                request = self.url + "json.htm?type=command&param=udevice&idx=" + str(self.idx) + "&nvalue=0&svalue=Roztopeni"
            else:
                request = self.url + "json.htm?type=command&param=udevice&idx=" + str(self.idx) + "&nvalue=0&svalue=Alarm: "  + str(self.value)
        return request
    def printStat(self):
        print ("domotiz url:",self.url)
        print ("Idx:",self.idx)
        print ("name:",self.name)
        print ("type:",self.type)
        print ("send to DZ:",self.send)
        print ("value",self.value)
        print ("LastValue", self.LastValue)
        print ("popis:",self.popis)
        print ("hex parametr", self.para)
    
    def dzMqttCmd(self):
        dzmqttcmd = ""
        if (self.type == "temp"):
            dzmqttcmd = "{\"idx\" : " + str(self.idx) + ", \"nvalue\" : 0, \"svalue\" : \"" + str(self.value) +"\"}"
        if (self.type == "settemp"):
            dzmqttcmd = "{\"idx\" : " + str(self.idx) + ", \"nvalue\" : 0, \"svalue\" : \"" + str(self.value) +"\"}"
        if (self.type == "proc"):
            dzmqttcmd = "{\"idx\" : " + str(self.idx) + ", \"nvalue\" : 0, \"svalue\" : \"" + str(self.value) +"\"}"
        if (self.type == "switch"):
            if (self.value == 0 ):
                cmdpar = "Off"
            if (self.value == 1 ):
                cmdpar = "On"
            dzmqttcmd = "{\"command\": \"switchlight\", \"idx\":" + str(self.idx) + ", \"switchcmd\": \"" + cmdpar + "\" }"
        if (self.type == "stav"):
            dzmqttcmd = "{\"command\": \"switchlight\", \"idx\":" + str(self.idx) + ", \"switchcmd\": \"" + str(self.value) + "\" }"
        if (self.para == "15CD"):
            if (self.value == 3):
                dzmqttcmd = "{\"command\": \"switchlight\", \"idx\":" + str(self.idx) +", \"switchcmd\": \"Set Level\", \"level\": 0 }"
            if (self.value == 2):
                dzmqttcmd = "{\"command\": \"switchlight\", \"idx\":" + str(self.idx) +", \"switchcmd\": \"Set Level\", \"level\": 10 }"
            if (self.value == 1):
                dzmqttcmd = "{\"command\": \"switchlight\", \"idx\":" + str(self.idx) +", \"switchcmd\": \"Set Level\", \"level\": 20 }"
            if (self.value == 0):
                dzmqttcmd = "{\"command\": \"switchlight\", \"idx\":" + str(self.idx) +", \"switchcmd\": \"Set Level\", \"level\": 30 }"
        if (self.para == "157C"):
            if (self.value == 2):
                dzmqttcmd = "{\"idx\" : " + str(self.idx) + ", \"nvalue\" : 0, \"svalue\" : \"Topeni\"}"
            elif (self.value == 130):
                dzmqttcmd = "{\"idx\" : " + str(self.idx) + ", \"nvalue\" : 0, \"svalue\" : \"Dohled\"}"
            elif (self.value == 80):
                dzmqttcmd = "{\"idx\" : " + str(self.idx) + ", \"nvalue\" : 0, \"svalue\" : \"Udrzovani\"}"
            elif (self.value == 82):
                dzmqttcmd = "{\"idx\" : " + str(self.idx) + ", \"nvalue\" : 0, \"svalue\" : \"Dohled\"}"
            elif (self.value == 9):
                dzmqttcmd = "{\"idx\" : " + str(self.idx) + ", \"nvalue\" : 0, \"svalue\" : \"Alarm:teplota_neroste\"}"
            elif (self.value == 14):
                dzmqttcmd = "{\"idx\" : " + str(self.idx) + ", \"nvalue\" : 0, \"svalue\" : \"Alarm:vadný_snimac_CO\"}"
            elif (self.value == 10):
                dzmqttcmd = "{\"idx\" : " + str(self.idx) + ", \"nvalue\" : 0, \"svalue\" : \"Alarm:vadny_snimac_podavace\"}" 
            elif (self.value == 49):
                dzmqttcmd = "{\"idx\" : " + str(self.idx) + ", \"nvalue\" : 0, \"svalue\" : \"Roztopeni\"}"  
            elif (self.value == 39):
                dzmqttcmd = "{\"idx\" : " + str(self.idx) + ", \"nvalue\" : 0, \"svalue\" : \"Alarm 27\"}"
            elif (self.value == 41):
                dzmqttcmd = "{\"idx\" : " + str(self.idx) + ", \"nvalue\" : 0, \"svalue\" : \"Alarm 29\"}"  
            elif (self.value == 33):
                dzmqttcmd = "{\"idx\" : " + str(self.idx) + ", \"nvalue\" : 0, \"svalue\" : \"Dohorely\"}"  
            else:
                dzmqttcmd = "{\"idx\" : " + str(self.idx) + ", \"nvalue\" : 0, \"svalue\" : \"Alarm:  " + str(self.value) +"\"}"
        return dzmqttcmd
