import pygame # For joystick - python-pygame
import subprocess
import zmq
from time import sleep
from Logger import Logger
        
import signal   ## for Ctrl+C 

class MyGamePad:
    def __init__(self):

        self.zmqPort = "10001"
        self.zmqID = "gamepad"
        
        self.enabled = True

        pygame.init()
        pygame.joystick.init()

        self.logger = Logger("GamePad")
        zmq_cont = zmq.Context()
        self.publisher = zmq_cont.socket(zmq.PUB)
        self.publisher.bind('tcp://127.0.0.1:'+self.zmqPort)
        
        sleep(0.5)
        
        signal.signal(signal.SIGINT, self.sigINT_Handler)
        
        self.main_loop()

    def initGamepad(self):
        self.my_clock = pygame.time.Clock()
        self.num_of_gamepads = pygame.joystick.get_count()
        
        if(self.num_of_gamepads > 0):
            self.my_gamepad = pygame.joystick.Joystick(0)
            self.my_gamepad.init()
        else:
            print("No gamepad found, exiting...")
            self.enabled = False
            return -1
        
        self.axes_num = self.my_gamepad.get_numaxes()
        self.btns_num = self.my_gamepad.get_numbuttons()
        self.hats_num = self.my_gamepad.get_numhats()

        self.btns_state = []
        for i in range(self.btns_num):
            self.btns_state.append(self.my_gamepad.get_button(i))

        self.hats_state = []
        for i in range(self.hats_num):
            self.hats_state.append(self.my_gamepad.get_hat(i))

        self.axis_state = []
        for i in range(self.axes_num):
            self.axis_state.append(round(self.my_gamepad.get_axis(i),2))
        
        return 0
        
    def sigINT_Handler(self, signal, frame):
        self.logger.save_line("SigINT detected")
        print("\nSigINT detected")
        self.enabled = False
        
    def check_buttons_down(self):
        for i in range( self.btns_num):
            if(self.btns_state[i] is not self.my_gamepad.get_button(i)):
                self.publisher.send_string("ID:GP,BTN," + str(i) + ",1")
                self.logger.save_line("ID:GP,BTN," + str(i) + ",1")
                self.btns_state[i] = self.my_gamepad.get_button(i)

    def check_buttons_up(self):
        for i in range( self.btns_num):
            if(self.btns_state[i] is not self.my_gamepad.get_button(i)):
                self.publisher.send_string("ID:GP,BTN," + str(i) + ",0")
                self.logger.save_line("ID:GP,BTN," + str(i) + ",0")
                self.btns_state[i] = self.my_gamepad.get_button(i)

    def check_hat(self):
        for i in range(self.hats_num):
            new_hat_state = self.my_gamepad.get_hat(i)
            for j in range(len(self.hats_state[i])): ## 0 = X ; 1 = Y
                if(self.hats_state[i][j] is not new_hat_state[j]):
                    self.publisher.send_string("ID:GP,HAT,"+ str(i) + "," + str(j) + "," +str(new_hat_state[j]))
                    self.logger.save_line("ID:GP,HAT,"+ str(i) + "," + str(j) + "," +str(new_hat_state[j]) + "\r\n")
                    self.hats_state[i] = new_hat_state
                    
    def check_axes(self):
        # upadate values
        new_value = []
        for i in range(self.axes_num):
            new_value.append(round(self.my_gamepad.get_axis(i),2))
        
        for i in [0,2]:
            if((abs(self.axis_state[i]-new_value[i])>=0.02) or (abs(self.axis_state[i+1]-new_value[i+1])>=0.02)):
                self.publisher.send_string("ID:GP,AXS," + str(i) +","+ str(i+1) + "," + str(new_value[i]) + ","+ str(new_value[i+1]))
                self.logger.save_line("ID:GP,AXS," + str(i) +","+ str(i+1) + "," + str(new_value[i]) + ","+ str(new_value[i+1]))
                self.axis_state[i] = new_value[i]
                self.axis_state[i+1] = new_value[i+1]
                                
    def main_loop(self):
        self.initGamepad()
        while self.enabled:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.enabled = False
                if event.type == pygame.JOYBUTTONDOWN:
                    self.check_buttons_down()
                if event.type == pygame.JOYBUTTONUP:
                    self.check_buttons_up()
                if event.type == pygame.JOYHATMOTION:
                    self.check_hat()
            self.check_axes();
            self.my_clock.tick(10) # omezení na cca 5 Hz
        self.deinit()

    def deinit(self):
        pygame.quit()
        self.publisher.disconnect("tcp://127.0.0.1:"+ self.zmqPort)
        self.logger.save_line("GamePad terminated")
        self.logger.close()
        

logitechFX710 = MyGamePad()

