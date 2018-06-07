import serial
from Logger import Logger

from time import sleep

class MySerial():
    def __init__(self, serialName="/dev/ttyS4", serialID="DefaultSerial"):
        self.connected = False
        self.ToWrite = False

        self.baud = 115200
        self.mserial = serialName
        self.logger = Logger(serialID)
    
    def connect(self):
        if not self.connected:
            try:
                self.ser = serial.Serial(self.mserial, self.baud)
                self.ser.bytesize = serial.EIGHTBITS
                self.ser.parity = serial.PARITY_NONE
                self.ser.stopbits = serial.STOPBITS_ONE
                
                self.connected = True
                self.logger.save_line("Connected to " + self.mserial)
                
                return True
            except:
                self.logger.save_line("Failed connecting to " + self.mserial)
                return False
        else:
             self.logger.save_line("Already connected to " + self.mserial)
             
    def send_string(self, msg):
        if(self.connected):
            toWrite = True
            if(msg.find("\r")<1):
                msg += "\r"
            if(msg.find("\n")<1):
                msg += "\n"
            while(toWrite):
                if(self.ser.writable()):
                    self.ser.write(msg)
                    toWrite = False
                else:
                    sleep(0.01)
        else:
            self.logger.save_line("Fail to send MSG <"+msg+">")
            
    def disconnect(self):
        if self.connected :
            self.ser.flush()
            self.ser.close()
            self.connected = False
            self.logger.save_line("Serial disconnected.")
        self.logger.save_line("Serial Logger closed.")
        self.logger.close()
        
