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
		self.set_intensity(1)
		self.intensity_list = [1,2,4,8,16,32,64,128,160,256]
		self.intensity_index = 0
		
	def off(self):
		self.LED.setMotorSpeed(1)
		
	def on(self):
		self.LED.setMotorSpeed(self.intensity_list[self.intensity_index])
		
	def increase_intensity(self):
		if(self.intensity_index < (len(self.intensity_list)-1)):
			self.intensity_index += 1
			self.LED.setMotorSpeed(self.intensity_list[self.intensity_index])

	def decrease_intensity(self):
		if(self.intensity_index > 0):
			self.intensity_index -= 1
			self.LED.setMotorSpeed(self.intensity_list[self.intensity_index])

	def set_intensity(self,value):
		if(value > 255):
			self.intensity = 255
		elif(value < 1):
			self.intensity = 1
		else:
			self.intensity = value
		self.LED.setMotorSpeed(self.intensity)
