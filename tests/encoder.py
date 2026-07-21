import serial
import struct
import sys

# Configurações da Porta Serial
# No Windows costuma ser 'COMx', no Linux/Mac '/dev/ttyUSBx'
PORTA = '/dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001-if00-port0'
BAUD_RATE = 921600

def iniciar_leitura():
    try:
        # Abre a conexão serial
        ser = serial.Serial(PORTA, BAUD_RATE, timeout=0.1)
        print(f"Conectado em {PORTA}. Aguardando dados do encoder...")
        
        # Tamanho da struct: 1 (uint8) + 4 (int32) + 4 (float) = 9 bytes
        tamanho_pacote = 9
        
        while True:
            # Verifica se há pelo menos 9 bytes esperando no buffer
            if ser.in_waiting >= 9:
                # Procura pelo byte de sincronismo
                byte = ser.read(1)
                if byte == b'\xaa':
                    # Se achou o sync, lê exatamente os 8 bytes do corpo
                    dados_corpo = ser.read(8)
                    
                    if len(dados_corpo) == 8:
                        pulsos, angulo = struct.unpack('<if', dados_corpo)
                        # Usando print normal para testar primeiro
                        print(f"Angulo: {angulo:.2f}")
                else:
                    # Se não for o sync, limpa o buffer para não acumular lixo
                    ser.reset_input_buffer() 
            # Pequena pausa para não fritar a CPU se não houver dados
            # Mas não muito, pois o baud rate é alto

    except serial.SerialException as e:
        print(f"\nErro de conexão: {e}")
    except KeyboardInterrupt:
        print("\nLeitura interrompida pelo usuário.")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Conexão serial fechada.")

if __name__ == "__main__":
    iniciar_leitura()