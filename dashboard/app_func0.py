import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import psycopg2
#import ".env"

###################
# CONNECTION

conn_params = {
    'dbname': 'healthstack',    # Nome do seu banco de dados
    'user': 'postgres',         # Seu usuário do PostgreSQL
    'password': 'D1@l0g.d@t@.b@s3',       # Sua senha do PostgreSQL
    'host': '192.168.1.3',           # Endereço do servidor (pode ser localhost)
    'port': '5432'                 # Porta padrão do PostgreSQL
}

def consulta(query):
    try:
        conn = psycopg2.connect(**conn_params)
        print('conexão com o basnco de dados estabelecida com sucesso')

        df = pd.read_sql_query(query, conn)

        return df
    except Exception as e:
        print(f"Ocorreu um erro ao conectar ao banco de dados: {e}")



st.set_page_config(page_title="Dashlog", page_icon="ic_launcher_round.png", layout="wide")

# CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
# Chame a função para carregar o CSS
local_css("style.css")

st.title("Dados Médicos")
st.markdown('<style>div.block-container{padding-top:2rem}</style>', unsafe_allow_html=True)
# Configurar a página para largura total (comentar o código acima)


date="2024-09-29"
df_novo = consulta(f"""
select q1.fiui_email as email,
       locations.loca_name as ubs,
       bia_cafe1, bia_cafe2, bia_almoco1, bia_almoco2, bia_jantar1, bia_jantar2,
       ecg_cafe1, ecg_cafe2, ecg_almoco1, ecg_almoco2, ecg_jantar1, ecg_jantar2,
       libre,
       diario_alimentar,
       sono,
       q1.ecg1_date -- Adicionando a data do ECG 1
from (select fiui_email,
             ecg_cafe1, ecg_cafe2, ecg_almoco1, ecg_almoco2, ecg_jantar1, ecg_jantar2,
             max(case when ecg_type = 1 then date(ecg.time) else null end) as ecg1_date -- Data do ECG 1
      from (select fiui_email,
                   max(case when ecg_type = 1 and meal = 'Café da Manhã' then 1 else 0 end) as ecg_cafe1,
                   max(case when ecg_type = 2 and meal = 'Café da Manhã' then 1 else 0 end) as ecg_cafe2,
                   max(case when ecg_type = 1 and meal = 'Almoço' then 1 else 0 end) as ecg_almoco1,
                   max(case when ecg_type = 2 and meal = 'Almoço' then 1 else 0 end) as ecg_almoco2,
                   max(case when ecg_type = 1 and meal = 'Jantar' then 1 else 0 end) as ecg_jantar1,
                   max(case when ecg_type = 2 and meal = 'Jantar' then 1 else 0 end) as ecg_jantar2
            from (select firebase.fiui_email, ecg.ecg_type, ecg.time, meals.meal
                  from project_1_research.ecg as ecg
                  join project_1_research.meals as meals on ecg.session_id = meals.time
                  right join project_1_research.firebase_uids as firebase on ecg.user_id = firebase.fiui_uid and date(ecg.time) = '{date}'
                  group by firebase.fiui_email, ecg.session_id, ecg.ecg_type, ecg.time, meals.meal) q1
            group by fiui_email) q) as q1

         join

     (select fiui_email, bia_cafe1, bia_cafe2, bia_almoco1, bia_almoco2, bia_jantar1, bia_jantar2
      from (select fiui_email,
                   max(case when bia_type = 1 and meal = 'Café da Manhã' then 1 else 0 end) as bia_cafe1,
                   max(case when bia_type = 2 and meal = 'Café da Manhã' then 1 else 0 end) as bia_cafe2,
                   max(case when bia_type = 1 and meal = 'Almoço' then 1 else 0 end) as bia_almoco1,
                   max(case when bia_type = 2 and meal = 'Almoço' then 1 else 0 end) as bia_almoco2,
                   max(case when bia_type = 1 and meal = 'Jantar' then 1 else 0 end) as bia_jantar1,
                   max(case when bia_type = 2 and meal = 'Jantar' then 1 else 0 end) as bia_jantar2
            from (select firebase.fiui_email, bia_type, meals.meal
                  from project_1_research.bia as bia
                  join project_1_research.meals as meals on bia.session_id = meals.time
                  right join project_1_research.firebase_uids as firebase on bia.user_id = firebase.fiui_uid and date(bia.time) = '{date}'
                  group by firebase.fiui_email, bia.session_id, bia.bia_type, meals.meal) q1
            group by fiui_email) q) as q2
     on q1.fiui_email = q2.fiui_email

         join

     (select firebase.fiui_email,
             count(task_results) as diario_alimentar
      from project_1_research.task_results as task_results
               right join project_1_research.firebase_uids as firebase
           on
               task_results.user_id = firebase.fiui_uid
                   and date(task_results.submitted_at) = '{date}'
      group by firebase.fiui_email,
               date(task_results.submitted_at)) q3
     on q2.fiui_email = q3.fiui_email

         join

     (select firebase.fiui_email,
             count(libre) as libre
      from project_1_research.libre as libre
               right join
           project_1_research.firebase_uids as firebase
           on
               libre.libr_user_id = firebase.fiui_uid
                   and date(libre.libr_date_time_measure) = '{date}'
                   and libre.libr_type_measure = 'Automatico'
      group by firebase.fiui_email,
               date(libre.libr_date_time_measure)) q4
     on q4.fiui_email = q3.fiui_email
         join project_1_research.patients as patients on pati_email = q4.fiui_email
         join project_1_research.locations as locations on loca_id = patients.pati_location
         join
     (select firebase.fiui_email,
             (case when (count(sleep_sessions)) > 0 then 1 else 0 end) as sono
      from project_1_research.sleepsessions as sleep_sessions
               right join
           project_1_research.firebase_uids as firebase
           on
               sleep_sessions.user_id = firebase.fiui_uid
                   and date(sleep_sessions.end_time) = '{date}'
      group by firebase.fiui_email,
               date(sleep_sessions.end_time)) q5
     on q4.fiui_email = q5.fiui_email
order by email;

                          """)

