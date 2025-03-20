import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import colors
import numpy as np
import psycopg2
import datetime
from sqlalchemy import create_engine
from urllib.parse import quote
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
        password_escaped = quote(conn_params['password'])

        # Construir a string de conexão com a senha escapada
        conn_str = f"postgresql+psycopg2://{conn_params['user']}:{password_escaped}@{conn_params['host']}:{conn_params['port']}/{conn_params['dbname']}"
        # Criar o engine usando SQLAlchemy
        engine = create_engine(conn_str)
        # Executar a query e obter o dataframe
        df = pd.read_sql_query(query, engine)

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


#df = pd.read_csv('dados_usuarios.csv')

#df['Data'] = pd.to_datetime(df['Data'], errors='coerce')

startDate = datetime.date(2024, 9, 30)
endDate = datetime.date(2024, 12, 31)

# Criar a interface com o filtro de data usando Streamlit
date_selected = startDate
col8 = st.columns(1)[0]
with col8:
    # Adicionar um campo de input para selecionar uma data
    date_selected = st.date_input("Selecionar data", startDate)

# Formatar para o formato "YYYY-MM-DD" usando strftime
date = date_selected.strftime("%Y-%m-%d")

print(date)

dfq = consulta(f"""
select q1.fiui_email as email,
    bia_breakfast1, bia_breakfast2, bia_lunch1, bia_lunch2, bia_dinner1, bia_dinner2,
    ecg_breakfast1, ecg_breakfast2, ecg_lunch1, ecg_lunch2, ecg_dinner1, ecg_dinner2,
    libre,
    food_journal,
    sleep
from (select fiui_email, ecg_breakfast1, ecg_breakfast2, ecg_lunch1, ecg_lunch2, ecg_dinner1, ecg_dinner2
      from (select fiui_email,
                   max(case when ecg_type = 1 and meal = 'breakfast' then 1 else 0 end) as ecg_breakfast1,
                   max(case when ecg_type = 2 and meal = 'breakfast' then 1 else 0 end) as ecg_breakfast2,
                   max(case when ecg_type = 1 and meal = 'lunch' then 1 else 0 end) as ecg_lunch1,
                   max(case when ecg_type = 2 and meal = 'lunch' then 1 else 0 end) as ecg_lunch2,
                   max(case when ecg_type = 1 and meal = 'dinner' then 1 else 0 end) as ecg_dinner1,
                   max(case when ecg_type = 2 and meal = 'dinner' then 1 else 0 end) as ecg_dinner2
            from (select firebase.fiui_email, ecg.ecg_type, meals.meal
                  from project_3_research.ecg as ecg
                  join project_3_research.meals as meals on ecg.session_id = meals.time
                  right join project_3_research.firebase_uids as firebase on ecg.user_id = firebase.fiui_uid and date(ecg.time) = '{date}'
                  group by firebase.fiui_email, ecg.session_id, ecg.ecg_type, meals.meal) q1
            group by fiui_email) q) as q1

         join

     (select fiui_email, bia_breakfast1, bia_breakfast2, bia_lunch1, bia_lunch2, bia_dinner1, bia_dinner2
      from (select fiui_email,
                   max(case when bia_type = 1 and meal = 'breakfast' then 1 else 0 end) as bia_breakfast1,
                   max(case when bia_type = 2 and meal = 'breakfast' then 1 else 0 end) as bia_breakfast2,
                   max(case when bia_type = 1 and meal = 'lunch' then 1 else 0 end) as bia_lunch1,
                   max(case when bia_type = 2 and meal = 'lunch' then 1 else 0 end) as bia_lunch2,
                   max(case when bia_type = 1 and meal = 'dinner' then 1 else 0 end) as bia_dinner1,
                   max(case when bia_type = 2 and meal = 'dinner' then 1 else 0 end) as bia_dinner2
            from (select firebase.fiui_email, bia_type, meals.meal
                  from project_3_research.bia as bia
                  join project_3_research.meals as meals on bia.session_id = meals.time
                  right join project_3_research.firebase_uids as firebase on bia.user_id = firebase.fiui_uid and date(bia.time) = '{date}'
                  group by firebase.fiui_email, bia.session_id, bia.bia_type, meals.meal) q1
            group by fiui_email) q) as q2
     on q1.fiui_email = q2.fiui_email

         join

     (select firebase.fiui_email,
             count(task_results) as food_journal
      from project_3_research.task_results as task_results
               right join project_3_research.firebase_uids as firebase
           on
               task_results.user_id = firebase.fiui_uid
                   and date(task_results.submitted_at) = '{date}'
      group by firebase.fiui_email,
               date(task_results.submitted_at)) q3
     on q2.fiui_email = q3.fiui_email

         join

     (select firebase.fiui_email,
             count(libre) as libre
      from project_3_research.libre as libre
               right join
           project_3_research.firebase_uids as firebase
           on
               libre.libr_user_id = firebase.fiui_uid
                   and date(libre.libr_date_time_measure) = '{date}'
                   and libre.libr_type_measure = 'Automatico'
      group by firebase.fiui_email,
               date(libre.libr_date_time_measure)) q4
     on q4.fiui_email = q3.fiui_email
         join
     (select firebase.fiui_email,
             (case when (count(sleep_sessions)) > 0 then 1 else 0 end) as sleep
      from project_3_research.sleepsessions as sleep_sessions
               right join
           project_3_research.firebase_uids as firebase
           on
               sleep_sessions.user_id = firebase.fiui_uid
                   and date(sleep_sessions.start_time) = '{date}'
      group by firebase.fiui_email,
               date(sleep_sessions.start_time)) q5
     on q4.fiui_email = q5.fiui_email
order by email;

                          """)


