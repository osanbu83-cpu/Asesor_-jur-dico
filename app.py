import hashlib
import os
from groq import Groq
import streamlit as st

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

st.title("⚖️ Asesoría Jurídica Inteligente (Constitución y Leyes de Colombia)")

# --- SECCIÓN DE PAGO / MONETIZACIÓN ---
if not st.session_state.pago_verificado:
  st.markdown("### 🔒 Desbloquea tu Asesoría Legal")
  st.info(
      "Para habilitar tus **5 preguntas** con nuestros abogados expertos y"
      " redactores de documentos legales, debes realizar una consignación de"
      " **$5,000 COP** a la siguiente cuenta Nequi:"
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
        st.session_state.preguntas_restantes = 5
        st.session_state.mensajes = []
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
      "Expón tu caso o pide tu documento (ej. Redáctame una tutela, un derecho"
      " de petición...)"
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
        with st.spinner(
            "El abogado experto está redactando el documento y estructurando"
            " los pasos a seguir..."
        ):
          try:
            # Obtener la llave de Groq desde los Secrets de Streamlit
            groq_api_key = st.secrets["GROQ_API_KEY"]
            client = Groq(api_key=groq_api_key)

            # Llamada al modelo con instrucciones para redactar documentos y dar instrucciones de trámite
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Eres un abogado senior experto en todas las ramas"
                            " del derecho en Colombia. Cuando el usuario te"
                            " pida redactar un documento (como Acción de Tutela,"
                            " Derecho de Petición, Contrato, Demanda menor, etc.),"
                            " debes escribir el contenido completo, formal y"
                            " adaptado a la ley colombiana para que lo pueda"
                            " copiar y usar. Además, en tu respuesta debes"
                            " incluir obligatoriamente:\n1. **Rama del"
                            " derecho** aplicable.\n2. **Minuta o borrador del"
                            " documento** redactado formalmente.\n3. **Lugar o"
                            " entidad específica** a la que debe dirigirse el"
                            " usuario para presentarlo (ej. Juzgados, EPS,"
                            " Ministerio de Trabajo, Notaría, etc.).\n4."
                            " **Pasos exactos** que debe seguir para"
                            " radicarlo."
                        ),
                    },
                    {"role": "user", "content": pregunta_usuario},
                ],
                model="llama-3.1-8b-instant",
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

      # Si se agotan las preguntas, redirige al panel de pago
      if st.session_state.preguntas_restantes <= 0:
        st.warning(
            "Has agotado tus 5 preguntas. Redirigiendo al panel de pagos..."
        )
        st.session_state.pago_verificado = False

      st.rerun()
