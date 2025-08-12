import streamlit as st
import openai
import os
from PIL import Image

# Configurar la clave de API
openai.api_key = st.secrets["OPENAI_API_KEY"]

# ID del asistente personalizado
ASSISTANT_ID = "asst_qQ2eCW3Os9ewKIpmoAX6dA6H"

st.set_page_config(page_title="INSIS Asistente", layout="centered")
st.title("💬 INSIS comisiones - Asistente OpenAI")

# 📷 Mostrar imagen precargada al iniciar
try:
    imagen_precargada = Image.open("logo.jpg")
    st.image(imagen_precargada, caption="Imagen de inspiración para tu viaje", use_container_width=True)
except FileNotFoundError:
    st.warning("No se encontró la imagen 'logo.jpg'. Asegúrate de que esté en el mismo directorio que el script.")


# 🧹 Opción en la barra lateral para borrar historial
if st.sidebar.button("🗑️ Borrar conversación"):
    st.session_state.pop("thread_id", None)
    st.session_state.pop("messages", None)
    st.rerun()


# Inicializar el hilo si no existe
if "thread_id" not in st.session_state:
    thread = openai.beta.threads.create()
    st.session_state.thread_id = thread.id

# Inicializar historial de mensajes
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar historial como chat natural
for msg in st.session_state.messages:
    with st.chat_message("user"):
        st.markdown(msg["user"])
    with st.chat_message("assistant"):
        st.markdown(msg["assistant"])

# Entrada del usuario en formato de chat
user_input = st.chat_input("Escribe tu mensaje...")

if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.spinner("Consultando al asistente..."):
        # Añadir el mensaje del usuario al hilo existente
        openai.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content=user_input
        )

        # Ejecutar el asistente
        run = openai.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=ASSISTANT_ID
        )

        # Esperar a que se complete
        while True:
            run_status = openai.beta.threads.runs.retrieve(
                thread_id=st.session_state.thread_id,
                run_id=run.id
            )
            if run_status.status == "completed":
                break

        # Obtener la respuesta más reciente
        messages = openai.beta.threads.messages.list(thread_id=st.session_state.thread_id)
        respuesta = messages.data[0].content[0].text.value

    with st.chat_message("assistant"):
        st.markdown(respuesta)

    # Guardar en historial
    st.session_state.messages.append({
        "user": user_input,
        "assistant": respuesta
    })


