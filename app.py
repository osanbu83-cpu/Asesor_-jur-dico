import hashlib
import os
import streamlit as st
from google import genai

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
  # --- SECCIÓN DE CHAT Y AGENTES CON INTELIGENCIA ARTIFICIAL ---
  st.success(
      f"💬 Tienes **{st.session_state.preguntas_restantes} preguntas"
      " restantes** disponibles."
  )

  # Mostrar historial de chat
  for mensaje in st.session_state.mensajes:
    with st.chat_message(mensaje["role"]):
      st.markdown(mensaje["content"])

  # Entrada del usuario
  pregunta_usuario = st.chat_input(
      "Expón tu caso legal aquí (ej. Despido injustificado, tutela por salud..."
  )

  if pregunta_usuario:
    if st.session_state.preguntas_restantes > 0:
      # Agregar mensaje del usuario al historial
      st.session_state.mensajes.append(
          {"role": "user", "content": pregunta_usuario}
      )
      with st.chat_message("user"):
        st.markdown(pregunta_usuario)

      # Disminuir contador
      st.session_state.preguntas_restantes -= 1

      # Generar respuesta dinámica usando Google Gemini
      with st.chat_message("assistant"):
        with st.spinner(
            "El Agente Orquestador está analizando tu caso bajo el marco de la"
            " Constitución de Colombia..."
        ):
          try:
            # Inicializar cliente de Gemini utilizando los secretos de Streamlit
            client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

            prompt_sistema = (
                "Eres un Agente Orquestador y Abogado Expertos en Derecho y"
                " Constitución Política de Colombia. Analiza de forma"
                " profesional, empática y detallada el caso que expone el"
                " usuario. Estructura tu respuesta indicando: 1. Rama"
                " judicial asignada (Constitucional/Tutela, Penal, Laboral,"
                " Civil, Administrativo, etc.). 2. Análisis jurídico del caso"
                " basándote en la ley colombiana. 3. Pasos exactos y"
                " recomendaciones a seguir. 4. Borrador o estructura base si"
                " aplica."
            )

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[prompt_sistema, pregunta_usuario],
            )
            respuesta_ia = response.text

          except Exception as e:
            respuesta_ia = (
                "⚠️ Ocurrió un error al conectar con el servicio de Inteligencia"
                f" Artificial. Asegúrate de configurar tu `GEMINI_API_KEY` en"
                f" los Secrets de Streamlit. (Detalle: {e})"
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
