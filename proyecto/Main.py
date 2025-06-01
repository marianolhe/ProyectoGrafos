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
                    st.session_state.usuario_logueado = True
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
    
    # Mostrar estadísticas del usuario
    with st.sidebar:
        st.header("📊 Tus Estadísticas")
        stats = st.session_state.sistema.obtener_estadisticas_usuario()
        if stats:
            st.metric("Libros Aceptados", stats['libros_aceptados'])
            st.metric("Libros Rechazados", stats['libros_rechazados'])
            st.write(f"**Ritmo Preferido:** {stats['preferencia_ritmo']}")
            st.write(f"**Final Preferido:** {stats['preferencia_final']}")
            
            # *** MOSTRAR géneros favoritos ***
            if stats['generos_favoritos']:
                st.write(f"**Géneros Favoritos:** {', '.join(stats['generos_favoritos'])}")
            
            if stats['elementos_favoritos']:
                st.write(f"**Elementos Favoritos:** {', '.join(stats['elementos_favoritos'])}")
    
    st.header("📖 Evaluar Libros")
    
    libros_evaluar = st.session_state.sistema.obtener_libros_para_evaluar()
    
    if libros_evaluar:
        libro_actual = libros_evaluar[0]  # Mostrar primer libro
        
        with st.container():
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader(f"📕 {libro_actual.titulo}")
                st.caption(f"ID: {libro_actual.id}")
                st.write(f"**Ritmo:** {libro_actual.ritmo}")
                st.write(f"**Final:** {libro_actual.final}")
                st.write(f"**Elementos:** {', '.join(libro_actual.elementos)}")
                st.write(f"**Puntuación:** {libro_actual.puntuacion_global}/5.0")
                
                # Mostrar información de compatibilidad si está disponible
                if hasattr(libro_actual, 'categoria_evaluacion'):
                    if libro_actual.categoria_evaluacion == 'alta_compatibilidad':
                        st.success("🎯 Alta compatibilidad con tus gustos")
                    elif libro_actual.categoria_evaluacion == 'media_compatibilidad':
                        st.info("👍 Buena compatibilidad")
                    else:
                        st.warning("🤔 Lectura exploratoria")
            
            with col2:
                col_a, col_r = st.columns(2)
                
                with col_a:
                    if st.button("✅ Aceptar", use_container_width=True):
                        exito, msg = st.session_state.sistema.evaluar_libro(libro_actual.id, True)
                        if exito:
                            st.success("¡Libro aceptado!")
                            st.rerun()
                        else:
                            st.error(msg)
                
                with col_r:
                    if st.button("❌ Rechazar", use_container_width=True):
                        exito, msg = st.session_state.sistema.evaluar_libro(libro_actual.id, False)
                        if exito:
                            st.info("Libro rechazado")
                            st.rerun()
                        else:
                            st.error(msg)
    else:
        st.info("¡Has evaluado todos los libros disponibles! 🎉")
    
    # Mostrar recomendaciones
    st.header("🎯 Recomendaciones Personalizadas con Dijkstra")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        if st.button("🔄 Generar Nuevas Recomendaciones", use_container_width=True):
            with st.spinner("🧠 Analizando patrones con algoritmo de Dijkstra..."):
                recomendaciones = st.session_state.sistema.obtener_recomendaciones()
                st.session_state.recomendaciones = recomendaciones
                if recomendaciones:
                    st.success(f"✅ {len(recomendaciones)} recomendaciones generadas")
                else:
                    st.warning("No se encontraron recomendaciones. Evalúa más libros.")
    
    with col2:
        st.info("🤖 Algoritmo: **Dijkstra** para encontrar usuarios similares")
    
    # Mostrar recomendaciones actuales
    if 'recomendaciones' in st.session_state and st.session_state.recomendaciones:
        st.subheader("📚 Tus Recomendaciones Personalizadas")
        
        for i, libro in enumerate(st.session_state.recomendaciones, 1):
            with st.expander(f"📖 {libro.titulo} (Compatibilidad: {libro.puntaje}/10.0)"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.caption(f"ID: {libro.id}")
                    st.write(f"**🎯 Por qué te lo recomendamos:** {libro.motivo}")
                    st.write(f"**📈 Características:** Ritmo {libro.ritmo}, Final {libro.final}")
                    if libro.elementos:
                        st.write(f"**🎭 Elementos:** {', '.join(libro.elementos)}")
                    
                    # Mostrar usuarios específicos que lo recomiendan
                    if hasattr(libro, 'nombres_usuarios_recomiendan') and libro.nombres_usuarios_recomiendan:
                        usuarios_texto = ", ".join(libro.nombres_usuarios_recomiendan[:3])  # Máximo 3 nombres
                        if len(libro.nombres_usuarios_recomiendan) > 3:
                            usuarios_texto += f" y {len(libro.nombres_usuarios_recomiendan) - 3} más"
                        st.write(f"**👥 Usuarios que lo aceptaron:** {usuarios_texto}")
                    elif hasattr(libro, 'usuarios_recomiendan') and libro.usuarios_recomiendan > 0:
                        st.write(f"**👥 Aceptado por:** {libro.usuarios_recomiendan} usuarios similares")
                
                with col2:
                    st.metric("Puntuación Global", f"{libro.puntuacion_global}/5.0")
                    # Asegurar que compatibilidad nunca supere 10/10
                    compatibilidad_mostrar = min(10.0, libro.puntaje)
                    st.metric("Compatibilidad", f"{compatibilidad_mostrar}/10.0")
                    
                    # Mostrar indicador visual de compatibilidad
                    porcentaje = int((compatibilidad_mostrar / 10.0) * 100)
                    if porcentaje >= 80:
                        st.success(f"🎯 {porcentaje}% Compatible")
                    elif porcentaje >= 60:
                        st.info(f"👍 {porcentaje}% Compatible")
                    else:
                        st.warning(f"🤔 {porcentaje}% Compatible")
                    
                    # Botón para evaluar directamente desde recomendaciones
                    if st.button(f"⭐ Evaluar", key=f"eval_{libro.id}"):
                        st.session_state[f"evaluar_{libro.id}"] = True
                        st.rerun()
                    
                    # Mostrar botones de evaluación si está activado
                    if st.session_state.get(f"evaluar_{libro.id}", False):
                        col_a, col_r = st.columns(2)
                        with col_a:
                            if st.button("✅", key=f"accept_{libro.id}", use_container_width=True):
                                exito, msg = st.session_state.sistema.evaluar_libro(libro.id, True)
                                if exito:
                                    st.success("¡Aceptado!")
                                    st.session_state[f"evaluar_{libro.id}"] = False
                                    # Actualizar recomendaciones
                                    st.session_state.recomendaciones = st.session_state.sistema.obtener_recomendaciones()
                                    st.rerun()
                        with col_r:
                            if st.button("❌", key=f"reject_{libro.id}", use_container_width=True):
                                exito, msg = st.session_state.sistema.evaluar_libro(libro.id, False)
                                if exito:
                                    st.info("Rechazado")
                                    st.session_state[f"evaluar_{libro.id}"] = False
                                    # Actualizar recomendaciones
                                    st.session_state.recomendaciones = st.session_state.sistema.obtener_recomendaciones()
                                    st.rerun()
    
    elif 'recomendaciones' in st.session_state:
        st.warning("🔍 No se encontraron nuevas recomendaciones. Evalúa más libros para mejorar las sugerencias.")
    else:
        st.info("👆 Haz clic en 'Generar Recomendaciones' para descubrir libros perfectos para ti")
    
    # Sección adicional: Historial de evaluaciones
    with st.expander("📈 Historial de Evaluaciones"):
        stats = st.session_state.sistema.obtener_estadisticas_usuario()
        if stats and (stats['libros_aceptados'] > 0 or stats['libros_rechazados'] > 0):
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("✅ Libros Aceptados")
                usuario_actual = st.session_state.sistema.usuario_actual
                if usuario_actual and usuario_actual.aceptados:
                    for libro_id in usuario_actual.aceptados:
                        libro_info = next((l for l in st.session_state.sistema.libros_sistema if l.id == libro_id), None)
                        if libro_info:
                            st.write(f"📚 {libro_info.titulo}")
                        else:
                            st.write(f"📚 Libro {libro_id}")
                else:
                    st.write("No has aceptado libros aún")
            
            with col2:
                st.subheader("❌ Libros Rechazados")
                if usuario_actual and usuario_actual.rechazados:
                    for libro_id in usuario_actual.rechazados:
                        libro_info = next((l for l in st.session_state.sistema.libros_sistema if l.id == libro_id), None)
                        if libro_info:
                            st.write(f"📚 {libro_info.titulo}")
                        else:
                            st.write(f"📚 Libro {libro_id}")
                else:
                    st.write("No has rechazado libros aún")
        else:
            st.write("Aún no has evaluado ningún libro. ¡Comienza evaluando algunos libros!")

# Botón de cerrar sesión
if st.session_state.get('usuario_logueado', False):
    with st.sidebar:
        st.markdown("---")
        if st.button("🔓 Cerrar Sesión", use_container_width=True):
            st.session_state.sistema.cerrar_sesion()
            st.session_state.usuario_logueado = False
            if 'recomendaciones' in st.session_state:
                del st.session_state.recomendaciones
            # Limpiar estados de evaluación
            keys_to_remove = [key for key in st.session_state.keys() if key.startswith('evaluar_')]
            for key in keys_to_remove:
                del st.session_state[key]
            st.rerun()

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666666;'>
        <p>📚 Sistema de Recomendación de Libros | Algoritmo de Dijkstra</p>
        <p>Encuentra tu próxima lectura favorita basada en usuarios con gustos similares</p>
    </div>
    """, 
    unsafe_allow_html=True
)