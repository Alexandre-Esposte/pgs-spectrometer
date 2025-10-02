#include <Arduino.h>
#include "MotorPasso.h"

#define motorPIN1 9 // Vermelho
#define motorPIN2 10 // Laranja
#define motorPIN3 11 // Marrom

// tamanho da estrutura: 4 bytes
struct Comando
{
  uint8_t sentido; // 0- descendente, 1- ascendente -> 1 byte
  uint8_t status;  // 0- desligar, 1-ligar -> 1 byte
  uint8_t tempo;   // tempo em ms entre passos -> 1 byte (corrigido de 2 bytes para 1)
};


MotorPasso motor(motorPIN1, motorPIN2, motorPIN3, MotorPasso::DOUBLE);
MotorPasso::Direcao sentido;

Comando cmd;
uint8_t buffer[sizeof(Comando)];
const uint8_t SYNC_BYTE = 0xAA;

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.setTimeout(100);
  while (Serial.available()) Serial.read(); // limpa buffer

  pinMode(motorPIN1, OUTPUT);
  pinMode(motorPIN2, OUTPUT);
  pinMode(motorPIN3, OUTPUT);

}

// Função que aguarda o byte de sincronização e lê a struct
bool lerComandoSincronizado() {
  // Aguarda SYNC_BYTE
  while (Serial.available()) {
    uint8_t b = Serial.read();
    if (b == SYNC_BYTE) {
      // SYNC recebido, tenta ler o resto da struct
      int bytesLidos = Serial.readBytes((char*)buffer, sizeof(Comando));
      if (bytesLidos == sizeof(Comando)) {
        memcpy(&cmd, buffer, sizeof(Comando));
        return true; // comando completo lido
      }
      // Se não leu o suficiente, espera nova tentativa
      return false;
    }
  }
  return false; // ainda não recebeu sync
}

void loop() {
  if (lerComandoSincronizado()) {
    // Serial.println("Comando recebido:");
    // Serial.print("  Sentido: ");
    // Serial.println(cmd.sentido);
    // Serial.print("  Status: ");
    // Serial.println(cmd.status);
    // Serial.print("  Tempo: ");
    // Serial.println(cmd.tempo);
    
    while (cmd.status)
    {

      if(cmd.sentido)
        sentido = MotorPasso::ASCENDENTE;
      else
        sentido = MotorPasso::DESCENDENTE;

      lerComandoSincronizado();


      motor.passo(sentido);
      delay(cmd.tempo);
    }
    
    motor.desativar();
  }
}
