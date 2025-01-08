from motor.motor import Motor
from encoder.encoder import Encoder
import time

soma = 0
count = 0
encoder = Encoder()
motor = Motor()

#encoder.start_monitoring()

print('Posicionando no furo')
while(encoder.on_hole != True):
    encoder.verificarFuro()
    motor.step('descendente')
    time.sleep(0.008)

encoder.state_changes = 0
print('Posicionamento concluido')
time.sleep(1)
print('Contando passos até o próximo furo')

#angulo_inicial = float(input('Informe o angulo inicial: '))

amostras = 5
for i in range(amostras):
    encoder.state_changes = 0
    count = 0
    while(encoder.state_changes == 0):
        count +=1
        encoder.verificarFuro()
        motor.step('ascendente')
        time.sleep(0.008)
    #angulo_final = float(input('Informe o angulo final: '))
    print(f"Passos dados na rodada {i} -> {count}")
    #print(f'Angulo inicial: {angulo_inicial}\nAngulo final: {angulo_final}\nVariação angular: {angulo_final - angulo_inicial}')
    
    #angulo_inicial = angulo_final     
    soma += count
    time.sleep(1)


print(f'Passo médio entre os furos: {soma/amostras}')

print('finalizando')
motor.deactivate()
motor.clean()