# Filtrar o dataframe para manter apenas as linhas com a data selecionada
# Certifique-se de que o nome da coluna de data está correto
#filtered_data = df[df['Data'] == date].copy()

#####################################################
#STREAMLIT

# css = '''
# <style>
#     section.main > div {max-width:75rem}
# </style>
# '''
# st.markdown(css, unsafe_allow_html=True)

#ubs_options = dfq['ubs'].dropna().unique().tolist()

#st.sidebar.image("ic_launcher_round.png", use_column_width=False)  # Ícone

#selected_ubs = st.sidebar.selectbox("🔍 Procurando uma UBS específica?",
     #                ubs_options,
      #               index=None,
       #              placeholder="Selecionar UBS",)
#if selected_ubs == None:
#    if selected_patient == None:
#        st.write("")
#else:
#    dfq = dfq[dfq["ubs"] == selected_ubs].copy()
#    st.write("Pacientes da ", selected_ubs)


patient_options = dfq['email'].dropna().unique().tolist()
selected_patient = st.sidebar.selectbox("🔍 Procurando um paciente específico?",
                     patient_options,
                     index=None,
                     placeholder="Selecionar paciente",)

if selected_patient:
    dfq_patient = dfq[dfq["email"] == selected_patient].copy()
    st.write("Paciente: ", selected_patient)
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Café da Manhã")
        selected_cafe_pac = ['bia_breakfast1', 'ecg_breakfast1', 'bia_breakfast2', 'ecg_breakfast2']
        dfq_cafe_pac = dfq[selected_cafe_pac]

        fig, ax = plt.subplots()
        table_cafe = ax.table(cellText=[dfq_cafe_pac.iloc[0].values],  # Selecionar apenas a primeira linha
                            colLabels=selected_cafe_pac, cellLoc='center', loc='center')

        for j in range(dfq_cafe_pac.shape[1]):  # Para cada coluna
            value = dfq_cafe_pac.iloc[0, j]  # Obter o valor da célula da primeira linha
            if value == 0:
                table_cafe[(0, j)].set_facecolor("lightcoral")  
            elif value == 1:
                table_cafe[(0, j)].set_facecolor("lightgreen")  

        table_cafe.auto_set_font_size(False)  
        table_cafe.set_fontsize(12)  
        table_cafe.scale(1.2, 0.9)  
        ax.axis('off')  

        fig.patch.set_visible(False)
        ax.patch.set_visible(False)

        plt.title("Café")
        #plt.savefig('cafe_pac.png')
        plt.legend()
        st.pyplot(plt)
        plt.clf()
        
    with col2:
        st.subheader("----")
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("Almoço")
        selected_lunch_pac = ['bia_lunch1', 'ecg_lunch1', 'bia_lunch2', 'ecg_lunch2']
        dfq_lunch_pac = dfq[selected_lunch_pac]

        fig, ax = plt.subplots()
        table_lunch = ax.table(cellText=[dfq_lunch_pac.iloc[0].values],  # Selecionar apenas a primeira linha
                            colLabels=selected_lunch_pac, cellLoc='center', loc='center')

        for j in range(dfq_lunch_pac.shape[1]):  # Para cada coluna
            value = dfq_lunch_pac.iloc[0, j]  # Obter o valor da célula da primeira linha
            if value == 0:
                table_lunch[(0, j)].set_facecolor("lightcoral")  
            elif value == 1:
                table_lunch[(0, j)].set_facecolor("lightgreen")  

        table_lunch.auto_set_font_size(False)  
        table_lunch.set_fontsize(12)  
        table_lunch.scale(1.2, 0.9)  
        ax.axis('off')  

        fig.patch.set_visible(False)
        ax.patch.set_visible(False)

        plt.title("Almoço")
        #plt.savefig('lunch_pac.png')
        plt.legend()
        st.pyplot(plt)
        plt.clf()
        
    with col4:
        st.subheader("---")
        
    col5, col6 = st.columns(2)
    with col5:
        st.subheader("Jantar")
        selected_dinner_pac = ['bia_dinner1', 'ecg_dinner1', 'bia_dinner2', 'ecg_dinner2']
        dfq_dinner_pac = dfq[selected_dinner_pac]
        
        fig, ax = plt.subplots()
        table_dinner = ax.table(cellText=[dfq_dinner_pac.iloc[0].values],
                                colLabels=selected_dinner_pac, cellLoc='center', loc='center')
        
        for j in range (dfq_dinner_pac.shape[1]):
            value = dfq_dinner_pac.iloc[0, j]
            if value == 0:
                table_dinner[(0, j)].set_facecolor("lightcoral")
            elif value == 1:
                table_lunch[(0, j)].set_facecolor("lightgreen")
                
        table_dinner.auto_set_font_size(False)
        table_dinner.set_fontsize(12)
        table_dinner.scale(1.2, 0.9)
        ax.axis('off')
        
        fig.patch.set_visible(False)
        ax.patch.set_visible(False)
        
        plt.title("Jantar")
        #plt.savefig('dinner_pac.png')
        plt.legend()
        st.pyplot(plt)
        plt.clf()
        
    with col6:
        st.subheader('---')
    
