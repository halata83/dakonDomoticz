#from posixpath import split
import time
import serial
import os
import urllib.request as ur
import urllib.parse as par
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
dzurl = ""
# ------------ load config file-------------------------------
test = str2bool(config["DEFAULT"]["test"])
if (test == True):
    tsend = 5
else:
    tsend = 300
print ("RS reading started...")
#---------------------- set serial ----------------------------------------
if (test == False):
    seru = serial.Serial('/dev/ttyS0', baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS, timeout = 1)
# ------------------ load setup.dat file ---------------------------------
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


# zacnu smycku cteni dat z kotle, v pripade testu je cteni nahrazeno staickymi daty
while True:
        now = time.time()
        akt_time = now
        if (test == False):
            seru.flushInput
            i = seru.readline()
            a = i.hex()
            a = a.upper()
            a = a.strip()
            b = load_rs_data(a)
        else:
            print ("testovani")
            a = "0226FFFA169E572D169F4B28157C0021157D00D2157E0032166E02941616002D158B00001681F83015CD00021620022516210002158900001587000015880000159B000001F60000028E0000029800000299000002450000157F00011610000002FC000001F9000003110000031200000288000002183A22"
            a = "0226FFF816EF000116C2000016F9000016EF000216C2000016F9000016F1000016F2000002185F190226FFF4169E572D169F4B28157C0021157D00D2157E0032166E02C61616002D158B00001681F83015CD00021620171716210003158900001587000015880000159B000001F60000028E000002980000029900000245000002189F020226FFF415A7001516FF000616F800C815B700D21684000002182325"
            a = a.upper()
            a = a.strip()
            b = load_rs_data(a)
#-- zkontroluu CRC prijatych dat když nesouhlasi pokracuju dalsim ctenim ----------------------                                                    
        index = 0
        for i in b:
            a = b[index]
            #print (a)
            crc_cajk = porovnej_crc(a)
            if ( crc_cajk != True ):
                print ("spatne crc")
                index += 1 
                continue
            #-- upravim data do nějakeho normalniho formatu
            y = 0
            for x in range(len(a)):
                parametr = a[y:y+4]
                data = a[y+4:y+8]
                #dataDec = int(a[y+4:y+8],16)
                ukaz_RS_Data(zarizeni,data,parametr)
                y = y + 8
                if (y >= len(a)):
                    break
            #zobrazData(zarizeni)
            
        if (test == True):
            time.sleep(1)
        
