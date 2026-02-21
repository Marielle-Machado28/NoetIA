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
        st.image("assets/logo-secondary.png", width='stretch')
        st.divider()
        
        st.markdown("### Navegación")
        
        # Como Home.py está en el mismo nivel que la carpeta 'pages',
        # la ruta es simplemente el nombre del archivo:
        st.page_link("Home.py", label="Home", icon="🏠")
        
        # Como las otras páginas están DENTRO de 'pages/', la ruta es:
        st.page_link("pages/chatbot.py", label="Chatbot", icon="💬")
        st.page_link("pages/Calendario.py", label="Calendario", icon="📅")
        st.page_link("pages/Proyectos.py", label="Proyectos", icon="📂")
        st.page_link("pages/Tareas.py", label="Tareas", icon="✅")
            
        st.divider()
        st.caption("NoetIA v1.0")