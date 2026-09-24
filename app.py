# app.py
import streamlit as st
import pandas as pd
from config import CIUDADES, ITEMS_TO_CHECK
from services import MarketAnalysisService

st.set_page_config(
    page_title="Albion Trade Hub",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; background-color: #ff4b4b; color: white; }
    </style>
""", unsafe_allow_html=True)

st.sidebar.title("🧭 Navegación")
menu = st.sidebar.radio(
    "Selecciona una herramienta:",
    ["🎯 Arbitraje Mercado Negro (Transporte)", "⚡ Flipping Local (Caerleon / Encantamiento)"]
)

st.sidebar.markdown("---")
st.sidebar.info("💡 **Consejo:** Combina el transporte en zonas rojas con el flipping seguro de encantamientos dentro de Caerleon.")

if menu == "🎯 Arbitraje Mercado Negro (Transporte)":
    st.title("🎯 Buscador de Arbitraje - Mercado Negro")
    st.write("Encuentra márgenes comprando en ciudades del continente y transportando hacia Caerleon.")

    col1, col2 = st.columns(2)
    with col1:
        ciudad_origen = st.selectbox("Ciudad de Origen (Compra):", CIUDADES[:-2], index=0)
    with col2:
        ordenar_por = st.selectbox("Ordenar resultados por:", ["Mayor % de ROI (Rentabilidad)", "Mayor Ganancia Neta (Plata)"])

    if st.button("🚀 Analizar Oportunidades de Transporte"):
        with st.spinner("Consultando servidores de Albion Online..."):
            df_ops = MarketAnalysisService.analizar_arbitraje_bm(ciudad_origen, ITEMS_TO_CHECK)
            
            if df_ops.empty:
                st.warning("No se encontraron oportunidades rentables de transporte en este momento.")
            else:
                if ordenar_por == "Mayor Ganancia Neta (Plata)":
                    df_ops.sort_values(by='ganancia_neta', ascending=False, inplace=True)
                else:
                    df_ops.sort_values(by='roi_%', ascending=False, inplace=True)

                st.success(f"¡Se encontraron {len(df_ops)} oportunidades!")
                st.dataframe(
                    df_ops[['nombre', 'calidad', 'precio_compra', 'precio_venta_bm', 'ganancia_neta', 'roi_%']],
                    use_container_width=True,
                    column_config={
                        "nombre": "Ítem",
                        "calidad": "Calidad",
                        "precio_compra": st.column_config.NumberColumn("Compra (Origen)", format="¥ %d"),
                        "precio_venta_bm": st.column_config.NumberColumn("Venta (Mercado Negro)", format="¥ %d"),
                        "ganancia_neta": st.column_config.NumberColumn("Ganancia Neta", format="¥ %d"),
                        "roi_%": st.column_config.NumberColumn("ROI", format="%.2f %%")
                    }
                )

elif menu == "⚡ Flipping Local (Caerleon / Encantamiento)":
    st.title("⚡ Flipping Local de Encantamiento (Caerleon)")
    st.write("Analiza precios de materiales base, calcula el costo real de encantamiento basado en la parte del equipo y descubre qué ítems dan más profit directo en el Mercado Negro.")

    # Selectores de configuración y ordenamiento
    st.subheader("⚙️ Configuración de Filtros")
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        tiers_seleccionados = st.multiselect(
            "Selecciona los Tiers que deseas buscar y analizar:",
            options=[4, 5, 6, 7, 8],
            default=[4, 5, 6, 7, 8],
            format_func=lambda x: f"Tier {x}"
        )
    with col_f2:
        ordenar_flipping_por = st.selectbox(
            "Ordenar resultados de flipping por:",
            ["Mayor % de ROI (Rentabilidad)", "Mayor Profit Neto (Plata)"],
            key="orden_flip"
        )

    if not tiers_seleccionados:
        st.warning("⚠️ Por favor selecciona al menos un Tier para continuar.")
    else:
        st.markdown("---")
        
# --- TABLA FIJA DE REQUISITOS CORRECTOS DE MATERIALES ---
        st.subheader("📋 Tabla Fija Oficial: Unidades por Parte de Equipamiento")
        st.write("Cantidades exactas para .1 (Runas), .2 (Almas) y .3 (Reliquias) sin importar el Tier:")
        
        df_requisitos = pd.DataFrame([
            {"Parte / Tipo de Equipamiento": "Armas Principales de Dos Manos (2H)", "Unidades Requeridas": "384 Unidades"},
            {"Parte / Tipo de Equipamiento": "Armas Principales de Una Mano (Main Hand)", "Unidades Requeridas": "288 Unidades"},
            {"Parte / Tipo de Equipamiento": "Túnicas (Armaduras de Cuerpo) y Bolsas", "Unidades Requeridas": "192 Unidades"},
            {"Parte / Tipo de Equipamiento": "Armas Secundarias, Capas, Cascos y Botas", "Unidades Requeridas": "96 Unidades"}
        ])
        st.dataframe(df_requisitos, use_container_width=True, hide_index=True)

        st.markdown("---")

        # 1. Tabla de cotización real de materiales en Caerleon
        st.subheader("📦 Cotización Actual de Materiales en Caerleon")
        with st.spinner("Cargando precios de runas, almas y reliquias..."):
            df_mats = MarketAnalysisService.obtener_tabla_materiales_caerleon(tiers_seleccionados)
            if not df_mats.empty:
                st.dataframe(
                    df_mats,
                    use_container_width=True,
                    column_config={
                        "Tier": "Tier",
                        "Runas (.1)": st.column_config.NumberColumn("Runas (.1)", format="¥ %d"),
                        "Almas (.2)": st.column_config.NumberColumn("Almas (.2)", format="¥ %d"),
                        "Reliquias (.3)": st.column_config.NumberColumn("Reliquias (.3)", format="¥ %d"),
                    }
                )

        st.markdown("---")
        
        # 2. Tabla analítica de oportunidades de flipping interno
        st.subheader("🎯 Oportunidades de Mejora y Venta al Mercado Negro")

        if st.button("🔍 Calcular Flips Rentables en Caerleon"):
            with st.spinner("Procesando costos reales por parte de equipo, materiales y órdenes del Mercado Negro..."):
                df_flips = MarketAnalysisService.analizar_flipping_caerleon(tiers_seleccionados, ordenar_flipping_por)

                if df_flips.empty:
                    st.warning("No se encontraron combinaciones rentables para encantar con los Tiers seleccionados.")
                else:
                    st.success(f"¡Se encontraron {len(df_flips)} opciones ideales para hacer flipping local!")
                    st.dataframe(
                        df_flips[['Ítem a Vender', 'Precio Base Caerleon', 'Costo Materiales', 'Costo Total Inversión', 'Precio BM (Orden Compra)', 'Profit (Ganancia Neta)', 'ROI %']],
                        use_container_width=True,
                        column_config={
                            "Ítem a Vender": "Ítem Objetivo",
                            "Precio Base Caerleon": st.column_config.NumberColumn("Precio Base Caerleon (.0)", format="¥ %d"),
                            "Costo Materiales": st.column_config.NumberColumn("Costo Materiales", format="¥ %d"),
                            "Costo Total Inversión": st.column_config.NumberColumn("Inversión Total", format="¥ %d"),
                            "Precio BM (Orden Compra)": st.column_config.NumberColumn("Precio BM (Orden)", format="¥ %d"),
                            "Profit (Ganancia Neta)": st.column_config.NumberColumn("Profit Neto", format="¥ %d"),
                            "ROI %": st.column_config.NumberColumn("ROI", format="%.2f %%")
                        }
                    )