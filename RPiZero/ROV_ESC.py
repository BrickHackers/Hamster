import time
from darkwater_escape import dw_Controller, dw_Servo, dw_Motor

class Motor:
    def __init__(self,port,addr=0x61):
        self.dw = dw_Controller(addr)
        self.motor = self.dw.getMotor(port)
        self.motor.off()
        self.maximal_speed = [0, 1, -1]
        self.minimal_speed = [0, 0.2, -0.2]
        self.running = False
        self.direction = 0
        self.dirdic = {"OFF":0,"CW":1,"CCW":2}
        
    def off(self):
        self.speed = 0
        self.direction = 0
        self.motor.off()
    
    def on(self):
        self.direction = self.getdir(self.speed)
        self.startUp(self.direction)
        self.setMotorSpeed(self.speed)
        self.running = True
    
    def change_direction(self,new_dir):
        self.stand_by()
        #newDir = self.get_dir(new_speed)
        return None
	
    def get_dir(self,speed):
        if(speed > 0):
            return self.dirdic["CW"]
        elif(speed < 0):
            return self.dirdic["CCW"]
        else:
            return self.dirdic["OFF"]
    
    def setMotorSpeed(self,speed):
        speed = 1500 + 500*speed
        self.motor.setMotorSpeed(speed)
    
    def update_speed(self,new_speed):
        new_direction = self.get_dir(new_speed)
        if (new_speed < self.minimal_speed[new_direction]):
            new_speed = self.minimal_speed[new_direction]
        if (new_speed > self.maximal_speed[new_direction]):
            new_speed = self.maximal_speed[new_direction]
        
        if(self.running):
            if(new_direction is not self.direction):
                self.change_direction(new_direction)
        else:
            self.start_up(new_direction)
        self.setMotorSpeed(new_speed)
        self.speed = new_speed

    def standBy(self, direction):
        if(self.speed > self.minimal_speed[self.direction]):
            step = -0.05
        else:
            step = 0.05
        
        for i in range(self.speed, self.minimal_speed[direction], step):
            self.setMotorSpeed(i)
            self.speed = i
            sleep(0.2)
    
    def start_up(self, direction):
        self.setMotorSpeed(self.minimal_speed[direction])
        self.speed = self.minimal_speed[direction]
        self.running = True
    
class Servo:
    def __init__(self,port,addr=0x61):
        self.dw = dw_Controller(addr)
        self.servo = self.dw.getServo(port)
        self.servo.setPWMuS(1500)
        self.pos = 0
    
    def setPosition(self, new_pos):
        if(new_pos < -1):
            new_pos = -1
        if(new_pos < 1):
            new_pos = 1
        
        self.servo.setPWMuS(1500+500*new_pos)
        
    def goHome(self):
        self.servo.setPWMuS(1500+500*new_pos)
        
        
        
        




