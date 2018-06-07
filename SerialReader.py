import serial   # apt install python-serial
import zmq      # apt install python-zmq
from Logger import Logger

import signal
import sys
from time import sleep

class SerialReader():

    def __init__(self):
        self.connected = False
        self.enabled = True

        self.baud = 115200
        self.zmqOutPort = "10000"
        self.mserial = "ttyS4"
        self.zmqID = "defaultSerialReader"

        self.get_args()
        
        self.logger = Logger(self.zmqID)
        
        zmq_cont = zmq.Context()
        self.publisher = zmq_cont.socket(zmq.PUB)
        signal.signal(signal.SIGINT, self.sigINT_Handler)
        
        if(self.connect_serial() and self.connect_zmq()):
            self.main_loop()

    def sigINT_Handler(self, signal, frame):
        print (self.zmqID + " detected SigINT signal")
        self.logger.save_line("Signal SigINT detected")
        self.enabled = False
        
    def deinit(self):
        self.publisher.disconnect('tcp://127.0.0.1:'+str(self.zmqOutPort))
        self.logger.save_line("Publisher disconnected.")
        self.ser.close()
        self.logger.save_line("Serial closed.")
        self.logger.close()

    def get_args(self):
        if(len(sys.argv) < 2):
            print ("Usage: " + str(sys.argv[0]) + " <PATH TO TTY PORT>" +
                   "[opt: <BaudRate> <ZMQPort> <ID>]" )
            print ("Secondary use: " + str(sys.argv[0])
                   + " <PATH TO RAW LOGFILE>")
            sys.exit(0)
    
        if(len(sys.argv) >= 2):
            self.mserial = sys.argv[1]
            if(sys.argv[1].find("/dev/") >= 0):
                #normal run from physical device
                self.normalRun = True
            elif(sys.argv[1].find("Logs/") >= 0):
                # Run from LOG
                self.normalRun = False
            
        if(len(sys.argv) >= 3):
            self.baud = int(sys.argv[2])

        if(len(sys.argv) >= 4):
            self.zmqOutPort = str(sys.argv[3])

        if(len(sys.argv) >= 5):
            self.zmqID = str(sys.argv[4])

        print("Settings -> Serial: " + self.mserial + " speed: "
              + str(self.baud) + " ZMQ port: " + self.zmqOutPort
              + " serial ID: " + str(self.zmqID))
       
    def connect_serial(self):
        if not self.connected:
            try:
                self.ser = serial.Serial(self.mserial, self.baud)
                self.ser.bytesize = serial.EIGHTBITS
                self.ser.parity = serial.PARITY_NONE
                self.ser.stopbits = serial.STOPBITS_ONE
                
                self.disconected = False
                print( "Connected to " + self.mserial)
            
                if(self.ser.readable()):
                    self.ser.flush()
                    self.ser.readline()
                return True
            except:
                print( "Failed connecting to " + self.mserial)
                return False
        else:
            return True

    def connect_zmq(self):
        try:
            self.publisher.bind('tcp://127.0.0.1:'+str(self.zmqOutPort))
            self.logger.save_line("Binded to local port: " + self.zmqOutPort)
            self.publisher.send_string(self.zmqID + " binded on port "
                                       + self.zmqOutPort)
        except:
            self.logger.save_line("Failed to bind localPort "
                                  + self.zmqOutPort)
            return False
        sleep(0.5)
        return True
                    
    def main_loop(self):
        while self.enabled:
            if(self.ser.readable()):
                line = self.ser.readline()
                self.logger.save_line("Incomming msg: <"+line+">")
                self.publisher.send_string("ID:"+self.zmqID+","+line)
            sleep(0.001)
        self.deinit()

B = SerialReader()
