from Logger import Logger
import signal
import sys
from time import sleep
import zmq
import subprocess

class master:
    def __init__(self):
        self.logger = Logger("SoPine_MainLog")

        self.InPB = "10009"
        self.OutPB = "10010"
        self.InRPi = "10029"
        self.OutRPi = "10011"

        self.enabled = True
        signal.signal(signal.SIGINT, self.sigINT_Handler)
        
        self.getIP()
        
        zMQC = zmq.Context()
        
        self.subscriber = zMQC.socket(zmq.SUB)
        self.subscriber.connect('tcp://10.42.0.1:'+self.InPB )
        self.logger.save_line("SUB connected to external IP: 10.42.0.1:" + self.InPB )
        self.subscriber.connect('tcp://127.0.0.1:'+self.InRPi)
        self.logger.save_line("SUB connected to local port: " + self.InRPi)
        self.subscriber.setsockopt(zmq.SUBSCRIBE, b"")

        sleep(0.5)
        
        self.publisherPB = zMQC.socket(zmq.PUB)
        self.publisherPB.bind('tcp://'+self.ip+':'+self.OutPB)
        self.logger.save_line("PublisherPB binded to: " + self.ip + ":" + self.OutPB)

        self.publisherRPi = zMQC.socket(zmq.PUB)
        self.publisherRPi.bind('tcp://127.0.0.1:'+self.OutRPi)
        self.logger.save_line("PublisherRPi binded to local port: " + self.OutRPi)
        
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

        self.publisherRPi.disconnect('tcp://127.0.0.1:'+self.OutRPi)
        self.logger.save_line("PUB_RPi disconnected from local port: " + self.OutRPi)
        
    def checkAll(self):
        msg = ""
        oldmsg = " "
        waitingMSG = self.subscriber.poll(100,zmq.POLLIN)
        print("Waiting msgs: " +str(waitingMSG))
        while(waitingMSG > 0):
            msg = self.subscriber.recv_string()
            self.parseMessage(msg)
            waitingMSG = self.subscriber.poll(100,zmq.POLLIN)
        for msg in self.msgRPiOut:
            self.publisherRPi.send_string(msg)
        self.msgRPiOut = []
        for msg in self.msgPBOut:
            self.publisherPB.send_string(msg)
        self.msgPBOut = []

    def parseMessage(self,data):
        return 0

    def initRobot(self):
        sleep(1)

    def run(self):
        self.initRobot()
        while(self.enabled):
            self.checkAll()
            sleep(0.1)
        self.deinitRobot()
        
M = master()
M.run()
