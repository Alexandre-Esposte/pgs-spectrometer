import RPi.GPIO as gpio
import time
import threading

class Encoder:
    def __init__(self, pin: int = 4):

        self.pin = pin

        # Configuração do gpio
        gpio.setmode(gpio.BCM)  

        gpio.setup(self.pin, gpio.IN, pull_up_down= gpio.PUD_UP)

        self.on_hole = True if gpio.input(self.pin) == 0 else False

        self.state_changes = 0


    def encoderMedir(self):

        while(1):
            try:
                
                estado = gpio.input(self.pin)
                
                if estado == 0 and self.on_hole == False:
                    print('Furo detectado')
                    self.on_hole = True
                    self.state_changes += 1

                elif estado == 1 and self.on_hole == True:
                    self.on_hole = False

                #print(f'Pino {self.pin} está no estado -> {gpio.input(self.pin)}')
                time.sleep(0.5)

            except KeyboardInterrupt:
                print("Finalizando monitoramento do encoder")
    

    def verificarFuro(self):
        estado = gpio.input(self.pin)
                
        if estado == 0 and self.on_hole == False:
            # futo detectado
            self.on_hole = True
            self.state_changes += 1
            return 1

        elif estado == 1 and self.on_hole == True:
            # fora do furo
            self.on_hole = False
            return 0
            
        else:
            return 0

    def start_monitoring(self):
        # Inicia o monitoramento em uma thread separada
        threading.Thread(target=self.encoderMedir, daemon=True).start()
        

if __name__ == "__main__":
    encoder = Encoder(pin = 4)

    while(True):
        try:
            print(encoder.state_changes, encoder.on_hole)
            encoder.verificarFuro()
        except KeyboardInterrupt:
            gpio.cleanup()
            print('Finalizando encoder')