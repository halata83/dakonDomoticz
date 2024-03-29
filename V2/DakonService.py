import os
import time
import serial
import binascii
import urllib.request as ur
import urllib.parse as par
import json
import subprocess
import math
from datetime import datetime
from function import porovnej_crc
from function import cal_crc
from function import mess_for_send
from function import load_dz_data
from function import send_data_to_domoticz
dzurl = "http://192.168.1.107:1080/"
url_json = dzurl + "json.htm?type=command&param=udevice&idx="
url_json2 = dzurl + "json.htm?type=command&param=switchlight&idx="
sent = 0
lastTV = 0
lastTUV = 0
lastRezCer = ""

# ----- domoticz idx ------
setTVidx = 676
actTVidx = 171
setTUVidx = 678
actTUVidx = 172
ventStatIdx = 629
ventOtidx = 633
cerpTVidx = 630
cerTUVidx = 631
podavacidx = 632
cerpStatidx = 630
procPaliva = 637
casPaliva = 638
tempPodavacidx = 174
tempSpalinidx = 636
statKotle = 635
#---------------------------
print ("prijimam data po RS...")

seru = serial.Serial('/dev/ttyS0', baudrate=9600,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    bytesize=serial.EIGHTBITS, timeout = 1)

while True:
        now = datetime.now()
        i = seru.readline()
        a = i.hex()
#---- otestuju dostupnost domoticz pokud neni pokracuju ve smyccse ----
        try:
           page = ur.urlopen(dzurl+"json.htm?")
        except ur.HTTPError as err:
           if err.code == 404:
               print("stranka nenalezena!")
           elif err.code == 403:
               print("pristup odepren!")
           else:
               print("Neco je spatne! Error code: ", err.code)
        except ur.URLError as err:
            print("Domoticz neni dostupny", err.reason)
            continue
#---- nactu data z domoticz --------------------------------------------
        TVsetTemp = load_dz_data(dzurl+'json.htm?type=devices&rid='+str(setTVidx),"SetPoint")
#        print (TVsetTemp)
        TUVsetTemp = load_dz_data(dzurl+'json.htm?type=devices&rid='+str(setTUVidx),"SetPoint")
#        print (TUVsetTemp)
        CerpStat = load_dz_data(dzurl+'json.htm?type=devices&rid='+str(cerpStatidx),"Level")
#        print (CerpStat)
# vytvorim zprávy ------------------------------------------------------
        CMDPARTUV = "028E"
        CMDPARTV = "01F6"
        CMDPARCerpStat = "0245"
        dataTUV = mess_for_send(CMDPARTUV,TUVsetTemp)
        dataTV = mess_for_send(CMDPARTV,TVsetTemp)
        dataCerp = mess_for_send(CMDPARCerpStat,CerpStat)
