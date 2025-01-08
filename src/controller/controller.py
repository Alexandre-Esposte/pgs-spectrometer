import sys
sys.path.append('../')

import time
from encoder.encoder import Encoder
from motor.motor import Motor



class Controller:

    def __init__(self):

        self.motor = Motor()

        self.encoder = Encoder()

        self.encoder_step = 0.072

        self._look_for_hole()


    def _look_for_hole(self):
        while(self.encoder.on_hole != True):
            self.encoder.verificarFuro()
            self.motor.step('descendente')
            time.sleep(0.008)
        
        print('Sistema inicializado')


    def toAngle(self, init_angle: float, final_angle: float):

        angular_displacement = final_angle - init_angle

        current_angle = init_angle

        if angular_displacement < 0:
            direction = "descendente"
            fator = -self.encoder_step

        
        elif angular_displacement > 0:
            direction = "ascendente"
            fator = self.encoder_step

        else:
            return


        while(self._condition(current_angle, final_angle,direction)):
            print(current_angle)
            current_angle  = current_angle + fator * self.encoder.verificarFuro()
            self.motor.step(direction)
            time.sleep(0.008)

        self.motor.deactivate()
        
    def _condition(self, current_angle: float, final_angle: float, direction: str) -> bool:
        
        if direction == "ascendente":
            return current_angle < final_angle
    
        elif direction == "descendente":
            return current_angle > final_angle


