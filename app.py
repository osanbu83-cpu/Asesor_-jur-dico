import hashlib
import os
import streamlit as st
from groq import Groq

# Configuración de la página
st.set_page_config(
    page_title="Asesoría Legal IA - Colombia", page_icon="⚖️", layout="centered"
)

# Directorio para almacenar hashes de comprobantes y evitar reutilización
UPLOAD_DIR = "comprobantes_verificados"
os.makedirs(UPLOAD_DIR, exist_ok=True)
HASH_LOG = os.path.join(UPLOAD_DIR, "used_hashes.txt")


def check_hash_exists(file_hash):
  if not os.path.exists(HASH_LOG):
    return False
  with open(HASH_LOG, "r") as f:
    hashes = f.read().splitlines()
    return file_hash in hashes


def save_hash(file_hash):
  with open(HASH_LOG, "a") as f:
    f.write(file_hash + "\n")


# Inicializar estados de sesión
if "pago_verificado" not in st.session_state:
  st.session_state.pago_verificado = False
if "preguntas_restantes" not in st.session_state:
  st.session_state.preguntas_restantes = 5
if "mensajes" not in st.session_state:
  st.session_state.mensajes = []

st.title("⚖️ Asesoría Jurídica Inteligente (Constitución de Colombia)")

# --- SECCIÓN DE PAGO / MONETIZACIÓN ---
if not st.session_state.pago_verificado:
  st.markdown("### 🔒 Desbloquea tu Asesoría Legal")
  st.info(
      "Para habilitar tus **5 preguntas** con nuestros agentes especializados"
      " en ramas judiciales, debes realizar una consignación de **$5,000 COP**"
      " a la siguiente cuenta Nequi:"
  )

  st.markdown(
      """
        * **Número Nequi:** `304 3711 233`
        * **A nombre de:** Blanca Mirella Gómez
        """
  )

  st.markdown("---")
  st.markdown("#### Sube el comprobante de pago para verificar:")

  comprobante_file = st.file_uploader(
      "Carga la imagen o PDF del comprobante de Nequi",
      type=["png", "jpg", "jpeg", "pdf"],
  )

  if comprobante_file is not None:
    file_bytes = comprobante_file.read()
    file_hash = hashlib.sha256(file_bytes).hexdigest()

    if check_hash_exists(file_hash):
      st.error(
          "❌ Este comprobante ya fue utilizado anteriormente. Por favor, sube"
          " un comprobante válido y único."
      )
    else:
      if st.button("Verificar Pago y Liberar Preguntas"):
        save_hash(file_hash)
        st.session_state.pago_verificado = True
        st.success(
            "¡Pago verificado con éxito! Se han habilitado tus 5 preguntas."
        )
        st.rerun()

else:
  # --- SECCIÓN DE CHAT Y ASESORÍA INTELIGENTE CON GROQ ---
  st.success(
      f"💬 Tienes **{st.session_state.preguntas_restantes} preguntas"
      " restantes** disponibles."
  )

  # Mostrar historial de chat
  for mensaje in st.session_state.mensajes:
    with st.chat_message(mensaje["role"]):
      st.markdown(mensaje["content"])

  pregunta_usuario = st.chat_input(
      "Expón tu caso legal aquí (ej. Divorcio, despido, tutela...)"
  )

  if pregunta_usuario:
    if st.session_state.preguntas_restantes > 0:
      st.session_state.mensajes.append(
          {"role": "user", "content": pregunta_usuario}
      )
      with st.chat_message("user"):
        st.markdown(pregunta_usuario)

      st.session_state.preguntas_restantes -= 1

      with st.chat_message("assistant"):
        with st.spinner("Consultando con la Inteligencia Artificial..."):
          try:
            # Obtener la llave de Groq desde los Secrets de Streamlit
            groq_api_key = st.secrets["GROQ_API_KEY"]
            client = Groq(api_key=groq_api_key)

            # Llamada al modelo ultrarrápido de Groq (Llama 3)
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Eres un abogado experto en la Constitución y las"
                            " leyes de Colombia. Responde de forma coherente,"
                            " directa y estructurada dando la rama del derecho,"
                            " análisis y pasos a seguir."
                        ),
                    },
                    {"role": "user", "content": pregunta_usuario},
                ],
                model="llama3-8b-8192",
            )
            respuesta_ia = chat_completion.choices[0].message.content
            respuesta_ia += (
                f"\n\n*(Preguntas restantes:"
                f" {st.session_state.preguntas_restantes})*"
            )
          except Exception as e:
            respuesta_ia = (
                f"⚠️ Error al conectar con Groq: {e}\n\nPor favor verifica que"
                " hayas configurado `GROQ_API_KEY` en los Secrets de"
                " Streamlit."
            )

        st.markdown(respuesta_ia)
        st.session_state.mensajes.append(
            {"role": "assistant", "content": respuesta_ia}
        )

      st.rerun()
    else:
      st.warning(
          "Has agotado tus 5 preguntas. Por favor realiza un nuevo pago para"
          " continuar con la asesoría."
      )
