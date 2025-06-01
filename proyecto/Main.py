# Crear archivo: streamlit_app.py
import streamlit as st
from Sistema_Recomendacion import SistemaRecomendacion

# Configurar página
st.set_page_config(
    page_title="Sistema de Recomendación de Libros",
    page_icon="📚",
    layout="wide"
)

# Inicializar sistema
if 'sistema' not in st.session_state:
    st.session_state.sistema = SistemaRecomendacion()

# Título principal
st.title("📚 Sistema de Recomendación con Dijkstra")
st.markdown("*Encuentra tu próxima lectura favorita usando algoritmos de grafos*")

# Sidebar para navegación
with st.sidebar:
    st.header("🔐 Autenticación")
    opcion = st.radio("Selecciona:", ["Iniciar Sesión", "Registrarse"])

# Panel principal
if opcion == "Registrarse":
    st.header("📝 Crear Nueva Cuenta")
    
    with st.form("registro"):
        col1, col2 = st.columns(2)
        
        with col1:
            usuario_id = st.text_input("ID de Usuario")
            password = st.text_input("Contraseña", type="password")
            
        with col2:
            generos = st.multiselect(
                "Géneros Favoritos (max 3)",
                ["Thriller", "Romance", "Ciencia Ficción", "Fantasía", "Histórico", "Misterio"],
                max_selections=3
            )
            
        ritmo = st.radio("Ritmo Preferido:", ["rápido", "lento"])
        final = st.radio("Finales Preferidos:", ["felices", "trágicos"])
        elementos = st.multiselect(
            "Elementos Narrativos (max 2):",
            ["giros", "personajes", "mundos", "romance", "acción"],
            max_selections=2
        )
        
        if st.form_submit_button("🚀 Crear Cuenta"):
            if usuario_id and password:
                exito, mensaje = st.session_state.sistema.registrar_nuevo_usuario(
                    usuario_id, password, generos, ritmo, final, elementos
                )
                if exito:
                    st.success(mensaje)
                    st.balloons()
                else:
                    st.error(mensaje)

elif opcion == "Iniciar Sesión":
    st.header("🔑 Acceder al Sistema")
    
    with st.form("login"):
        usuario_id = st.text_input("ID de Usuario")
        password = st.text_input("Contraseña", type="password")
        
        if st.form_submit_button("🔓 Iniciar Sesión"):
            if usuario_id and password:
                exito, mensaje = st.session_state.sistema.autenticar_usuario(usuario_id, password)
                if exito:
                    st.success(mensaje)
                    st.session_state.usuario_logueado = True
                else:
                    st.error(mensaje)

# Si el usuario está logueado, mostrar funcionalidades principales
if st.session_state.get('usuario_logueado', False):
    st.header("📖 Evaluar Libros")
    
    libros_evaluar = st.session_state.sistema.obtener_libros_para_evaluar()
    
    if libros_evaluar:
        libro_actual = libros_evaluar[0]  # Mostrar primer libro
        
        with st.container():
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader(f"📕 Libro: {libro_actual.titulo}")
                st.caption(f"ID: {libro_actual.id}")
                st.write(f"**Ritmo:** {libro_actual.ritmo}")
                st.write(f"**Final:** {libro_actual.final}")
                st.write(f"**Elementos:** {', '.join(libro_actual.elementos)}")
                st.write(f"**Puntuación:** {libro_actual.puntuacion_global}/5.0")
            
            with col2:
                col_a, col_r = st.columns(2)
                
                with col_a:
                    if st.button("✅ Aceptar", use_container_width=True):
                        exito, msg = st.session_state.sistema.evaluar_libro(libro_actual.id, True)
                        st.success("¡Libro aceptado!")
                        st.rerun()
                
                with col_r:
                    if st.button("❌ Rechazar", use_container_width=True):
                        exito, msg = st.session_state.sistema.evaluar_libro(libro_actual.id, False)
                        st.info("Libro rechazado")
                        st.rerun()
    
    # En la sección de mostrar recomendaciones
    if st.button("🔄 Generar Recomendaciones Personalizadas"):
        with st.spinner("Analizando tus preferencias..."):
            recomendaciones = st.session_state.sistema.obtener_recomendaciones()
            
        if recomendaciones:
            st.subheader("📚 Libros que podrían gustarte")
            for i, libro in enumerate(recomendaciones, 1):
                with st.expander(f"Recomendación #{i}: {libro.titulo}"):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**¿Por qué te lo recomendamos?** {libro.motivo}")
                        st.write("**Características:**")
                        st.write(f"- Ritmo: {libro.ritmo}")
                        st.write(f"- Final: {libro.final}")
                        st.write(f"- Elementos: {', '.join(libro.elementos)}")
                    
                    with col2:
                        st.metric("Valoración", f"{libro.puntuacion_global}/5.0")
        else:
            st.warning("No encontramos recomendaciones que coincidan con tus preferencias. Por favor, evalúa más libros.")
  
    # Botón de cerrar sesión
    if st.session_state.get('usuario_logueado', False):
        with st.sidebar:
            if st.button("🔓 Cerrar Sesión"):
                st.session_state.sistema.cerrar_sesion()
                st.session_state.usuario_logueado = False
                st.rerun()