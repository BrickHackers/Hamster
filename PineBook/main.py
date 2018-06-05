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
        self.logger.save_line("Binded to port: " + self.InGamepad)
        self.subscriber.connect('tcp://'+self.ROVip +':'+self.InSoPine)
        self.logger.save_line("Binded to port: " + self.InSoPine)
        self.subscriber.setsockopt(zmq.SUBSCRIBE, b"")

        sleep(0.5)
        
        self.connectPublishers()
        
    def connectPublishers(self):
        self.publisherSoPine = self.zMQC.socket(zmq.PUB)
        self.publisherSoPine.bind('tcp://10.42.0.1:'+self.OutPortSoPine)
        self.logger.save_line("PublisherGPS connected to port: " + self.OutPortSoPine)

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
        print msg

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
