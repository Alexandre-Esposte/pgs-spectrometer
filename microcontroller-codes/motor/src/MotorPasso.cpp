#include <Arduino.h>
#include "MotorPasso.h"


const int MotorPasso::EXCITACAO_SIMPLES[3][3] = {
  {1, 0, 0},
  {0, 1, 0},
  {0, 0, 1}
};

const int MotorPasso::EXCITACAO_DUPLA[6][3] = {
  {1, 0, 0},
  {1, 1, 0},
  {0, 1, 0},
  {0, 1, 1},
  {0, 0, 1},
  {1, 0, 1}
};

MotorPasso::MotorPasso(int pino1, int pino2, int pino3, Excitacao tipo) {
  pinos[0] = pino1;
  pinos[1] = pino2;
  pinos[2] = pino3;

  tipoExcitacao = tipo;
  indicePasso = 0;

  // Desenergiza todas as bobinas por segurança
  for (int i = 0; i < 3; i++) {
    pinMode(pinos[i], OUTPUT);
    digitalWrite(pinos[i], LOW);
  }
}

void MotorPasso::desativar() {
  for (int i = 0; i < 3; i++) {
    digitalWrite(pinos[i], LOW);
  }
}

void MotorPasso::passo(Direcao direcao) {
  const int (*config)[3];
  int tamanho;
  int ordemPinos[3];


  if (tipoExcitacao == SINGLE) {
    config = EXCITACAO_SIMPLES;
    tamanho = 3;
  } else {
    config = EXCITACAO_DUPLA;
    tamanho = 6;
  }

  if (direcao == ASCENDENTE) {
    ordemPinos[0] = pinos[2];
    ordemPinos[1] = pinos[1];
    ordemPinos[2] = pinos[0];
  } else {
    ordemPinos[0] = pinos[0];
    ordemPinos[1] = pinos[1];
    ordemPinos[2] = pinos[2];
  }

  for (int i = 0; i < 3; i++) {
    digitalWrite(ordemPinos[i], config[indicePasso][i]);
  }

  indicePasso++;
  if (indicePasso >= tamanho) {
    indicePasso = 0;
  }
}

void MotorPasso::passos(int totalPassos, int delayMs, Direcao direcao) {
  if (tipoExcitacao == DOUBLE) {
    totalPassos *= 2;
  }

  for (int i = 0; i < totalPassos; i++) {
    passo(direcao);
    delay(delayMs);  
  }

  delay(100);  // tempo de descanso sem bloquear o core
  desativar();
}

void MotorPasso::setModo(Excitacao novoModo) {
  tipoExcitacao = novoModo;
  indicePasso = 0;  // Resetar o passo para garantir consistência na nova sequência
}
