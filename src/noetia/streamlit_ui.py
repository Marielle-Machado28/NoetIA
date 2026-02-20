from __future__ import annotations

from pathlib import Path

import streamlit as st


def inject_branding(sidebar_logo_path: str = "assets/logo-secondary.png") -> None:
    """
    Logo secundario SOLO en la barra lateral, arriba del todo.
    Lo ponemos dentro de una card (border) para que el fondo blanco del logo
    no se vea “pegado” al UI.
    """
    with st.sidebar:
        with st.container(border=True):
            st.image(sidebar_logo_path, use_container_width=True)


def hero_logo(logo_path: str = "assets/logo-main.png") -> None:
    """Muestra el logo principal grande en una card centrada."""
    _, mid, _ = st.columns([1, 5, 1])
    with mid:
        with st.container(border=True):
            st.image(logo_path, use_container_width=True)

