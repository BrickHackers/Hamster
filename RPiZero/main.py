from Logger import Logger
import signal
import sys
from time import sleep
import zmq
import subprocess
from SerialWriter import MySerial
from ROV_640 import LEDs,Pump
from ROV_ESC import Motor,Servo

class master:
    def __init__(self):
        self.logger = Logger("RPi_MainLog")

        self.InSoPine = "10020"
        self.msgSoPineOut = []
        self.enabled = True
        self.externals = False
        
        LedWC = LEDs(4)
        LedWW = LEDs(5)
        LedRA = LEDs(6)
        
        self.Leds = [LedWC, LedWW, LedRA]
        self.leds_dict = {"whiteCold":0,"whiteWarm":1,"red":2}
    
        self.pumps = [Pump(1),Pump(2)]
        
        MotX1 = Motor(1)
        MotX2 = Motor(2)
        MotZ  = Motor(3)
        
        self.Motors = [MotX1,MotX2,MotZ]
        
        signal.signal(signal.SIGINT, self.sigINT_Handler)
        
        self.serialSoPine = MySerial("/dev/ttyAMA0", "Serial_TO_soPine")
        
        zMQC = zmq.Context()
        self.subscriber = zMQC.socket(zmq.SUB)
        self.subscriber.connect('tcp://127.0.0.1:'+self.InSoPine)
        self.logger.save_line("SUB connected to local port: " + self.InSoPine)
        self.subscriber.setsockopt(zmq.SUBSCRIBE, b"")
        
        sleep(0.5)

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
        elif(data[1] == "TO:All"):
            if(data[2] == "TotalStop"):
                self.estop()
            elif(data[2] == "Start"):
                self.enable()
            else:
                self.logger.save_line("Unknown message toAll <"+data[1]+ ";"+data[2]+">" )
        else:
            self.logger.save_line("Unknown message destination! <" +msg+ ">")
    
    def parseLED(self,data):
        print("Parsing LEDs " + str(self.leds_dict[data[0]]))
        if(self.externals):
            if(data[1] == "ON"):
                print("LED" + data[0] + " ON")
                self.Leds[self.leds_dict[data[0]]].on()
            elif(data[1] == "OFF"):
                self.Leds[self.leds_dict[data[0]]].off()
                print("LED" + data[0] + " OFF")
            elif(data[1] == "I"):
                self.Leds[self.leds_dict[data[0]]].increase_intensity()
                    print("LED" + data[0] + " increased.")
            elif(data[1] == "D"):
                self.Leds[self.leds_dict[data[0]]].decrease_intensity()
                print("LED" + data[0] + " decreased")
            else:
                self.logger.save_line("Unknown LED command! <" +data[:]+ ">")
        else:
            self.logger.save_line("LEDs not enabled!")
    
    def parseMotor(self,data):
        if(self.externals):
            speed = data[3]
            direction = data[2]
            motorA = speed + direction
            motorB = speed - direction

            self.Motors[0].update_speed(MotorA)
            self.Motors[1].update_speed(MotorB)

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
