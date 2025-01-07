from motor.motor import Motor
from encoder.encoder import Encoder
import time

soma = 0
count = 0
encoder = Encoder()
motor = Motor()

encoder.start_monitoring()

print('Posicionando no furo')
while(encoder.on_hole != True):
    motor.step('descendente')
    time.sleep(0.03)

encoder.state_changes = 0
print('Posicionamento concluido')
print('Contando passos até o próximo furo')

for i in range(10):
    encoder.state_changes = 0
    count = 0
    while(encoder.state_changes == 0):
        count +=1
        motor.step('descendente')
        time.sleep(0.03)
    print(f"Passos dados na rodada {i} -> {count}")
    soma += count
    time.sleep(1)


print(f'Passo médio entre os furos: {soma/3}')

print('finalizando')
motor.deactivate()
motor.clean()