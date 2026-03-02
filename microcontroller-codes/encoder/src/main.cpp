#include <Arduino.h>
#include "driver/pcnt.h"

#define ENCODER_PIN_A 34
#define ENCODER_PIN_B 35
#define ENCODER_PIN_Z 33 

volatile long totalEncoderCount = 0; 
int16_t lastRawCount = 0;
float anguloAcumulado = 0;

unsigned long lastResetTime = 0; 
const int DEBOUNCE_Z = 50; // Milissegundos mínimos entre resets do Z (ajuste conforme a velocidade)

void IRAM_ATTR resetIndexISR() {
  unsigned long currentTime = millis();
  // Só reseta se o intervalo for maior que 50ms (evita resets por ruído)
  if (currentTime - lastResetTime > DEBOUNCE_Z) {
    pcnt_counter_clear(PCNT_UNIT_0);
    totalEncoderCount = 0;
    lastRawCount = 0;
    lastResetTime = currentTime;
  }
}

void setupPCNT() {
  pcnt_config_t pcnt_config = {};
  pcnt_config.pulse_gpio_num = ENCODER_PIN_A;
  pcnt_config.ctrl_gpio_num = ENCODER_PIN_B;
  pcnt_config.unit = PCNT_UNIT_0;
  pcnt_config.channel = PCNT_CHANNEL_0;
  pcnt_config.pos_mode = PCNT_COUNT_INC;
  pcnt_config.neg_mode = PCNT_COUNT_DEC;
  pcnt_config.lctrl_mode = PCNT_MODE_KEEP;
  pcnt_config.hctrl_mode = PCNT_MODE_REVERSE;
  pcnt_config.counter_h_lim = 32767;
  pcnt_config.counter_l_lim = -32768;
  pcnt_unit_config(&pcnt_config);

  pcnt_config.pulse_gpio_num = ENCODER_PIN_B;
  pcnt_config.ctrl_gpio_num = ENCODER_PIN_A;
  pcnt_config.channel = PCNT_CHANNEL_1;
  pcnt_config.pos_mode = PCNT_COUNT_INC;
  pcnt_config.neg_mode = PCNT_COUNT_DEC;
  pcnt_config.lctrl_mode = PCNT_MODE_REVERSE;
  pcnt_config.hctrl_mode = PCNT_MODE_KEEP;
  pcnt_unit_config(&pcnt_config);

  pcnt_set_filter_value(PCNT_UNIT_0, 1023); // Filtro máximo no hardware para A e B
  pcnt_filter_enable(PCNT_UNIT_0);
  pcnt_counter_clear(PCNT_UNIT_0);
  pcnt_counter_resume(PCNT_UNIT_0);
}

// Estrutura de Telemetria (ESP32 -> Python)
struct __attribute__((packed)) Telemetria {
  uint8_t sync = 0xAA;    // Byte de sincronismo
  int32_t pulsos;         // 4 bytes
  float angulo;           // 4 bytes
};

Telemetria tele;



void setup() {
  Serial.begin(921600);
  // Se estiver usando 4.8V direto, o ruído entra fácil aqui. 
  // O ideal seria um capacitor de 100nF entre o Pino 33 e o GND.
  pinMode(ENCODER_PIN_Z, INPUT_PULLUP); 
  attachInterrupt(digitalPinToInterrupt(ENCODER_PIN_Z), resetIndexISR, RISING);

  setupPCNT();
  //Serial.println("Filtro Z ativado. Rodando...");
}

void loop() {
  int16_t rawCount = 0;
  pcnt_get_counter_value(PCNT_UNIT_0, &rawCount);

  if (rawCount != lastRawCount) {
    int16_t diff = rawCount - lastRawCount;
    
    totalEncoderCount += diff;
    anguloAcumulado += (diff * (360.0 / 20000.0));
    
    lastRawCount = rawCount;

    // Alimenta a struct
    tele.pulsos = totalEncoderCount;
    tele.angulo = anguloAcumulado;

    // Envia o bloco binário de uma vez (9 bytes no total)
    Serial.write((uint8_t*)&tele, sizeof(Telemetria));

    //Serial.print("Ang. Var (Z): ");
    //Serial.print(totalEncoderCount * (360.0 / 20000.0), 2);
    //Serial.print("Delta theta: ");
    //Serial.print(anguloAcumulado, 2);
    //Serial.print(" | Contagens: ");
    //Serial.println(totalEncoderCount);
  }
  // Delay de 1ms para não travar a CPU
  delay(1);
}