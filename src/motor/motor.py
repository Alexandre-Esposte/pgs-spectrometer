from typing import List, Tuple, Union
import RPi.GPIO as gpio
import time

class Motor:

    def __init__(self, type: str = 'single', pinout: Tuple[int, int, int] = (10, 9, 11) ):

        self._SINGLE_PHASE_EXCITATION = [
            [1, 0, 0],  # Ativa apenas a primeira bobina
            [0, 1, 0],  # Ativa apenas a segunda bobina
            [0, 0, 1],  # Ativa apenas a terceira bobina
        ]
        
        self._DOUBLE_PHASE_EXCITATION = [
            [1, 0, 0],  # Ativa apenas a primeira bobina
            [1, 1, 0],  # Ativa a primeira e a segunda bobinas
            [0, 1, 0],  # Ativa apenas a segunda bobina
            [0, 1, 1],  # Ativa a segunda e a terceira bobinas
            [0, 0, 1],  # Ativa apenas a terceira bobina
            [1, 0, 1],  # Ativa a primeira e a terceira bobinas
        ]

        gpio.setmode(gpio.BCM)

        self.pinout = pinout # (13, 19, 26)

        for pin in  pinout:
            gpio.setup(pin, gpio.OUT)
            gpio.output(pin, gpio.LOW)

        self.type = type

        self.step_index = 0


    def deactivate(self):
        for pin in self.pinout:
            gpio.output(pin,gpio.LOW)

    def step(self, direction: Union['ascendente', 'descendente']) -> None:
        
        # Estabelecendo a estrategia de acionamento de bobinas
        if self.type == 'single':
            configs = self._SINGLE_PHASE_EXCITATION

        elif self.type == 'double':
            configs = self._DOUBLE_PHASE_EXCITATION

        else:
            print('Tipo de ativação invalida')
            return
        
        # Estabelecendo direção
        if direction == 'ascendente':
            pinout = self.pinout[::-1]

        elif direction == 'descendente':
            pinout = self.pinout
            
        activation = configs[self.step_index]

       # Executando a organização do indice de ativações
        #print(self.step_index, activation, self.pinout, pinout)

        if self.step_index >= len(configs) - 1:
            self.step_index = 0
            
        else:
            self.step_index += 1

        # Executando o passo
        for pin, state in zip(pinout, activation):
            gpio.output(pin, state)

    
    def steps(self, steps: int, time_delay: float, direction: Union['ascendente', 'descendente'] = 'ascendente') -> None:

        if self.type == 'double':
            print('double')
            steps *= 2

            
        for _ in range(steps):
            self.step(direction)
            time.sleep(time_delay)

        time.sleep(0.1)
        self.deactivate()

            

    