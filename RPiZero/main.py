from Logger import Logger
import signal
import sys
from time import sleep
import zmq
import subprocess
from SerialWriter import MySerial
from ROV_640 import LEDs,Pump

class master:
    def __init__(self):
        self.logger = Logger("RPi_MainLog")

        self.InSoPine = "10020"
        self.msgSoPineOut = []
        self.enabled = True
        self.externals = False
        
        LedWC = LEDs(1)
        LedWW = LEDs(2)
        LedRA = LEDs(3)
        
        self.Leds = [LedWC, LedWW, LedRA]
        
        self.pump = Pump(6)
        
        self.Motors = [LedWC, LedWW, LedRA]
        
        signal.signal(signal.SIGINT, self.sigINT_Handler)
        
        self.serialSoPine = MySerial("/dev/ttyAMA0", "Serial_TO_soPine")
                
        self.getIP()
        
        zMQC = zmq.Context()
        self.subscriber = zMQC.socket(zmq.SUB)
        self.subscriber.connect('tcp://127.0.0.1:'+self.InSoPine)
        self.logger.save_line("SUB connected to local port: " + self.InSoPine)
        self.subscriber.setsockopt(zmq.SUBSCRIBE, b"")
        
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
        self.subscriber.disconnect('tcp://127.0.0.1:'+self.InSoPine)
        self.logger.save_line("SUB disconnected from local port: " + self.InSoPine)
             
        self.serialSoPine.disconnect()
        
    def checkAll(self):
        waitingMSG = self.subscriber.poll(100,zmq.POLLIN)
        print("Waiting msgs: " +str(waitingMSG))
        while(waitingMSG > 0):
            msg = self.subscriber.recv_string()
            self.parseMessage(msg)
            waitingMSG = self.subscriber.poll(100,zmq.POLLIN)
        
        for msg in self.msgSoPineOut:
            self.serialSoPine.send_string(msg)
        self.msgSoPineOut = []

    def parseMessage(self,msg):
		data = msg.split(",")
		if(data[1] == "TO:RPi"):
			if(data[2] == "LED"):
				self.parseLED(data[3:])
			elif(data[2] == "Motor"):
				self.parseMotor(data[3:])
			elif(data[2] == "CAM") and (data[3] == "Rot"):
				self.parseServo(data[3:])
			elif(data[2] == "Pump"):
				self.parsePump(data[3:])
		elif(data[1] == "TO:ALL"):
			if(data[2] == "TotalStop"):
				self.estop()
			elif(data[2] == "Start"):
				self.enable()
		else:
			self.logger.save_line("Unknown message destination! <" +msg+ ">")
	
    def parseLED(self,data):
        if(self.externals):
            #TODO smt
            pass
			
    def parseMotor(self,data):
        if(self.externals):
			#TODO smt
			pass
    def parseServo(self,data):
        if(self.externals):
			#TODO smt
			pass
    def parsePump(self,data):
        if(self.externals):
            #TODO smt
            pass
	
    def estop(self):
        self.externals = False
        for led in self.Leds:
            led.off()
        for motor in self.Motors:
            motor.off()
        pump.off()
		
    def enable(self):
        self.externals = True

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
