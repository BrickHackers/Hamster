from Logger import Logger
import signal
import sys
from time import sleep
import zmq
import subprocess
from SerialWriter import MySerial

class master:
    def __init__(self):
        self.logger = Logger("SoPine_MainLog")

        self.InPB = "10009"
        self.OutPB = "10010"
        self.InRPi = "10019"
        self.InMBED = "10018"
        
        self.msgRPiOut = []
        self.msgMBEDOut = []
        self.msgPBOut = []
        
        self.GoProREC = 0
        
        self.enabled = True
        signal.signal(signal.SIGINT, self.sigINT_Handler)
        
        self.serialRPi = MySerial("/dev/ttyS4", "Serial_TO_rpi")
        self.serialRPi.connect()
        
        self.serialMBED = MySerial("/dev/ttyS3", "Serial_TO_mbed")
        self.serialMBED.connect()
        
        self.getIP()
        
        zMQC = zmq.Context()
        self.subscriber = zMQC.socket(zmq.SUB)
        self.subscriber.connect('tcp://10.42.0.1:'+self.InPB )
        self.logger.save_line("SUB connected to external IP: 10.42.0.1:" + self.InPB )
        self.subscriber.connect('tcp://127.0.0.1:'+self.InRPi)
        self.logger.save_line("SUB connected to local port: " + self.InRPi)
        self.subscriber.setsockopt(zmq.SUBSCRIBE, b"")
        
        self.publisherPB = zMQC.socket(zmq.PUB)
        self.publisherPB.bind('tcp://'+self.ip+':'+self.OutPB)
        self.logger.save_line("PublisherPB binded to: " + self.ip + ":" + self.OutPB)

        sleep(0.5)
    
    def getIP(self):
        cmd = ["ip","address"]
        data = subprocess.check_output(cmd)
        data = data.split("\n")
        addrs = []
        for line in data:
            if (line.find("inet ") > 0) and (line.find("global") > 0):
                startIndex = line.find("inet ")
                stopIndex = line.find("/24")
                self.ip = line[startIndex+5:stopIndex]
        
    def sigINT_Handler(self, signal, frame):
        print("\nMaster detected SigINT signal")
        self.logger.save_line("Signal SigINT detected")
        self.enabled = False
        
    def deinitRobot(self):
        self.subscriber.disconnect('tcp://127.0.0.1:'+self.InRPi)
        self.logger.save_line("SUB disconnected from local port: " + self.InRPi)
        
        self.subscriber.disconnect('tcp://10.42.0.1:'+self.InPB)
        self.logger.save_line("SUB disconnected from remote port: 10.42.0.1:" + self.InRPi)
        
        self.publisherPB.disconnect('tcp://'+ self.ip + ':' + self.OutPB)
        self.logger.save_line("PUB_PB disconnected from remote port: 10.42.0.1:" + self.OutPB)
        
        self.serialRPi.disconnect()
        self.serialMBED.disconnect()
        
    def checkAll(self):
        waitingMSG = self.subscriber.poll(100,zmq.POLLIN)
        print("Waiting msgs: " +str(waitingMSG))
        while(waitingMSG > 0):
            msg = self.subscriber.recv_string()
            self.parseMessage(msg)
            waitingMSG = self.subscriber.poll(100,zmq.POLLIN)
        
        for msg in self.msgRPiOut:
            self.serialRPi.send_string(msg)
        self.msgRPiOut = []
        for msg in self.msgMBEDOut:
            self.serialMBED.send_string(msg)
        self.msgMBEDOut = []
        for msg in self.msgPBOut:
            self.publisherPB.send_string(msg)
        self.msgPBOut = []

    def parseMessage(self,msg):
        if(msg.find("ID:PB")>-1):
            if(msg.find("TO:RPi")>0):
                self.msgRPiOut.append(msg)
            elif(msg.find("TO:SoPine")>0):
                FirstPart = msg.split(",")[2]
                SecondPart = msg.split(",")[3]
                if(FirstPart == "GoPro"):
                    if(SecondPart == "REC"):
                        if(self.GoProREC == 0):
                            self.GoProREC = 1
                        elif(self.GoProREC == 1):
                            self.GoProREC = 0
                        else:
                            self.logger.save_line("GoPro confused!")
                    else:
                        self.logger.save_line("Unknown GoPro message! <" +SecondPart+ ">")                
                ''' TODO:
                Camera support (On/Off)
                GoPro (mode VID/PIC, start/stop/takePic, resolution(?))
                '''
                pass
            elif(msg.find("TO:All")>0):
                self.msgRPiOut.append(msg)
                self.msgMBEDOut.append(msg)
                ''' TODO:
                Start/Stop platform
                EStop
                '''
            else:
                self.logger.save_line("Unknown message destination! <" +msg+ ">")                
        elif(msg.find("ID:RPi")>1):
            self.msgRPiOut.append(msg)
            '''TODO:
            add feedback for PineBook etc
            '''
        elif(msg.find("ID:MBED")>-1):
            self.msgMBEDOut.append(msg)
            '''TODO:
            Battery checker
            sensors udates
            '''
        else:
            self.logger.save_line("Message ID not supported! <" +msg+ ">")

    def initRobot(self):
        sleep(1)

    def run(self):
        self.initRobot()
        while(self.enabled):
            self.checkAll()
            sleep(0.05)
        self.deinitRobot()
        
M = master()
M.run()
