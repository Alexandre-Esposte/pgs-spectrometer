import serial
import struct
import time
import threading

# ==== CONFIGURAÇÕES ====
PORTA_ENCODER = "/dev/ttyUSB0"   # ajuste para o ESP32
BAUD_ENCODER = 921600

PORTA_MOTOR = "/dev/ttyACM0"     # ajuste para o Arduino/motor
BAUD_MOTOR = 115200

SYNC_BYTE = 0xAA
SYNC_CONFIG_ENCODER = 0XAB
MARGEM_ERRO = 0.0009   # tolerância em graus

# Solicita parâmetros ao usuário
novo_fator_correcao =   0#0.000004
novo_fator_calibracao = 1#0.00005
novo_debounce = 0

# ==== VARIÁVEIS GLOBAIS ====
angulo_inicial = 0.0
angulo_atual = 0.0
angulo_alvo = 0.0
encoder_ref = 0.0
encoder_atual = 0.0
stop_flag = {"stop": False}


# ==== THREAD PARA LER O ENCODER ====
def ler_encoder(ser_encoder, stop_flag):
    global encoder_atual
    while not stop_flag["stop"]:
        try:
            if ser_encoder.in_waiting >= 9:  # 1 byte sync + 8 bytes double
                sync = ser_encoder.read(1)
                if sync == bytes([SYNC_BYTE]):
                    data = ser_encoder.read(8)
                    if len(data) == 8:
                        encoder_atual = struct.unpack('<d', data)[0]  # valor acumulativo em graus (resolução 0.01°)
                        encoder_atual = encoder_atual * 6.05417771e-5 - encoder_atual**2 * 2.39498272e-11 + encoder_atual**3 * 5.95802917e-16 -0.00217498

        except Exception as e:
            print(f"[ERRO ENCODER] {e}")
        time.sleep(0.005)

# ==== FUNÇÃO PARA ENVIAR COMANDO AO MOTOR ====
def enviar_comando(ser_motor, sentido, status, tempo):
    try:
        data = struct.pack('<BBB', sentido, status, tempo)
        ser_motor.write(bytes([SYNC_BYTE]))
        ser_motor.write(data)
        ser_motor.flush()
        print("\n[CMD] Enviado:", struct.unpack('<BBB', data))
    except Exception as e:
        print(f"[ERRO MOTOR] {e}")


# ==== PROGRAMA PRINCIPAL ====
def main():
    global angulo_inicial, angulo_alvo, encoder_ref, angulo_atual

    # Conectar encoder
    try:
        ser_encoder = serial.Serial(PORTA_ENCODER, BAUD_ENCODER, timeout=1)
        time.sleep(2)
        print(f"[OK] Conectado ao encoder em {PORTA_ENCODER}")
    except Exception as e:
        print(f"[FALHA] Não conectou encoder: {e}")
        return

    # Conectar motor
    try:
        ser_motor = serial.Serial(PORTA_MOTOR, BAUD_MOTOR, timeout=1)
        time.sleep(2)
        print(f"[OK] Conectado ao motor em {PORTA_MOTOR}")
    except Exception as e:
        print(f"[FALHA] Não conectou motor: {e}")
        ser_encoder.close()
        return


    try:
        angulo_inicial = float(input("Digite o ângulo verdadeiro inicial (°): "))
        angulo_alvo = float(input("Digite o ângulo alvo desejado (°): "))
    except ValueError:
        print("Valor inválido.")
        return
    pacote = struct.pack('<BddI', SYNC_CONFIG_ENCODER, novo_fator_correcao, novo_fator_calibracao, novo_debounce)
    ser_encoder.write(pacote)
    ser_encoder.flush()
    print("[INFO] Parâmetros enviados ao ESP32")
    time.sleep(1)
    ser_encoder.write(bytes([0xAC]))
    ser_encoder.flush()
    print("\n[INFO] Reset solicitado ao encoder.")
    time.sleep(1)
    # Ângulo inicial e alvo


    # Espera primeira leitura do encoder
    print("Aguardando leitura do encoder...")
    time.sleep(2)
    global encoder_atual
    encoder_ref = encoder_atual  # referência inicial
    print(f"[INFO] Encoder inicial = {encoder_ref:.2f}°",end="")

    # Inicia thread de leitura
    t = threading.Thread(target=ler_encoder, args=(ser_encoder, stop_flag))
    t.daemon = True
    t.start()

    print("\n=== CONTROLE AUTOMÁTICO ===")
    print(f"Objetivo: mover de {angulo_inicial:.2f}° para {angulo_alvo:.2f}°", end="")

    try:
        motor_ligado = False
        while True:
            # calcula ângulo atual baseado na referência
            angulo_atual = angulo_inicial + (encoder_atual - encoder_ref)

            erro = angulo_alvo - angulo_atual

            print(f"\rÂngulo atual: {angulo_atual:.2f}° | Alvo: {angulo_alvo:.2f}° | Erro: {erro:.2f}°")

            if abs(erro) <= MARGEM_ERRO:

                if motor_ligado:
                    enviar_comando(ser_motor, sentido=0, status=0, tempo=100)  # parar
                    motor_ligado = False
                    print("\n[INFO] Posição atingida!", end='')

                    # Atualiza referências para próxima movimentação
                    angulo_inicial = angulo_atual
                    encoder_ref = encoder_atual
                    print(f"[INFO] Nova referência definida: {angulo_inicial:.2f}°")
            else:
                if abs(erro) <= 0.03:
                    velocidade = 30
                else:
                    velocidade = 15
                if erro > 0:
                    enviar_comando(ser_motor, sentido=1, status=1, tempo=velocidade)  # ascendente
                    motor_ligado = True
                elif erro < 0:
                    enviar_comando(ser_motor, sentido=0, status=1, tempo=velocidade)  # descendente
                    motor_ligado = True

            time.sleep(0.07)

    except KeyboardInterrupt:
        print("\nEncerrado pelo usuário.")

    finally:
        stop_flag["stop"] = True
        enviar_comando(ser_motor, sentido=0, status=0, tempo=100)  # garantir parada
        ser_encoder.close()
        ser_motor.close()


if __name__ == "__main__":
    main()