#####################################################
#STREAMLIT

# css = '''
# <style>
#     section.main > div {max-width:75rem}
# </style>
# '''
# st.markdown(css, unsafe_allow_html=True)

df = pd.read_csv('dados_usuarios.csv')

df['Data'] = pd.to_datetime(df['Data'], errors='coerce')

# Calcular a data inicial e final para os filtros
startDate = df['Data'].min()
endDate = df['Data'].max()

# Criar a interface com o filtro de data usando Streamlit
col8 = st.columns(1)[0]
with col8:
    # Adicionar um campo de input para selecionar uma data
    selected_date = st.date_input("Selecionar data", startDate)


# Filtrar o dataframe para manter apenas as linhas com a data selecionada
# Certifique-se de que o nome da coluna de data está correto
filtered_data = df[df['Data'] == selected_date].copy()

ubs_options = df['Ubs'].dropna().unique().tolist()
patient_options = df['Nome'].dropna().unique().tolist()
st.sidebar.image("ic_launcher_round.png", use_column_width=False)  # Ícone

selected_patient = st.sidebar.selectbox("🔍 Procurando um paciente específico?",
                     patient_options,
                     index=None,
                     placeholder="Selecionar paciente",)
#if selected_patient == None:
#    st.write("Todos os pacientes")
#else:
#    st.write("Paciente: ", selected_patient)

#st.sidebar.text_input("🔍 Procurando um paciente específico?", placeholder="Pesquisar pacientes...")  # Campo de pesquisa
selected_ubs = st.sidebar.selectbox("🔍 Procurando uma UBS específica?",
                     ubs_options,
                     index=None,
                     placeholder="Selecionar UBS",)
if selected_ubs == None:
    if selected_patient == None:
        st.write("")
else:
    df = df[df["Ubs"] == selected_ubs].copy()
    st.write("Pacientes da ", selected_ubs)


if selected_patient:
    df_patient = df[df["Nome"] == selected_patient].copy()
    st.write("Paciente: ", selected_patient)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Café da Manhã")
        
    with col2:
        st.subheader("Almoço")
        
    with col3:
        st.subheader("Jantar")
else:
    st.subheader("Refeições")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Café da Manhã")
        plt.bar(df['c_bia1'], df['c_ecg1'], color='teal')
        plt.xticks(rotation=45)
        st.pyplot(plt)
        plt.clf()  # Limpar a figura

    with col2:
        st.subheader("Almoço")
        plt.bar(df['a_bia1'], df['a_ecg1'], color='cyan')
        plt.xticks(rotation=45)
        st.pyplot(plt)
        plt.clf()  # Limpar a figura

    with col3:
        st.subheader("Jantar")
        plt.bar(df['j_bia1'], df['j_ecg1'], color='royalblue')
        plt.xticks(rotation=45)
        st.pyplot(plt)
        plt.clf()  # Limpar a figura

    # Layout com gráficos para sono e livre (2ª linha)
    #st.subheader("Sono e Libre")

    col4, col5, col6, col7 = st.columns(4)

    # Gráfico de pizza com furo no meio (sono)
    with col4:
        st.subheader("Sono")
        fig1, ax1 = plt.subplots()
        ax1.pie(df['sono'].value_counts(), labels=df['sono'].unique(), autopct='%1.1f%%', startangle=90)
        centre_circle = plt.Circle((0, 0), 0.70, fc='white')
        fig1.gca().add_artist(centre_circle)
        ax1.axis('equal')
        st.pyplot(fig1)
        plt.clf()  # Limpar a figura

    # Gráfico de barras horizontal (livre)
    with col5:
        st.subheader("Medições")
        fig1, ax1 = plt.subplots()
        ax1.pie(df['libre'].value_counts(), labels=df['libre'].unique(), autopct='%1.1f%%', startangle=90)
        centre_circle = plt.Circle((0, 0), 0.70, fc='white')
        fig1.gca().add_artist(centre_circle)
        ax1.axis('equal')
        st.pyplot(fig1)
        plt.clf()  # Limpar a figura
        

    with col6:
        st.subheader("Libre")
        plt.barh(df['Nome'], df['libre'], color='teal')
        plt.xlabel('Quantidade de medições')
        st.pyplot(plt)
        plt.clf()  # Limpar a figura
        
    # Gráfico de barras vertical (diário alimentar)    
    with col7:
        st.subheader("Diário Alimentar")
        plt.bar(df['diario'], df['diario'], color='turquoise')
        plt.xticks(rotation=45)
        st.pyplot(plt)

    


    
# Layout em grid com 3 gráficos de barras (Refeições)
