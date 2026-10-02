import json
import random
import streamlit as st

# Configuración de la página
st.set_page_config(page_title="Simulador Medicina UCC", page_icon="🏥", layout="centered")

@st.cache_data
def cargar_banco():
    try:
        with open("banco_preguntas_medicina.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("No se encontró el archivo 'banco_preguntas_medicina.json'")
        return []

banco = cargar_banco()

if banco:
    st.title("🏥 Simulador de Admisión Medicina UCC")

    # Inicializar variables de estado
    if "preguntas" not in st.session_state:
        st.session_state.preguntas = []
        st.session_state.indice = 0
        st.session_state.puntaje = 0
        st.session_state.iniciado = False
        st.session_state.respondido = False
        st.session_state.opcion_seleccionada = None

    # Pantalla de Configuración
    if not st.session_state.iniciado:
        areas = sorted(list(set(q["area"] for q in banco)))
        area_sel = st.selectbox("Selecciona el área de estudio:", ["Todas las áreas"] + areas)
        
        filtradas = banco if area_sel == "Todas las áreas" else [q for q in banco if q["area"] == area_sel]
        
        cant_max = len(filtradas)
        num_preg = st.number_input(f"¿Cuántas preguntas quieres responder? (Máx {cant_max})", min_value=1, max_value=cant_max, value=min(10, cant_max))

        if st.button("🚀 Comenzar Simulador", type="primary"):
            st.session_state.preguntas = random.sample(filtradas, num_preg)
            st.session_state.indice = 0
            st.session_state.puntaje = 0
            st.session_state.iniciado = True
            st.session_state.respondido = False
            st.rerun()

    # Pantalla de Preguntas
    else:
        total = len(st.session_state.preguntas)
        i = st.session_state.indice

        if i < total:
            q = st.session_state.preguntas[i]
            
            st.progress((i) / total)
            st.caption(f"Pregunta {i+1} de {total} | **Área:** {q['area']}")
            st.subheader(q['pregunta'])

            # Botones de opciones
            opciones = q['opciones']
            
            for k, v in opciones.items():
                if st.button(f"{k}) {v}", key=k, disabled=st.session_state.respondido, use_container_width=True):
                    st.session_state.respondido = True
                    st.session_state.opcion_seleccionada = k
                    if k == q['correcta']:
                        st.session_state.puntaje += 1
                    st.rerun()

            # Mostrar retroalimentación tras responder
            if st.session_state.respondido:
                k_sel = st.session_state.opcion_seleccionada
                if k_sel == q['correcta']:
                    st.success("✅ ¡CORRECTO!")
                else:
                    st.error(f"❌ INCORRECTO. La respuesta correcta era la **{q['correcta']}**.")

                st.info(f"📖 **Explicación:** {q['explicacion']}\n\n💡 **Perla médica:** {q['perla']}")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("➡️ Siguiente Pregunta", type="primary"):
                        st.session_state.indice += 1
                        st.session_state.respondido = False
                        st.rerun()
                with col2:
                    if st.button("🛑 Finalizar ahora"):
                        st.session_state.indice = total
                        st.rerun()

        # Pantalla Final
        else:
            st.balloons()
            st.header("🎯 ¡Sesión Finalizada!")
            respondidas = i
            if respondidas > 0:
                pct = (st.session_state.puntaje / respondidas) * 100
                st.metric("Puntaje obtenido", f"{st.session_state.puntaje} / {respondidas}", f"{pct:.1f}% de precisión")
            else:
                st.write("No respondiste ninguna pregunta.")

            if st.button("🔄 Reiniciar Simulador"):
                st.session_state.iniciado = False
                st.rerun()
