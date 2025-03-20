import psycopg2
import pandas as pd

def conectar():
    try:
        conn = psycopg2.connect(
            host="192.168.1.3",
            database="healthstack",
            user="postgres",
            password="D1@l0g.d@t@.b@s3"
        )
        return conn
    except Exception as e:
        print("Erro ao conectar ao banco de dados:", e)
        return None

def consulta(query):
    conn = conectar()
    if conn is None:
        return None
    try:
        df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        print("Erro ao executar a consulta:", e)
        return None
    finally:
        conn.close()
        
date="2024-09-21"
saida = consulta(f"select * from project_1_research.bia bia")

print(saida)