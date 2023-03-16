# bibliotecas necessárias
from haversine import haversine 
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
import folium
from streamlit_folium import folium_static

st.set_page_config(page_title = "Visão Entregadores", layout = 'wide')

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

def top_delivers(df1, top_asc):       
    df2 = (df1.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']]
              .groupby(['Delivery_person_ID','City'])
              .mean()
              .sort_values(['City', 'Time_taken(min)'], ascending=top_asc)
              .reset_index())

    df_aux01 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
    df_aux02 = df2.loc[df2['City'] == 'Urban', :].head(10)
    df_aux03 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)

    df3 = pd.concat( [df_aux01, df_aux02, df_aux03] ).reset_index( drop = True)
                
    return df3 

# ==============================================================================
#                 ÍNICIO DA ESTRUTURA LÓGICA DO CÓDIGO
# ==============================================================================

#import dataset
df = pd.read_csv('dataset\\train.csv')

# Limpando os dados
df1 = clean_code(df)

# ==============================================================================
#                             BARRA LATERAL
# ==============================================================================

st.header ('Marketplace - Visão Entregadores')

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

weather_options = st.sidebar.multiselect(
    'Condições do clima', 
    ['Sunny', 'Stormy', 'Sandstorms', 'Cloudy','Windy','Fog'],
    default = 'Sunny'
)

st.sidebar.markdown("""---""")
st.sidebar.markdown('### Powered by Comunidade DS')

st.sidebar.markdown("""---""")

# Fazer os filtros funcionarem nos dados 
# Filtro de data
linhas_selecionadas = df1['Order_Date'] < data_slider
df1 = df1.loc[linhas_selecionadas, :]

# Filtro de transito 
linhas_selecionadas = df1['Road_traffic_density'].isin( traffic_options )
df1 = df1.loc[linhas_selecionadas, :]

#Filtro Clima
#linhas_selecionadas = df1['Weatherconditions'].isin( weather_options )
#df1 = df1.loc[linhas_selecionadas, :]


# ==============================================================================
#                             LAYOUT NO STREAMLIT
# ==============================================================================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '-', '-']) 

with tab1: 
    with st.container():
        st.title("Overall Metrics")
        
        col1, col2, col3, col4 = st.columns (4, gap = 'large')
        with col1:
            #A maior idade
            maior_idade = df1.loc[:, 'Delivery_person_Age'].max()
            col1.metric("Maior idade", maior_idade)
        
        with col2:
            #A menor idade
            menor_idade = df1.loc[:, 'Delivery_person_Age'].min()
            col2.metric("Menor idade", menor_idade)
        
        with col3:
            #A melhor condição
            melhor_condicao = df1.loc[:, 'Vehicle_condition'].max()
            col3.metric("Melhor condição", melhor_condicao)
        
        with col4:
            #A pior condição
            pior_condicao = df1.loc[:, 'Vehicle_condition'].min()
            col4.metric("Pior condição", pior_condicao)
    
    with st.container(): 
        st.markdown("""___""")
        st.title("Avaliações")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Avaliação média por Entregador")
            df_avg_per_deliver = ( df1.loc[:, ['Delivery_person_ID', 'Delivery_person_Ratings']]
                                      .groupby('Delivery_person_ID')
                                      .mean()
                                      .reset_index() )
            st.dataframe(df_avg_per_deliver)
        
        with col2:
            st.markdown("#### Avaliação média por Trânsito")
            # média e desvio padrão
            df_avg_std_rating_by_traffic = ( df1.loc[:, ['Road_traffic_density','Delivery_person_Ratings']]
                                                .groupby('Road_traffic_density')
                                                .agg( { 'Delivery_person_Ratings':['mean', 'std'] } ) )

            #renomear as colunas
            df_avg_std_rating_by_traffic.columns = ['deliver_mean', 'deliver_std']
            df_avg_std_rating_by_traffic = df_avg_std_rating_by_traffic.reset_index()
            st.dataframe(df_avg_std_rating_by_traffic)
              
                
                
            st.markdown("#### Avaliação média por Clima")
            # média e desvio padrão
            df_avg_std_rating_by_weather = ( df1.loc[:, ['Weatherconditions','Delivery_person_Ratings']]
                                                .groupby('Weatherconditions')
                                                .agg( { 'Delivery_person_Ratings':['mean', 'std'] } ) )

            #renomear as colunas
            df_avg_std_rating_by_weather.columns = ['deliver_mean', 'deliver_std']
            df_avg_std_rating_by_weather = df_avg_std_rating_by_weather.reset_index()
            st.dataframe(df_avg_std_rating_by_weather)
    
    with st.container(): 
        st.markdown("""___""")
        st.title("Velocidade de Entrega")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Top entregadores mais rápidos")
            df3 = top_delivers(df1, top_asc=True)
            st.dataframe(df3)
        
        with col2:
            st.markdown("#### Top entregadores mais lentos")
            df3 = top_delivers(df1, top_asc=False)
            st.dataframe(df3)