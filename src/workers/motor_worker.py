import time
import serial
import struct
import numpy as np

# from ccd.AlphalasCCD import *
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QThread, QTimer


class MotorWorker(QObject):

    def __init__(self):
        super().__init__()
        
        self.arduino_port = "/dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_55437333637351F02270-if00"
        self.baud_rate = 115200
        self.sync_byte = 0xAA
        
        self.connector = None


    def initialize(self):
        self.conectar_arduino()

    def conectar_arduino(self):
        try:
            self.connector = serial.Serial(self.arduino_port, self.baud_rate, timeout = 1)
            time.sleep(0.1)
        except Exception as e:
            print(f"[ERRO] Conexão falhou -> {e}")

    @pyqtSlot(dict)
    def send_command(self, command: dict):

        print(command)
        if self.connector and self.connector.is_open():
            try:    
                sentido_rotacao = command['direction']
                status = command['status']
                tempo_acionamento_bobinas = command['velocity']
                
                data = struct.pack('<BBB', sentido_rotacao, status, tempo_acionamento_bobinas)
                self.connector.write(bytes([self.sync_byte]))
                self.connector.write(data)
                self.connector.flush()

            except Exception as e:
                print(f"[Erro] Não foi possível enviar o comando -> {e}")
        else:
            print("Objeto connector  não existe ou a conexão falhou")