else:
    st.subheader("Refeições")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Café da Manhã")
        selected_cafe = ['bia_breakfast1', 'ecg_breakfast1', 'bia_breakfast2', 'ecg_breakfast2']
        dfq_cafe = dfq[selected_cafe]
        count_1s = dfq_cafe.sum(axis=0)  # Quantos 1s em cada coluna
        count_0s = dfq_cafe.shape[0] - count_1s  # O restante são 0s

        # Posições no eixo X
        labels = dfq_cafe.columns
        x = np.arange(len(labels))
        # Plotar barras empilhadas
        plt.bar(x, count_0s, label='0', color='lightblue')
        plt.bar(x, count_1s, bottom=count_0s, label='1', color='cyan')
        plt.xticks(x, labels)  # Adicionar rótulos no eixo x
        plt.yticks([])
        plt.ylabel('Participantes')
        
        # Remover o grid
        plt.grid(False)
        # Definir o fundo do gráfico como transparente
        plt.gca().set_facecolor('none')
        # Remover as bordas
        plt.gca().spines['top'].set_visible(False)
        plt.gca().spines['right'].set_visible(False)
        #plt.gca().spines['left'].set_visible(False)
        #plt.gca().spines['bottom'].set_visible(False)

        plt.savefig('cafe.png')
        plt.legend()
        st.pyplot(plt)
        plt.clf()


    with col2:
        st.subheader("Almoço")
        selected_almoco = ['bia_lunch1', 'ecg_lunch1', 'bia_lunch2', 'ecg_lunch2']
        dfq_almoco = dfq[selected_almoco]
        count_1s = dfq_cafe.sum(axis=0)  # Quantos 1s em cada coluna
        count_0s = dfq_cafe.shape[0] - count_1s  # O restante são 0s

        # Posições no eixo X
        labels = dfq_almoco.columns
        x = np.arange(len(labels))
        # Plotar barras empilhadas
        plt.bar(x, count_0s, label='0', color='lightblue')
        plt.bar(x, count_1s, bottom=count_0s, label='1', color='cyan')
        plt.xticks(x, labels)  # Adicionar rótulos no eixo x
        plt.yticks([])
        plt.ylabel('Participantes')
        
        # Remover o grid
        plt.grid(False)
        # Definir o fundo do gráfico como transparente
        plt.gca().set_facecolor('none')
        # Remover as bordas
        plt.gca().spines['top'].set_visible(False)
        plt.gca().spines['right'].set_visible(False)
        #plt.gca().spines['left'].set_visible(False)
        #plt.gca().spines['bottom'].set_visible(False)
        
        plt.savefig('almoco.png')
        plt.legend()
        st.pyplot(plt)
        plt.clf()

    with col3:
        st.subheader("Jantar")
        selected_jantar = ['bia_dinner1', 'ecg_dinner1', 'bia_dinner2', 'ecg_dinner2']
        dfq_jantar = dfq[selected_jantar]
        count_1s = dfq_jantar.sum(axis=0)  # Quantos 1s em cada coluna
        count_0s = dfq_jantar.shape[0] - count_1s  # O restante são 0s

        # Posições no eixo X
        labels = dfq_jantar.columns
        x = np.arange(len(labels))
        # Plotar barras empilhadas
        plt.bar(x, count_0s, label='0', color='lightblue')
        plt.bar(x, count_1s, bottom=count_0s, label='1', color='cyan')
        plt.xticks(x, labels)  # Adicionar rótulos no eixo x
        plt.yticks([])
        plt.ylabel('Participantes')
        
        # Remover o grid
        plt.grid(False)
        # Definir o fundo do gráfico como transparente
        plt.gca().set_facecolor('none')
        # Remover as bordas
        plt.gca().spines['top'].set_visible(False)
        plt.gca().spines['right'].set_visible(False)
        #plt.gca().spines['left'].set_visible(False)
        #plt.gca().spines['bottom'].set_visible(False)

        plt.savefig('jantar.png')
        plt.legend()
        st.pyplot(plt)
        #plt.clf()
        
    col4, col5, col6, col7 = st.columns(4)

    # Gráfico de pizza com furo no meio (sono)
    with col4:
        st.subheader("Sono")
        fig1, ax1 = plt.subplots()
        sono_counts = dfq['sleep'].value_counts()
        ax1.pie(sono_counts, labels=sono_counts.index, autopct='%1.1f%%', startangle=90)
        centre_circle = plt.Circle((0, 0), 0.70, fc='white')
        fig1.gca().add_artist(centre_circle)
        ax1.axis('equal')
        plt.savefig('sono.png')
        st.pyplot(fig1)

    # Gráfico de barras horizontal (livre)
    with col5: #################################################
        st.subheader("Medições")
        #dfq_filtered = dfq.dropna(subset=['libre'])
        #maior_80 = (dfq_filtered['libre'] > 80).sum()  # Quantidade de valores > 80
        #menor_igual_80 = (dfq_filtered['libre'] <= 80).sum()  # Quantidade de valores <= 80
        #labels = ['> 80', '≤ 80']
        #sizes = [maior_80, menor_igual_80]
        #fig1, ax1 = plt.subplots()
        #ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        #centre_circle = plt.Circle((0, 0), 0.70, fc='white')
        #fig1.gca().add_artist(centre_circle)

        # garantir que o gráfico seja desenhado em um formato circular
        #ax1.axis('equal')
        #plt.savefig('medicoes.png')
        #st.pyplot(fig1)  # Limpar a figura
        
    with col6:
        st.subheader("Libre")
        dfq_filtered = dfq.dropna(subset=['libre'])
        plt.barh(dfq_filtered['email'], dfq_filtered['libre'], color='teal')
        plt.xlabel('Valor do Libre')
        plt.ylabel('Emails')
        plt.savefig('libre.png')
        st.pyplot(plt)
        plt.clf()

    with col7:
        st.subheader("Diário Alimentar")
        # conta quantos tem de cada categoria
        diario_counts = dfq['food_journal'].value_counts().sort_index()
        plt.bar(diario_counts.index, diario_counts.values, color='turquoise')
        plt.xticks(ticks=[0, 1, 2, 3])
        plt.xlabel('Valor de Diário Alimentar')
        plt.ylabel('Quantidade de Participantes')
        plt.savefig('diario.png')
        st.pyplot(plt)