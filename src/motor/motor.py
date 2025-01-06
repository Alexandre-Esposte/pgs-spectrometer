from typing import List, Tuple
#import RPi.GPIO as gpio

class motor:

    def __init__(self, type: str, pinout: Tuple[float, float, float]):

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


    
    def step(self) -> None:
        
        if self.type == 'single':
            configs = self._SINGLE_PHASE_EXCITATION

        elif self.type == 'double':
            configs = self._DOUBLE_PHASE_EXCITATION

        else:
            print('Tipo de ativação invalida')
            return
        
        activation = configs[self.step_index]
        print(self.step_index, activation , configs)

        if self.step_index >= len(configs) - 1:
            self.step_index = 0
            
        else:
            self.step_index += 1

        for pin, state in zip(self.pinout, activation):
            gpio.output(pin, state)

    def clean(self):
        gpio.cleanup()
            

        