import serial
from Logger import Logger

from time import sleep

class MySerial():
    def __init__(self, serialName="/dev/ttyS4", serialID="DefaultSerial"):
        self.connected = False
        self.ToWrite = False

        self.serBaud = 115200
        self.mserial = serialName
        self.logger = Logger(serialID)
    
    def connect_serial(self):
        if not self.connnected:
            try:
                self.ser = serial.Serial(self.mserial, self.mbaud)
                self.ser.bytesize = serial.EIGHTBITS
                self.ser.parity = serial.PARITY_NONE
                self.ser.stopbits = serial.STOPBITS_ONE
                
                self.disconected = False
                self.logger.save_line("Connected to " + self.mserial)
                
                if(self.ser.readable()):
                    self.ser.flush()
                    self.ser.readline()

                return True
            except:
                self.logger.save_line("Failed connecting to " + self.mserial)
                return False
        else:
             self.logger.save_line("Already connected to " + self.mserial)
             
    def writeMessage(self, msg):
        toWrite = True
        while(toWrite):
            if(self.ser.writable()):
                self.ser.write(msg)
                toWrite = False
        
    def disconnect(self):
        self.ser.flush()
        self.ser.close()
        
        