#        print (dataTUV)
#        print (dataTV)
#        print (dataCerp)
#        print (lastTV, TVsetTemp)
#        print (lastTUV, TUVsetTemp)
#        print (lastRezCer,CerpStat)
#--- poslu do kotle ---------------------------------------------------
        if (lastTV != TVsetTemp):
            lastTV = TVsetTemp
            print ("odesilam data TV do kotle:", dataTV)
            seru.write(dataTV)
            #time.sleep(0.5)
        if (lastTUV != TUVsetTemp):
            lastTUV = TUVsetTemp
            print ("odesilam data TUV do kotle:", dataTUV)
            seru.write(dataTV)
            #time.sleep(0.5)
        if (lastRezCer != CerpStat):
            lastRezCer = CerpStat
            print ("odesilam data cerp do kotle:", dataCerp)
            seru.write(dataCerp)
            #time.sleep(0.5)
        crc_cajk = porovnej_crc(a)
        if ( crc_cajk != True ):
             #print ("spatne crc")
             continue

        if( a.find('1681',8,-8) > -1):
            os.system('clear')
            print(now)
            tempOutsideActualHex =  a[a.find('1681',8,-8)+4:a.find('1681',8,-8)+8]
            tempOutsideActualDec  = int(tempOutsideActualHex,16)   
            #print(" -----------  tempOutsideActualDec ---------------------")
            print("tempOutsideActualDec:" ,tempOutsideActualDec/10 )
            if (tempOutsideActualDec/10 > -50 and tempOutsideActualDec/10 < 50):
                # use Domoticz JSON url to update
                cmd = url_json  + str(16) + "&nvalue=0&svalue=" + str(tempOutsideActualDec/10)       
                #urllib.request.urlopen(cmd)
                #print(cmd)
                #print("-------------------------------------------------------")
                
        if( a.find('157e',8,-8) > -1):
            tempTVSetpHex =  a[a.find('157e',8,-8)+4:a.find('157e',8,-8)+8]
            tempTVSetpDec = int(tempTVSetpHex,16)
            #print("------------------  tempTVSetpDec--------------------------")
            print("tempTVSetp: ",tempTVSetpDec)
            # use Domoticz JSON url to update
            cmd = url_json  + str(setTVidx) + "&nvalue=0&svalue=" + str(tempTVSetpDec)       
            send_data_to_domoticz(cmd)
            #print(cmd)
            #print("-------------------------------------------------------")
            
        if( a.find('157d',8,-8) > -1):
            tempTVActualHex =  a[a.find('157d',8,-8)+4:a.find('157d',8,-8)+8]
            tempTVActualDec = int(tempTVActualHex,16)
            #print("-------------  tempTVActualDec --------------------------")
            print("tempTVActual: ",tempTVActualDec/10)
            # use Domoticz JSON url to update
            cmd = url_json  + str(actTVidx) + "&nvalue=0&svalue=" + str(tempTVActualDec/10)       
            #send_data_to_domoticz(cmd)
            #print(cmd)
            #print("-------------------------------------------------------")
            
        if( a.find('1616',8,-8) > -1):
            tempTuvSetpHex =  a[a.find('1616',8,-8)+4:a.find('1616',8,-8)+8]
            tempTuvSetpDec = int(tempTuvSetpHex,16)
            #print("-------------- tempTuvSetpDec ----------------------------")
            print("tempTuvSetp: ",tempTuvSetpDec)
            # use Domoticz JSON url to update
            cmd = url_json  + str(setTUVidx) + "&nvalue=0&svalue=" + str(tempTuvSetpDec)       
            send_data_to_domoticz(cmd)
            #print(cmd)
            #print("-------------------------------------------------------")
            
        if( a.find('167f',8,-8) > -1):
            tempVentiluSetpHex =  a[a.find('167f',8,-8)+4:a.find('167f',8,-8)+8]
            tempVentiluSetpDec = int(tempVentiluSetpHex,16)
            #print("-----------  tempVentiluSetpDec ---------------------------")
            print("tempVentiluSetp: " ,tempVentiluSetpDec)
            # use Domoticz JSON url to update
            cmd = url_json  + str(39) + "&nvalue=0&svalue=" + str(tempVentiluSetpDec)       
            #send_data_to_domoticz(cmd)
            #print(cmd)
            #print("-------------------------------------------------------")
            
        if( a.find('166e',8,-8) > -1):
            tempTuvActualHex =  a[a.find('166e',8,-8)+4:a.find('166e',8,-8)+8]
            tempTuvActualDec = int(tempTuvActualHex,16)
            #print("-----------  tempTuvActualDec -------------------------")
            print("tempTuvActual: ", tempTuvActualDec/10)
            # use Domoticz JSON url to update
            cmd = url_json  + str(actTUVidx) + "&nvalue=0&svalue=" + str(tempTuvActualDec/10)       
            send_data_to_domoticz(cmd)
            #print(cmd)
            #print("-------------------------------------------------------")
            
        if( a.find('1614') >-1):
            tempVentiluActualHex =  a[a.find('1614')+4:a.find('1614')+8]
            tempVentiluActualDec = int(tempVentiluActualHex,16)
            #print("----------  tempVentiluActualDec -----------------------")
            print("tempVentiluActual: ", tempVentiluActualDec)
            # use Domoticz JSON url to update
            cmd = url_json  + str(13) + "&nvalue=0&svalue=" + str(tempVentiluActualDec/10)       
            #send_data_to_domoticz(cmd)
            #print(cmd)
            #print("-------------------------------------------------------")
            
        if( a.find('16c1',8,-8) > -1):
            tempZpateckyActualHex =  a[a.find('16c1',8,-8)+4:a.find('16c1',8,-8)+8]
            tempZpateckyActualDec = int(tempZpateckyActualHex,16)
            #print("---------  tempZpateckyActualDec -----------------------")
            print("tempZpateckyActual: ", tempZpateckyActualDec)
            # use Domoticz JSON url to update
            cmd = url_json  + str(14) + "&nvalue=0&svalue=" + str(tempZpateckyActualDec/10)       
            send_data_to_domoticz(cmd)
            #print(cmd)
            #print("-------------------------------------------------------")
            
        if( a.find('1588') > -1):
            ventilatorHex =  a[a.find('1588')+4:a.find('1588')+8]
            ventilatorDec = int(ventilatorHex,16)
            #print(" --------  ventilatorDec ------------------------------------")
            print("ventilator: " ,ventilatorDec)
            # use Domoticz JSON url to update
            if (ventilatorDec == 1):
                cmd = url_json2  + str(ventStatIdx) + "&switchcmd=On"
            else:
                cmd = url_json2  + str(ventStatIdx) + "&switchcmd=Off"
            send_data_to_domoticz(cmd)
            #print(cmd)
            #print("-------------------------------------------------------")
            
        if( a.find('158b') > -1):
            cerpadloTuvHex =  a[a.find('158b')+4:a.find('158b')+8]
            cerpadloTuvDec = int(cerpadloTuvHex,16)
            #print("---------  cerpadloTuvDec  -------------------------------")
            print("cerpadloTuv: " ,cerpadloTuvDec)
            # use Domoticz JSON url to update
            if (cerpadloTuvDec == 1):
                cmd = url_json2  + str(cerTUVidx) + "&switchcmd=On"
            else:
                cmd = url_json2  + str(cerTUVidx) + "&switchcmd=Off"
            send_data_to_domoticz(cmd)
            #print(cmd)
            #print("-------------------------------------------------------")
            
        if( a.find('1589') > -1):
            cerpadloTVHex =  a[a.find('1589')+4:a.find('1589')+8]
            cerpadloTVDec = int(cerpadloTVHex,16)
            #print("---------  cerpadloTVDec  --------------------------------")
            print("cerpadloTV: ",cerpadloTVDec)
             # use Domoticz JSON url to update
            if (cerpadloTVDec == 1):
                cmd = url_json2  + str(cerpTVidx) + "&switchcmd=On"
            else:
                cmd = url_json2  + str(cerpTVidx) + "&switchcmd=Off"      
            send_data_to_domoticz(cmd)
            #print(cmd)
            #print("-------------------------------------------------------")
            
        if( a.find('1587') > -1):
            podavacHex =  a[a.find('1587')+4:a.find('1587')+8]
            podavacDec = int(podavacHex,16)
            #print("----------  podavacDec  ----------------------------")
            print("podavac: ", podavacDec)
             # use Domoticz JSON url to update
            if (podavacDec == 1):
                cmd = url_json2  + str(podavacidx) + "&switchcmd=On"
            else:
                cmd = url_json2  + str(podavacidx) + "&switchcmd=Off"      
            send_data_to_domoticz(cmd)
            #print(cmd)
            #print("-------------------------------------------------------")
            
        if( a.find('159b',8,-8) > -1):
            ventilatorOtackyHex =  a[a.find('159b',8,-8)+4:a.find('159b',8,-8)+8]
            ventilatorOtackyDec = int(ventilatorOtackyHex,16)
            #print("---------  ventilatorOtackyDec  -----------------------------------")
            print("ventilatorOtacky: ", ventilatorOtackyDec)
             # use Domoticz JSON url to update
            cmd = url_json  + str(ventOtidx) + "&nvalue=0&svalue=" + str(ventilatorOtackyDec)       
            send_data_to_domoticz(cmd)
            #print(cmd)
            #print("-------------------------------------------------------")
                            
        if( a.find('15aa') > -1):
            cerpadlo2Hex =  a[a.find('15aa')+4:a.find('15aa')+8]
            cerpadlo2Dec = int(cerpadlo2Hex,16)
            #print("---------  cerpadlo2Dec  -------------------------------")
            print(cerpadlo2Dec)
             # use Domoticz JSON url to update
            if (cerpadlo2Dec == 1):
                cmd = url_json2  + str(22) + "&switchcmd=On"
            else:
                cmd = url_json2  + str(22) + "&switchcmd=Off"     
            send_data_to_domoticz(cmd)
            #print(cmd)
            #print("-------------------------------------------------------")
                                           
        if( a.find('157c') > -1):
            statHex =  a[a.find('157c')+4:a.find('157c')+8]
            #print("--------  statHex  ------------------------------------")
            #print("stat: ", statHex)
            if (statHex == '0002'): 
                cmd = url_json  + str(statKotle) + "&nvalue=0&svalue=" + "Topeni"     
                send_data_to_domoticz(cmd)
                print("status kotle: Topeni")
            elif(statHex == '0082'):
                cmd = url_json  + str(statKotle) + "&nvalue=0&svalue=" + "Dohled"     
                send_data_to_domoticz(cmd)
                print("status kotle: Dohled")
            elif(statHex == '0050'):
                cmd = url_json  + str(statKotle) + "&nvalue=0&svalue=" + "Udrzovani"     
                send_data_to_domoticz(cmd)
                print("status kotle: Udrzovani")
            elif(statHex == '0052'):
                cmd = url_json  + str(statKotle) + "&nvalue=0&svalue=" + "Dohled"     
                send_data_to_domoticz(cmd)
                print("status kotle: Dohled")
            elif(statHex == '0009'):
                cmd = url_json  + str(statKotle) + "&nvalue=0&svalue=" + "Alarm_Teplota_Neroste"
                send_data_to_domoticz(cmd)
                print("status kotle: Alarm teplota neroste")
            elif(statHex == '000e'):
                cmd = url_json  + str(statKotle) + "&nvalue=0&svalue=" + "Alarm:vadny_Snimac_CO"
                send_data_to_domoticz(cmd)
                print("status kotle: Alarm: vadny snimac CO")
            elif(statHex == '000a'):
                cmd = url_json  + str(statKotle) + "&nvalue=0&svalue=" + "Alarm:vadny_snimac_podavace"
                send_data_to_domoticz(cmd)
                print("status kotle: Alarm: Vadny snimac podavace")
            elif(statHex == '0031'):
                cmd = url_json  + str(statKotle) + "&nvalue=0&svalue=" + "Roztopeni"
                send_data_to_domoticz(cmd)
                print("status kotle: Roztopeni")
            elif(statHex == '0027'):
                cmd = url_json  + str(statKotle) + "&nvalue=0&svalue=" + "Alarm 27"
                send_data_to_domoticz(cmd)
                print("status kotle: Alarm 27")
            elif(statHex == '0029'):
                cmd = url_json  + str(statKotle) + "&nvalue=0&svalue=" + "Alarm 29"
                send_data_to_domoticz(cmd)
                print("status kotle: Alarm 29")
            elif(statHex == '0021'):
                cmd = url_json  + str(statKotle) + "&nvalue=0&svalue=" + "Dohorely"
                send_data_to_domoticz(cmd)
                print("status: Dohorely")
            else:
                cmd = url_json  + str(statKotle) + "&nvalue=0&svalue=" + "Alarm" + statHex
                send_data_to_domoticz(cmd)
                print("status: Alarm:" , statHex)
            #print("-------------------------------------------------------")     
        if( a.find('15cd') > -1):
            statCerpadelHex =  a[a.find('15cd')+4:a.find('15cd')+8]
            statCerpadelDec = int(statCerpadelHex,16)
            #print("-------  statCerpadelDec ----------------------------------")
            if (statCerpadelDec == 3): 
                cmd = url_json2  + str(cerpStatidx) + "&switchcmd=Set%20Level&level=0"
                send_data_to_domoticz(cmd)
                print("status cerpadel: Leto")
            elif(statCerpadelDec == 2):
                cmd = url_json2  + str(cerpStatidx) + "&switchcmd=Set%20Level&level=10"
                send_data_to_domoticz(cmd)
                print("status cerpadel: Paralelni cerpadla")
            elif(statCerpadelDec == 1):
                cmd = url_json2  + str(cerpStatidx) + "&switchcmd=Set%20Level&level=20" 
                send_data_to_domoticz(cmd)
                print("status cerpadel: priorita bojleru")
            elif(statCerpadelDec == 0):
                cmd = url_json2  + str(cerpStatidx) + "&switchcmd=Set%20Level&level=30"
                send_data_to_domoticz(cmd)
                print("status cerpadel: Vytapeni domu")
            #print("-------------------------------------------------------")     
        if( a.find('15ac',8,-8) > -1):
            otevreniVentiluHex =  a[a.find('15ac',8,-8)+4:a.find('15ac',8,-8)+8]
            otevreniVentiluDec = int(otevreniVentiluHex,16)
            #print("-------  otevreni Ventilu  ---------------------------")
            print("otevreniVentilu: " , otevreniVentiluDec )
             # use Domoticz JSON url to update
            cmd = url_json  + str(24) + "&nvalue=0&svalue=" + str(otevreniVentiluDec)       
            send_data_to_domoticz(cmd)
            #print(cmd)
            #print("-------------------------------------------------------")
            
        if( a.find('16f1') > -1):
            mnozstviPaliva2ActualHex =  a[a.find('16f1')+4:a.find('16f1')+8]
            mnozstviPaliva2ActualDec = int(mnozstviPaliva2ActualHex,16)
            #print("------  mnozstviPaliva2ActualDec ------------------------")
            print("mnozstviPaliva2Actual: ", mnozstviPaliva2ActualDec)
             # use Domoticz JSON url to update
            cmd = url_json  + str(procPaliva) + "&nvalue=0&svalue=" + str(mnozstviPaliva2ActualDec/512)       
            send_data_to_domoticz(cmd)
            #print(cmd)
            #print("-------------------------------------------------------")
            
                        
        if( a.find('0370',8,-8) > -1):
            tempPodavaceHex =  a[a.find('0370',8,-8)+4:a.find('0370',8,-8)+8]
            tempPodavaceDec = int(tempPodavaceHex,16)
            #print("-----  tempPodavaceDec  ------------------------------")
            print("tempPodavace: ",tempPodavaceDec)
             # use Domoticz JSON url to update
            cmd = url_json  + str(tempPodavacidx) + "&nvalue=0&svalue=" + str(tempPodavaceDec/10)       
            send_data_to_domoticz(cmd)
            #print(cmd)
            #print("-------------------------------------------------------")
            
        if( a.find('16f8') > -1):
            tempPodavace2Hex =  a[a.find('16f8')+4:a.find('16f8')+8]
            tempPodavace2Dec = int(tempPodavace2Hex,16)
            print("Teplota podavace: ", tempPodavace2Dec/10)
             # use Domoticz JSON url to update
            cmd = url_json  + str(tempPodavacidx) + "&nvalue=0&svalue=" + str(tempPodavace2Dec/10)       
            send_data_to_domoticz(cmd)
            
        if( a.find('15b7',8,-8) > -1):
            tempSpalinHex =  a[a.find('15b7',8,-8)+4:a.find('15b7',8,-8)+8]
            tempSpalinDec = int(tempSpalinHex,16)
            #print("------  tempPodavace3Dec  ----------------------------")
            print("teplota Spalin: ", tempSpalinDec/10)
             # use Domoticz JSON url to update
            cmd = url_json  + str(tempSpalinidx) + "&nvalue=0&svalue=" + str(tempSpalinDec/10)       
            send_data_to_domoticz(cmd)
            #print(cmd)
            #print("-------------------------------------------------------")
        if( a.find('16f2',8,-8) > -1):
            casPalivaHex =  a[a.find('16f2',8,-8)+4:a.find('16f2',8,-8)+8]
            casPalivaDec = int(casPalivaHex,16)
            #print("------  tempPodavace3Dec  ----------------------------")
            print("orientacni cas spotreby paliva: ", casPalivaDec)
             # use Domoticz JSON url to update
            cmd = url_json  + str(casPaliva) + "&nvalue=0&svalue=" + str(casPalivaDec)
            send_data_to_domoticz(cmd)
            #print(cmd)
            #print("-------------------------------------------------------")


