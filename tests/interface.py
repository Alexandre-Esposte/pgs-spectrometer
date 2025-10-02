import streamlit as st
import serial
import struct
import time

# Título e interface
st.title("Controle do Motor de Passo")
st.write("Interface simples para envio de comandos ao Arduino")

porta = st.text_input("Porta Serial", "/dev/ttyACM0")
velocidade = st.number_input("Baudrate", value=115200)

# Conecta apenas uma vez e armazena no session_state
if "ser" not in st.session_state:
    try:
        st.session_state.ser = serial.Serial(porta, int(velocidade), timeout=1)
        time.sleep(0.1)  # Aguarda estabilizar
        st.success("Conexão serial estabelecida!")
    except Exception as e:
        st.session_state.ser = None
        st.error(f"Erro ao abrir a porta serial: {e}")

# Parâmetros de controle
sentido = st.selectbox("Sentido", options=["Descendente", "Ascendente"])

col1, col2 = st.columns(2)
with col1:
    status_radio = st.radio("Status", ["Parar", "Iniciar"], index=0, label_visibility="collapsed")
with col2:
    st.write(" ")

tempo = st.slider("Tempo entre passos (ms)", min_value=3, max_value=255, value=100)

# Enviar comando
if st.button("Enviar Comando"):
    if st.session_state.ser and st.session_state.ser.is_open:
        try:
            SYNC_BYTE = 0xAA
            sentido_val = 0 if sentido == "Descendente" else 1
            status_val = 0 if status_radio == "Parar" else 1
            tempo_val = int(tempo)

            data = struct.pack('<BBB', sentido_val, status_val, tempo_val)
            ser = st.session_state.ser

            ser.write(bytes([SYNC_BYTE]))
            ser.write(data)
            ser.flush()

            st.success("Comando enviado com sucesso!")
            st.code(f"Dados enviados: {[hex(x) for x in [SYNC_BYTE] + list(data)]}")
            st.code(f"Desempacotado: {struct.unpack('<BBB', data)}")
        except Exception as e:
            st.error(f"Erro ao enviar: {e}")
    else:
        st.warning("Porta serial não conectada.")
