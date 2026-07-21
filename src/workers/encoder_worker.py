import time
import serial
import struct
import numpy as np

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QThread, QTimer

class EncoderWorker(QObject):

    dados_recebidos = pyqtSignal(int, int)

    def __init__(self):
        super().__init__()

        self.esp32_port = '/dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001-if00-port0'
        self.baud_rate = 115200
        self.sync_byte = b'\xaa'       
        self._running = True
        self.connector = None
        self.package_size = 9

    def initialize(self):
        self.conectar_esp()

    def conectar_esp(self):
        try:
            self.connector = serial.Serial(self.esp32_port, self.baud_rate, timeout = 0.1)
            self.connector.reset_input_buffer()
            time.sleep(0.1)
            return True
        except Exception as e:
            print(f"[ERRO] Conexão falhou -> {e}")
            return False
    
    @pyqtSlot()
    def receber_angulo(self):
        if not self.connector or not self.connector.is_open:
            if not self.conectar_esp():
                return

        self._running = True
        last_data_time = time.time()
        buffer_residual = b"" # Armazena bytes que sobraram de leituras incompletas

        while self._running:
            try:
                if not self.connector.is_open:
                    raise serial.SerialException("Porta fechada inesperadamente")

                n_waiting = self.connector.in_waiting
                
                if n_waiting > 0:
                    # 1. LÊ TUDO de uma vez para aliviar o buffer do Linux
                    dados_lidos = self.connector.read(n_waiting)
                    buffer_residual += dados_lidos
                    
                    # 2. Processa todos os pacotes de 9 bytes contidos no buffer
                    while len(buffer_residual) >= 9:
                        # Procura o byte de sincronismo
                        idx = buffer_residual.find(self.sync_byte)
                        
                        if idx == -1:
                            # Não tem sync_byte? Limpa o lixo e sai do loop interno
                            buffer_residual = b""
                            break
                        
                        if idx > 0:
                            # Achou o sync, mas havia lixo antes. Remove o lixo.
                            buffer_residual = buffer_residual[idx:]
                            continue # Reavalia o buffer agora começando com o sync
                        
                        # Se chegou aqui, o sync_byte está na posição [0]
                        # Verificamos se temos o pacote completo (1 sync + 8 corpo)
                        if len(buffer_residual) >= 9:
                            pacote_corpo = buffer_residual[1:9] # Os 8 bytes após o sync
                            
                            try:
                                # 3. EXTRAÇÃO (Igual ao seu código original)
                                pulsos, angulo = struct.unpack('<ii', pacote_corpo)
                                self.dados_recebidos.emit(pulsos, angulo)
                                last_data_time = time.time() # Reset do Watchdog
                            except struct.error:
                                print("⚠️ Erro de unpack - pacote corrompido")
                            
                            # Remove os 9 bytes processados e continua procurando no resto
                            buffer_residual = buffer_residual[9:]
                
                else:
                    # 4. WATCHDOG (O seu sistema de segurança de 0.1s)
                    if (time.time() - last_data_time) > 0.1:
                        print("⚠️ Buffer seco por 0.1s. Reiniciando conexão Serial...")
                        self.connector.close()
                        time.sleep(0.1)
                        if self.conectar_esp():
                            last_data_time = time.time()
                            buffer_residual = b"" # Limpa o buffer residual no reset

                # Sleep baixíssimo para não deixar a CPU fritar, 
                # mas sem segurar o fluxo de dados
                time.sleep(0.0001)

            except Exception as e:
                print(f"[ERRO] Falha na leitura: {e}")
                time.sleep(1.0)
                self.conectar_esp()
                last_data_time = time.time()
                buffer_residual = b""

    def stop(self):
        self._running = False
        if self.connector and self.connector.is_open:
            self.connector.close()