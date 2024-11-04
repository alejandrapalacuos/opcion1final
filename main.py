import streamlit as st

import numpy as np
from PIL import Image as Image, ImageOps as ImagOps
from keras.models import load_model
import platform

# Funciones para control por voz
import os
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
import time
import glob
import paho.mqtt.client as paho
import json
from gtts import gTTS
from googletrans import Translator

def on_publish(client, userdata, result):  # Callback para publicación MQTT
    print("el dato ha sido publicado \n")
    pass

def on_message(client, userdata, message):  # Callback para recibir mensajes MQTT
    global message_received
    time.sleep(2)
    message_received = str(message.payload.decode("utf-8"))
    st.write(message_received)

broker = "broker.mqttdashboard.com"
port = 1883
client1 = paho.Client("Alejita")
client1.on_message = on_message  # Asigna callback para mensajes

def pagina_inicio():
    st.title("Bienvenido a HomeDrive")
    if st.button("Empezar"):
        st.session_state.pagina_actual = "elegir_accion"
    else:
        st.write("Haz clic en 'Empezar' para continuar.")

def pagina_elegir_accion():
    st.title("Selecciona una acción")
    accion_seleccionada = st.selectbox("Elige una opción:", ("Garaje (Gestos)", "Luces (Control por Voz)"))
    
    if accion_seleccionada == "Garaje (Gestos)":
        st.session_state.pagina_actual = "control_gestos"
    elif accion_seleccionada == "Luces (Control por Voz)":
        st.session_state.pagina_actual = "control_voz"



def pagina_control_voz():
    st.title("Control por Voz")
    st.title("Interfaces Multimodales")
st.subheader("CONTROL POR VOZ")

image = Image.open('voice_ctrl.jpg')

st.image(image, width=200)




st.write("Toca el Botón y habla ")

stt_button = Button(label=" Inicio ", width=200)

stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
 
    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if ( value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }
    recognition.start();
    """))

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0)

if result:
    if "GET_TEXT" in result:
        st.write(result.get("GET_TEXT"))
        client1.on_publish = on_publish                            
        client1.connect(broker,port)  
        message =json.dumps({"Act1":result.get("GET_TEXT").strip()})
        ret= client1.publish("vocecita", message)

    
    try:
        os.mkdir("temp")
    except:
        pass

def main():
    # Inicializa el estado de la sesión si no existe
    if 'pagina_actual' not in st.session_state:
        st.session_state.pagina_actual = 'inicio'

    # Muestra la página correspondiente según el estado actual
    if st.session_state.pagina_actual == 'inicio':
        pagina_inicio()
    elif st.session_state.pagina_actual == 'elegir_accion':
        pagina_elegir_accion()
    elif st.session_state.pagina_actual == 'control_gestos':
        pagina_control_gestos()
    elif st.session_state.pagina_actual == 'control_voz':
        pagina_control_voz()

if __name__ == "__main__":
    main()
