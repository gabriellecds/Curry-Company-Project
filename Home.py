import streamlit as st
from PIL import Image

st.set_page_config(
    page_title = "Home",
)

st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fatest Delivery in Town')
st.sidebar.markdown("""---""")

st.write("# Curry Company Growth Dashboard")

st.markdown(
    """
    Growth Dashboard foi construído para acompanhar as métricas de crescimento dos Entregadores e Restaurantes. 
    ### Como utilizar esse Growth Dashboard?
    - Visão Empresa:
        - Visão Gerencial: métricas gerais de comportamento. 
        - Visão tática: indicadores semanais de crescimento. 
        - Visão Geográfica: insights de geolocalização.
    
    
    - Visão Entregador: 
        - Acompanhamento dos indicadores semanais de crescimento. 
        
        
    - Visão Restaurante:
        - Indicadores semanais de crescimento dos restaurantes. 
    
    ### Ask for Help
    - Time de Data Science no Discord 
         - @gabriellecosta#1532

    """ )
