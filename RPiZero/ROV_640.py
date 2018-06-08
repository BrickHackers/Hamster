import time
from darkwater_640 import dw_Controller, dw_Motor

class Pump:
	def __init__(self,port,addr=0x60):
		self.dw = dw_Controller( addr )
		self.motor = self.dw.getMotor(port)
		self.motor.off()

	def off(self):
		self.motor.off()

	def on(self):
		self.motor.setMotorSpeed(255)
		
class LEDs:
	def __init__(self,port,addr=0x60):
		self.dw = dw_Controller(addr)
		self.LED = self.dw.getMotor(port)
		self.LED.off()
		self.intensity = 64
		
	def off(self):
		self.LED.off()
		
	def on(self):
		seld.LED.setMotorSpeed(self.intensity)
		
	def change_intensity(self,value):
		new_intensity = self.intensity + value
		if(new_intensity > 255):
			self.intensity = 255
		elif(new_intensity < 0):
			self.intensity = 0
		else:
			self.intensity = new_intensity
		self.LED.setMotorSpeed(self.intensity)
