#ifndef MOTORPASSO_H
#define MOTORPASSO_H

#include <Arduino.h>

class MotorPasso {
    
  public:
    enum Excitacao { SINGLE, DOUBLE };
    enum Direcao { ASCENDENTE, DESCENDENTE };

    MotorPasso(int pino1, int pino2, int pino3, Excitacao tipo = SINGLE);
    
    void passo(Direcao direcao);
    void passos(int totalPassos, int delayMs, Direcao direcao = ASCENDENTE);
    void desativar();
    void setModo(Excitacao novoModo);

  private:
    int pinos[3];
    Excitacao tipoExcitacao;
    int indicePasso;

    const static int EXCITACAO_SIMPLES[3][3];
    const static int EXCITACAO_DUPLA[6][3];
};

#endif
