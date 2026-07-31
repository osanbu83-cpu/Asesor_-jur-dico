import hashlib
import os
import random
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
  # --- SECCIÓN DE CHAT Y ASESORÍA INTELIGENTE ---
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

      # Generar respuesta jurídica estructurada según el caso
      with st.chat_message("assistant"):
        with st.spinner(
            "El Agente Orquestador está analizando tu caso bajo el marco de la"
            " Constitución de Colombia..."
        ):

          texto_lower = pregunta_usuario.lower()

          # Seleccionar rama judicial basada en las palabras del usuario
          if any(
              w in texto_lower
              for w in ["salud", "eps", "vida", "derecho", "tutela", "hospital"]
          ):
            rama = "Derecho Constitucional / Acción de Tutela"
            analisis = (
                "Se evidencia una presunta vulneración a derechos"
                " fundamentales (como la salud, vida digna o petición),"
                " consagrados en los artículos de la Constitución Política de"
                " Colombia."
            )
            pasos = (
                "1. Recopilar historias clínicas, fórmulas o peticiones"
                " elevadas.\n   - 2. Redactar la Acción de Tutela dirigida a los"
                " Jueces de la República.\n   - 3. Radicar el documento en el"
                " juzgado de turno o mediante la plataforma virtual dispuesta"
                " para tal fin."
            )
          elif any(
              w in texto_lower
              for w in ["trabajo", "despido", "salario", "empleo", "patrono"]
          ):
            rama = "Derecho Laboral y de la Seguridad Social"
            analisis = (
                "El caso involucra relaciones de carácter laboral regidas por el"
                " Código Sustantivo del Trabajo y los principios constitucionales"
                " de protección al trabajador."
            )
            pasos = (
                "1. Reunir contratos, extractos, liquidaciones o pruebas de"
                " vinculación.\n   - 2. Acudir ante el Ministerio del Trabajo"
                " para solicitar una audiencia de conciliación prejudicial.\n  "
                " - 3. De no haber acuerdo, interponer demanda ordinaria ante"
                " un Juez Laboral."
            )
          elif any(
              w in texto_lower
              for w in ["multa", "policia", "comparendo", "espacio publico"]
          ):
            rama = "Derecho Administrativo / Policivo"
            analisis = (
                "El asunto se rige bajo la Ley 1801 de 2016 (Código Nacional de"
                " Seguridad y Convivencia Ciudadana) y los procedimientos"
                " contenciosos administrativos."
            )
            pasos = (
                "1. Verificar los tiempos de objeción (dentro de los 3 días"
                " hábiles siguientes).\n   - 2. Presentar recurso de apelación"
                " o descargos ante la inspección de policía respectiva.\n   -"
                " 3. Adjuntar pruebas físicas o testimoniales que desvirtúen el"
                " comparendo."
            )
          else:
            rama = (
                "Derecho Civil / General (Análisis Constitucional y de"
                " Obligaciones)"
            )
            analisis = (
                "Se analiza bajo las normas del Código Civil colombiano,"
                " contratos, obligaciones y los mecanismos ordinarios de"
                " resolución de conflictos entre particulares."
            )
            pasos = (
                "1. Agotar requisito de procedibilidad (Conciliación en"
                " centro autorizado o notarías).\n   - 2. Preparar el acervo"
                " probatorio documental y testimonial.\n   - 3. Iniciar el"
                " proceso judicial pertinente ante los jueces civiles"
                " municipales o del circuito."
            )

          respuesta_ia = (
              f"**[Agente Orquestador -> Rama Judicial Asignada]**\n\n"
              f"Hemos analizado tu caso basándonos en la Constitución Política"
              f" de Colombia y las normas vigentes.\n\n"
              f"1. **Rama asignada:** {rama}\n"
              f"2. **Análisis del caso:** {analisis}\n"
              f"3. **Pasos exactos a seguir:**\n   - {pasos}\n"
              f"4. **Recomendación:** Se sugiere contar con los soportes"
              f" documentales necesarios para respaldar el trámite.\n\n*(Preguntas"
              f" restantes: {st.session_state.preguntas_restantes})*"
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
