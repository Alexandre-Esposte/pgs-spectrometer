import serial
import struct
import time

# Ajuste a porta serial conforme seu sistema
ser = serial.Serial('/dev/ttyACM0', 115200)
time.sleep(2)  # espera a serial iniciar e Arduino resetar

SYNC_BYTE = 0xAA


sentido = 1  # 0 descendente, 1 ascendente
status = 1   # 0 parar, 1 iniciar
tempo = 255   # tempo em ms (1 byte)

# Monta struct: 4 bytes uint8
data = struct.pack('<BBB', sentido, status, tempo)

# Envia byte de sincronização
ser.write(bytes([SYNC_BYTE]))

# Envia struct
ser.write(data)

ser.flush()
print("Dados enviados:", [hex(x) for x in [SYNC_BYTE] + list(data)])
print("Dados enviados descompactados:", struct.unpack('<BBB', data))

ser.close()
