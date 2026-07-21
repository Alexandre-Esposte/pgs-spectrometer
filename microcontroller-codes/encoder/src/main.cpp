#include <Arduino.h>
#include "driver/pcnt.h"

#define ENCODER_PIN_A 34
#define ENCODER_PIN_B 35
#define ENCODER_PIN_Z 33 

// Ajuste conforme seu encoder: Se ele tem 5000 pulsos por volta
#define PPR 5000 

volatile int32_t totalHistorico = 0;   
volatile int32_t acumuladorDelta = 0;
int16_t lastRawCount = 0;

// Variáveis para filtro do Canal Z
volatile uint32_t ultimaInterrupcaoZ = 0;
const uint32_t DEBOUNCE_Z_MS = 50; // Ignora pulsos Z num intervalo menor que 50ms

struct __attribute__((packed)) Telemetria {
  uint8_t sync = 0xAA;    
  int32_t deltaPassos;    
  int32_t totalAbsoluto;  
};
Telemetria tele;

// INTERRUPÇÃO DO CANAL Z COM FILTRO DE TEMPO
void IRAM_ATTR trataCanalZ() {
  uint32_t agora = millis();
  
  // Só aceita o pulso Z se tiver passado pelo menos 50ms desde o último
  // Isso mata o ruído de alta frequência do motor
  if (agora - ultimaInterrupcaoZ > DEBOUNCE_Z_MS) {
    
    // CORREÇÃO: Em vez de zerar bruto, alinhamos ao múltiplo de PPR mais próximo
    // Isso evita "pulos" se o ruído bater fora de hora
    if (abs(totalHistorico) > (PPR / 2)) {
        int32_t resto = totalHistorico % PPR;
        totalHistorico -= resto;
    } else {
        totalHistorico = 0;
    }
    
    ultimaInterrupcaoZ = agora;
  }
}

void setupPCNT() {
  pcnt_config_t pcnt_config = {};
  pcnt_config.pulse_gpio_num = ENCODER_PIN_A;
  pcnt_config.ctrl_gpio_num = ENCODER_PIN_B; 
  pcnt_config.unit = PCNT_UNIT_0;
  pcnt_config.channel = PCNT_CHANNEL_0;
  
  pcnt_config.pos_mode = PCNT_COUNT_INC; 
  pcnt_config.neg_mode = PCNT_COUNT_DIS; // 1x para máxima estabilidade
  
  pcnt_config.lctrl_mode = PCNT_MODE_KEEP;    
  pcnt_config.hctrl_mode = PCNT_MODE_REVERSE; 
  
  pcnt_config.counter_h_lim = 32767; 
  pcnt_config.counter_l_lim = -32768;
  pcnt_unit_config(&pcnt_config);

  // Filtro de Hardware máximo para os canais A e B
  pcnt_set_filter_value(PCNT_UNIT_0, 1023);
  pcnt_filter_enable(PCNT_UNIT_0);

  pcnt_counter_clear(PCNT_UNIT_0);
  pcnt_counter_resume(PCNT_UNIT_0);
}

void setup() {
  Serial.begin(115200);
  
  pinMode(ENCODER_PIN_A, INPUT_PULLUP);
  pinMode(ENCODER_PIN_B, INPUT_PULLUP);
  pinMode(ENCODER_PIN_Z, INPUT_PULLUP);

  // Ativa interrupção no Canal Z
  attachInterrupt(digitalPinToInterrupt(ENCODER_PIN_Z), trataCanalZ, RISING);

  setupPCNT();
}

void loop() {
  int16_t rawCount = 0;
  pcnt_get_counter_value(PCNT_UNIT_0, &rawCount);

  int16_t diff = rawCount - lastRawCount;
  
  // Trava de sanidade contra saltos extraordinários de ruído
  if (diff != 0 && abs(diff) < 2000) {
    totalHistorico += diff;
    acumuladorDelta += diff;
    lastRawCount = rawCount;
  } else if (abs(diff) >= 2000) {
    lastRawCount = rawCount; 
  }

  static uint32_t lastSend = 0;
  if (millis() - lastSend >= 10) {
    tele.deltaPassos = acumuladorDelta;
    tele.totalAbsoluto = totalHistorico;
    Serial.write((uint8_t*)&tele, sizeof(Telemetria));
    
    acumuladorDelta = 0;
    lastSend = millis();
  }
  
  yield();
}