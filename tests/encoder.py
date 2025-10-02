import serial
import struct
import time


# Configurações da porta serial
PORTA = "/dev/ttyUSB0"   # ou COM3 no Windows
BAUDRATE = 921600

# Solicita parâmetros ao usuário
novo_fator_correcao =  0#0.000005
novo_fator_calibracao = 1#0.00005
novo_debounce = 0


angulo_inicial = float(input("Digite o ângulo inicial (°): "))

try:
    ser = serial.Serial(PORTA, BAUDRATE, timeout=1)
    print(f"[OK] Conectado na porta {PORTA} com baudrate {BAUDRATE}")
    time.sleep(2)
except Exception as e:
    print(f"[ERRO] Não foi possível abrir a porta serial: {e}")
    exit()

# Envia parâmetros iniciais
SYNC_CONFIG = 0xAB  
pacote = struct.pack('<BddI', SYNC_CONFIG, novo_fator_correcao, novo_fator_calibracao, novo_debounce)
ser.write(pacote)
ser.flush()
print("[INFO] Parâmetros enviados ao ESP32")
time.sleep(1)
ser.write(bytes([0xAC]))
ser.flush()
print("\n[INFO] Reset solicitado ao encoder.")
time.sleep(1)

print("\nLendo dados do encoder... (CTRL+C para parar)")

try:
    while True:
        # Verifica se há dados do encoder
        if ser.in_waiting >= 9:
            sync = ser.read(1)
            if sync == bytes([0xAA]):
                data = ser.read(8)
                if len(data) == 8:
                    grattingAngle = struct.unpack('<d', data)[0]
                    angulo_new = grattingAngle * 6.05417771e-5 - grattingAngle**2 * 2.39498272e-11 + grattingAngle**3 * 5.95802917e-16 -0.00217498

                    angulo = angulo_inicial + angulo_new
                    
                    print(f"\rÂngulo mesa: {angulo:.2f}° | Δθ: {grattingAngle:.2f}°", end="")

        #time.sleep(0.05)

except KeyboardInterrupt:
    print("\nLeitura encerrada pelo usuário.")
    ser.close()
