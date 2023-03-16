# bibliotecas necessárias
from haversine import haversine 
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
import numpy as np
import folium
from streamlit_folium import folium_static

st.set_page_config(page_title = "Visão Restaurantes", layout = 'wide')

# ==============================================================================
#                                  FUNÇÕES
# ==============================================================================

#função para limpar os dados 
def clean_code( df1 ):
    """ Esta funcao tem a responsabilidade de limpar o dataframe
        
        Tipos de limpeza: 
        1. Remoção dos dados NaN
        2. Mudança do tipo da coluna de dados
        3. Remoção dos espaços das variáveis de texto
        4. Formatacao da coluna de datas 
        5. Limpeza da coluna de tempo (remoção do texto da variácel numérica
        
        Input: DataFrame 
        Output: DataFrame 
    """
    
    # 1. Convertendo a coluna Age de texto para int e retirando os NaNs encontrados
    linhas_selecionadas = df1['Delivery_person_Age'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :].copy()
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)

    linhas_selecionadas = df1['Road_traffic_density'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = df1['City'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = df1['Festival'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :].copy()

    # 2. Convertendo a coluna ratings de texto para float
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)

    # 3. convertendo a coluna order_date de texto para data
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format = '%d-%m-%Y')

    # 4. convertendo multiple_deliveries para inteiro
    linhas_selecionadas = df1['multiple_deliveries'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :].copy()
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)


    # 5. Removendo os espaços  
    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()


    # 6. remover o texto min dos numeros 
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x: x.split('(min) ')[1])
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)
    
    return df1

