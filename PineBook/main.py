from Logger import Logger
import signal
import sys
from time import sleep
import zmq
import subprocess

class master:
    def __init__(self):
        
        self.logger = Logger("mainLog")

        self.InGamepad = "10001"
        self.InSoPine = "10010"
        self.OutPortSoPine = "10009"
        
        self.msgSoPineOut = []
        
        self.enabled = True
        signal.signal(signal.SIGINT, self.sigINT_Handler)
        self.zMQC = zmq.Context()

        self.subscriber = self.zMQC.socket(zmq.SUB)
        
        self.getROVip()
        
        self.subscriber.connect('tcp://127.0.0.1:'+self.InGamepad)
        self.logger.save_line("SUB connected to local port: " + self.InGamepad)
        self.subscriber.connect('tcp://'+self.ROVip +':'+self.InSoPine)
        self.logger.save_line("SUB connected to: " + self.ROVip + ":" + self.InSoPine)
        self.subscriber.setsockopt(zmq.SUBSCRIBE, b"")

        sleep(0.5)
        
        self.connectPublishers()
        
    def connectPublishers(self):
        self.publisherSoPine = self.zMQC.socket(zmq.PUB)
        self.publisherSoPine.bind('tcp://10.42.0.1:'+self.OutPortSoPine)
        self.logger.save_line("PublisherSoPine binded to port: " + self.OutPortSoPine)

        sleep(0.5)
        
    def sigINT_Handler(self, signal, frame):
        print("\nMaster detected SigINT signal")
        self.logger.save_line("Signal SigINT detected")
        self.enabled = False
    
    def deinitRobot(self):
        self.subscriber.disconnect('tcp://127.0.0.1:'+self.InGamepad)
        self.logger.save_line("SUB disconnected from local port: " +self.InGamepad)
        self.subscriber.disconnect('tcp://'+self.ROVip +':'+self.InSoPine)
        self.logger.save_line("SUB disconnected from local port: "+self.InSoPine)
        
        self.publisherSoPine.disconnect('tcp://'+self.ROVip +':'+self.OutPortSoPine)
        self.logger.save_line("PUB_GPS disconnected from local port: " + self.OutPortSoPine)

    def getROVip(self):
        data = subprocess.check_output(["cat","/var/lib/misc/dnsmasq.leases"])
        self.ROVip = data.split(" ")[2]

    def checkAll(self):
        msg = ""
        oldmsg = " "
        waitingMSG = self.subscriber.poll(100,zmq.POLLIN)
        print("Waiting msgs: " +str(waitingMSG))
        while(waitingMSG > 0):
            msg = self.subscriber.recv_string()
            self.parseMessage(msg)
            waitingMSG = self.subscriber.poll(100,zmq.POLLIN)
        for msg in self.msgSoPineOut:
            self.publisherSoPine.send_string(msg)
            self.logger.save_line("sending:"+msg)
        self.msgSoPineOut= []
		
    def parseMessage(self,msg):
        comboLEDon = 0
        if(msg.find("ID:GP")>-1):
            if(msg.find("BTN")>-1):
                btnNum = msg.split(",")[2]
                btnState = msg.split(",")[3]
                print "Button " + btnNum + " state: " + btnState
                if(btnState=="1"):
                    if(btnNum=="0"):
                        comboLEDon = 1
                        LEDwhiteCold = 1
                    elif(btnNum=="1"):
                        comboLEDon = 1
                        LEDred = 1
                        
                    elif(btnNum=="2"):
                        self.msgSoPineOut.append("ID:PB,TO:RPi,TotalStop")
                    elif(btnNum=="3"):
                        comboLEDon = 1
                        LEDwhiteWarm = 1
                        
                    elif(btnNum=="4"):
                        self.msgSoPineOut.append("ID:PB,TO:RPi,motorZ")
                    elif(btnNum=="5"):
                        self.msgSoPineOut.append("ID:PB,TO:SoPine,REC")
                    elif(btnNum=="6"):
                        self.msgSoPineOut.append("ID:PB,TO:RPi,motorZ")
                    elif(btnNum=="7"):
                        self.msgSoPineOut.append("ID:PB,TO:RPi,Pump")
                    elif(btnNum=="8"):
                        self.msgSoPineOut.append("ID:PB,TO:All,Shutdown")
                    elif(btnNum=="9"):
                        self.msgSoPineOut.append("ID:PB,TO:All,Boot")
                    else:
                        print "unspecified buton"
                else:
                    comboLEDon = 0
                    LEDwhiteCold = 0
                    LEDred = 0
                    LEDwhiteWarm = 0
            elif(msg.find("HAT")>-1):
                hatNum = msg.split(",")[2]
                hat2Num = msg.split(",")[3]
                hatState = msg.split(",")[4]
                print "Hat " + hatNum + hat2Num+" state: " + hatState
                if(comboLEDon==1):
                    if(hat2Num=="0"):
                        if(hatState=="1"):
                            if(LEDwhiteCold == 1):
                                self.msgSoPineOut.append("ID:PB,TO:RPi,LEDwhiteCold,ON")
                            elif(LEDred == 1):
                                self.msgSoPineOut.append("ID:PB,TO:RPi,LEDred,ON")
                            elif(LEDwhiteWarm == 1):
                                self.msgSoPineOut.append("ID:PB,TO:RPi,LEDwhiteWarm,ON")
                        elif(hatState=="-1"):
                            if(LEDwhiteCold == 1):
                                self.msgSoPineOut.append("ID:PB,TO:RPi,LEDwhiteCold,OFF")
                            elif(LEDred == 1):
                                self.msgSoPineOut.append("ID:PB,TO:RPi,LEDred,OFF")
                            elif(LEDwhiteWarm == 1):
                                self.msgSoPineOut.append("ID:PB,TO:RPi,LEDwhiteWarm,OFF")
                    elif(hat2Num=="1"):
                        if(hatState=="1"):
                            if(LEDwhiteCold == 1):
                                self.msgSoPineOut.append("ID:PB,TO:RPi,LEDwhiteCold,10i")
                            elif(LEDred == 1):
                                self.msgSoPineOut.append("ID:PB,TO:RPi,LEDred,10i")
                            elif(LEDwhiteWarm == 1):
                                self.msgSoPineOut.append("ID:PB,TO:RPi,LEDwhiteWarm,10i")
                        elif(hatState=="-1"):
                            if(LEDwhiteCold == 1):
                                self.msgSoPineOut.append("ID:PB,TO:RPi,LEDwhiteCold,10d")
                            elif(LEDred == 1):
                                self.msgSoPineOut.append("ID:PB,TO:RPi,LEDred,10d")
                            elif(LEDwhiteWarm == 1):
                                self.msgSoPineOut.append("ID:PB,TO:RPi,LEDwhiteWarm,10d")
                    else:
                        print "unspecified hat"
                
            elif(msg.find("AXS")>-1):
                axsNum = msg.split(",")[2]
                axsValue = msg.split(",")[3]
                print "Axes " + axsNum+" value: " + axsValue
                if(axsNum=="0"):
                    self.msgSoPineOut.append("ID:PB,TO:RPi,MotorY,"+axsValue)
                elif(btnNum=="1"):
                    self.msgSoPineOut.append("ID:PB,TO:RPi,MotorX"+axsValue)
                elif(btnNum=="2"):
                    self.msgSoPineOut.append("ID:PB,TO:RPi,CamY"+axsValue)
                elif(btnNum=="3"):
                    self.msgSoPineOut.append("ID:PB,TO:RPi,CamZ"+axsValue)
                
                
                
                
            else:
                self.logger.save_line("Wrong input")
            
    def initRobot(self):
        sleep(1)

    def run(self):
        self.initRobot()
        while(self.enabled):
            self.checkAll()
            sleep(0.1)
        self.deinitRobot

M = master()
M.run()
