import streamlit as st

def render_sidebar():
    # Este código CSS esconde el menú de navegación automático de Streamlit
    hide_streamlit_style = """
        <style>
        [data-testid="stSidebarNav"] {display: none;}
        </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    with st.sidebar:
        st.image("assets/logo-secondary.png", use_container_width=True)
        st.divider()
        
        st.markdown("### Navegación")
        
        # page_link es visualmente más limpio y nativo
        st.page_link("Home.py", label="Home", icon="🏠")
        st.page_link("pages/chatbot.py", label="Chatbot", icon="💬")
        st.page_link("pages/calendario.py", label="Calendario", icon="📅")
        st.page_link("pages/proyectos.py", label="Proyectos", icon="📂")
        st.page_link("pages/tareas.py", label="Tareas", icon="✅")
            
        st.divider()
        st.caption("NoetIA v1.0")