def distance(df1, fig):
    if fig == False:
        cols = ['Restaurant_longitude', 'Restaurant_latitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
        df1['Distance'] = df1.loc[:, cols].apply( lambda x: 
                          haversine(
                                  (x['Restaurant_latitude'], x['Restaurant_longitude']),
                                  (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis = 1)
        avg_distance = np.round(df1['Distance'].mean(), 2)

        return avg_distance
    else:
        cols = ['Restaurant_longitude', 'Restaurant_latitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
        df1['Distance'] = df1.loc[:, cols].apply( lambda x: 
                          haversine(
                                  (x['Restaurant_latitude'], x['Restaurant_longitude']),
                                  (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis = 1)

        avg_distance = df1.loc[:, ['City', 'Distance']].groupby('City').mean().reset_index()

        fig = go.Figure(data = [go.Pie(labels = avg_distance['City'], values = avg_distance['Distance'], pull=[0, 0.1, 0])])
        
        return fig

def avg_std_time_graph(df1):
    df_aux = df1.loc[:, ['Time_taken(min)', 'City']].groupby('City').agg({'Time_taken(min)': ['mean', 'std']})

    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()

    fig = go.Figure()
    fig.add_trace(go.Bar(name = 'Control', x = df_aux['City'], y = df_aux['avg_time'], error_y = dict(type = 'data', array = df_aux['std_time']))) #é o desvio padrão
    fig.update_layout(barmode = 'group')
                
    return fig

def avg_std_time_on_traffic(df1):
    df_aux = (df1.loc[:, ['Time_taken(min)', 'City','Road_traffic_density']]
                 .groupby(['City', 'Road_traffic_density'])
                 .agg({'Time_taken(min)': ['mean', 'std']}))

    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()

    fig = px.sunburst(df_aux, path = ['City', 'Road_traffic_density'], values = 'avg_time', 
                      color = 'std_time', color_continuous_scale = 'RdBu', 
                      color_continuous_midpoint = np.average(df_aux['std_time']))
    return fig

# ==============================================================================
#                 ÍNICIO DA ESTRUTURA LÓGICA DO CÓDIGO
# ==============================================================================

#import dataset
df = pd.read_csv('dataset/train.csv')

# Limpando os dados
df1 = clean_code(df)

# ==============================================================================
#                             BARRA LATERAL
# ==============================================================================

st.header ('Marketplace - Visão Restaurantes')

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fatest Delivery in Town')
st.sidebar.markdown("""---""")

st.sidebar.markdown('## Selecione uma data limite')

data_slider = st.sidebar.slider(
    'Até qual data?',
    value = pd.datetime(2022, 4, 13),
    min_value = pd.datetime(2022, 2, 11),
    max_value = pd.datetime(2022, 4, 6),
    format = 'DD-MM-YYYY'
)

st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect(
    'Condições do trânsito', 
    ['Low', 'Medium', 'High', 'Jam'],
    default = ['Low', 'Medium', 'High', 'Jam']
)
st.sidebar.markdown("""---""")
st.sidebar.markdown('### Powered by Comunidade DS')

# Fazer os filtros funcionarem nos dados 
# Filtro de data
linhas_selecionadas = df1['Order_Date'] < data_slider
df1 = df1.loc[linhas_selecionadas, :]

# Filtro de transito 
linhas_selecionadas = df1['Road_traffic_density'].isin( traffic_options )
df1 = df1.loc[linhas_selecionadas, :]

# ==============================================================================
#                             LAYOUT NO STREAMLIT
# ==============================================================================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '-', '-']) 

with tab1:
    with st.container():
        st.markdown("### Overall Metrics")
        
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            delivery_unique = len(df1.loc[:, 'Delivery_person_ID'].unique())
            col1.metric('Entregadores', delivery_unique)

        with col2:
            avg_distance = distance(df1, fig = False)
            col2.metric('A distancia media das entregas', avg_distance)             
            
        with col3:
            df_aux = (df1.loc[:, ['Time_taken(min)','Festival']]
                         .groupby( 'Festival')
                         .agg({'Time_taken(min)': ['mean', 'std']}))

            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            df_aux = np.round(df_aux.loc[df_aux['Festival'] == 'Yes', 'avg_time'], 2)
            
            col3.metric('Tempo médio de entrega com festival', df_aux)
            
        with col4:
            df_aux = (df1.loc[:, ['Time_taken(min)','Festival']]
                          .groupby( 'Festival')
                          .agg({'Time_taken(min)': ['mean', 'std']}))

            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            df_aux = np.round(df_aux.loc[df_aux['Festival'] == 'Yes', 'std_time'], 2)
            
            col4.metric('STD de entrega com festival', df_aux)
            
        with col5:
            df_aux = (df1.loc[:, ['Time_taken(min)','Festival']]
                         .groupby( 'Festival')
                         .agg({'Time_taken(min)': ['mean', 'std']}))

            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            df_aux = np.round(df_aux.loc[df_aux['Festival'] == 'No', 'avg_time'], 2)
            
            col5.metric('Tempo médio de entrega com festival', df_aux)
           
        with col6:
            df_aux = (df1.loc[:, ['Time_taken(min)','Festival']]
                          .groupby( 'Festival')
                          .agg({'Time_taken(min)': ['mean', 'std']}))

            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            df_aux = np.round(df_aux.loc[df_aux['Festival'] == 'No', 'std_time'], 2)
            
            col6.metric('STD de entrega com festival', df_aux)      
    
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("##### Distribuição da Distância")
            df_aux =( df1.loc[:, ['Time_taken(min)', 'City','Type_of_order']]
                     .groupby(['City', 'Type_of_order'])
                     .agg({'Time_taken(min)': ['mean', 'std']}))

            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            st.dataframe(df_aux, use_container_width = True)
        
        with col2:
            st.markdown("##### Tempo médio de entrega por cidade")
            fig = avg_std_time_graph(df1)
            st.plotly_chart(fig, use_container_width = True)              
        
        with st.container():
            st.markdown("### Distribuição do tempo ")
        
        col1, col2 = st.columns(2)
        with col1:            
            fig = distance(df1, fig = True)
            st.plotly_chart(fig, use_container_width = True)
        
        with col2:
            fig = avg_std_time_on_traffic(df1)
            st.plotly_chart(fig,  use_container_width = True)

                
