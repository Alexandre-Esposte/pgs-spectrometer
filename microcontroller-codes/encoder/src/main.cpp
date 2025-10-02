#include <Arduino.h>
#include "driver/pcnt.h"

#define ENCODER_PIN_A 34
#define ENCODER_PIN_B 35

// Variáveis ajustáveis
double fatorCorrecao = 0.00000760;
double fatorCalibracao = 0.000208;

double CONVERSAO;

volatile long encoderCount = 0;
volatile int16_t lastRawCount = 0; // Para controlar diferenças

// Configuração de quadratura no PCNT
void setupPCNT() {
  // Canal A
  pcnt_config_t pcntA = {};
  pcntA.pulse_gpio_num = ENCODER_PIN_A;
  pcntA.ctrl_gpio_num  = ENCODER_PIN_B;
  pcntA.unit           = PCNT_UNIT_0;
  pcntA.channel        = PCNT_CHANNEL_0;
  pcntA.pos_mode       = PCNT_COUNT_INC;
  pcntA.neg_mode       = PCNT_COUNT_DEC;
  pcntA.lctrl_mode     = PCNT_MODE_KEEP;
  pcntA.hctrl_mode     = PCNT_MODE_REVERSE;
  pcntA.counter_h_lim  = 32767;
  pcntA.counter_l_lim  = -32768;
  pcnt_unit_config(&pcntA);

  // Canal B
  pcnt_config_t pcntB = {};
  pcntB.pulse_gpio_num = ENCODER_PIN_B;
  pcntB.ctrl_gpio_num  = ENCODER_PIN_A;
  pcntB.unit           = PCNT_UNIT_0;
  pcntB.channel        = PCNT_CHANNEL_1;
  pcntB.pos_mode       = PCNT_COUNT_INC;
  pcntB.neg_mode       = PCNT_COUNT_DEC;
  pcntB.lctrl_mode     = PCNT_MODE_REVERSE;
  pcntB.hctrl_mode     = PCNT_MODE_KEEP;
  pcnt_unit_config(&pcntB);

  // Sem filtro → sem debounce
  pcnt_filter_disable(PCNT_UNIT_0);

  // Zera e inicia
  pcnt_counter_clear(PCNT_UNIT_0);
  pcnt_counter_resume(PCNT_UNIT_0);
  lastRawCount = 0;
}

// Task no Core 0 para envio via serial
void encoderTask(void *pvParameters) {
  int16_t rawCount = 0;

  while (true) {
    pcnt_get_counter_value(PCNT_UNIT_0, &rawCount);

    if (rawCount != lastRawCount) {
      encoderCount += (rawCount - lastRawCount);

      double encoderAngle = encoderCount * 360.0 / 20000.0;
      double grattingAngle = CONVERSAO * encoderCount;

      uint8_t sync = 0xAA;
      Serial.write(sync);
      Serial.write((uint8_t *)&encoderCount, sizeof(encoderCount));

      lastRawCount = rawCount;
    }
    vTaskDelay(2 / portTICK_PERIOD_MS);
  }
}

void setup() {
  Serial.begin(921600);
  delay(500);

  CONVERSAO = fatorCalibracao - fatorCorrecao;
  setupPCNT();

  xTaskCreatePinnedToCore(
    encoderTask,
    "encoderTask",
    2048,
    NULL,
    5,
    NULL,
    0 // Core 0
  );
}

void loop() {
  if (Serial.available() > 0) {
    uint8_t sync = Serial.read();

    if (sync == 0xAB && Serial.available() >= 20) {
      double novoFatorCorrecao;
      double novoFatorCalibracao;
      uint32_t dummy;

      Serial.readBytes((char *)&novoFatorCorrecao, sizeof(novoFatorCorrecao));
      Serial.readBytes((char *)&novoFatorCalibracao, sizeof(novoFatorCalibracao));
      Serial.readBytes((char *)&dummy, sizeof(dummy));

      fatorCorrecao = novoFatorCorrecao;
      fatorCalibracao = novoFatorCalibracao;
      CONVERSAO = fatorCalibracao - fatorCorrecao;
    }
    else if (sync == 0xAC) {
      encoderCount = 0;
      pcnt_counter_clear(PCNT_UNIT_0);
      lastRawCount = 0; // evita salto no próximo cálculo
    }
  }
}
