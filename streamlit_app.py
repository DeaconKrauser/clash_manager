# streamlit_app.py
import streamlit as st
import psycopg2
import pandas as pd
from dotenv import load_dotenv  # Importe dotenv, se você estiver usando .env
import os

# Carregue variáveis de ambiente do arquivo .env (se estiver usando)
load_dotenv()

# Configurações do Banco de Dados
DB_CONFIG = {
    "dbname": os.getenv("DB_NAME", "clash_db"),  # Valor padrão se não estiver no .env
    "user": os.getenv("DB_USER", "dkrauser"),
    "password": os.getenv("DB_PASSWORD", "Rinha@2025"), #Senha padrão
    "host": os.getenv("DB_HOST", "192.168.100.35"),
    "port": os.getenv("DB_PORT", "5432"),
}
# ... (resto do seu código) ...

def get_war_stats(war_id):
    """Busca os dados da guerra do banco de dados."""
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cur:
            # Jogadores que mais performaram (JOIN com a tabela players)
            cur.execute("""
                SELECT
                    p.name,  -- Seleciona o nome do jogador
                    SUM(wa.stars) AS total_stars,
                    AVG(wa.destruction) AS avg_destruction
                FROM war_off_mirror_attacks wa
                JOIN players p ON wa.player_tag = p.player_tag  -- JOIN com a tabela players
                WHERE wa.war_id = %s
                GROUP BY p.name  -- Agrupa pelo nome do jogador
                ORDER BY total_stars DESC, avg_destruction DESC
                LIMIT 10;
            """, (war_id,))
            top_performers = cur.fetchall()

            # Contagem de estrelas (não precisa de JOIN, pois já temos os dados)
            cur.execute("""
                SELECT stars, COUNT(*) AS count
                FROM war_off_mirror_attacks
                WHERE war_id = %s
                GROUP BY stars
                ORDER BY stars DESC;
            """, (war_id,))
            star_counts = cur.fetchall()

            # Jogadores que atacaram fora do espelho (sem estrelas) (JOIN)
            cur.execute("""
                SELECT DISTINCT p.name  -- Seleciona o nome do jogador
                FROM war_off_mirror_attacks wa
                JOIN players p ON wa.player_tag = p.player_tag  -- JOIN com a tabela players
                WHERE wa.war_id = %s AND wa.stars = 0 AND abs(wa.player_position - wa.defender_position) > 3;
            """, (war_id,))

            off_mirror_attackers = cur.fetchall()

            return top_performers, star_counts, off_mirror_attackers

    except Exception as e:
        print(f"Erro ao buscar dados: {e}")
        return [], [], []
    finally:
        conn.close()


def main():
#... (Restante do código streamlit)
    st.title("Estatísticas da Guerra - Clash of Clans")

    war_id = st.text_input("ID da Guerra:", "#2RLJVC200-20250224T195030.000Z")  # Substitua pelo valor padrão desejado

    if war_id:
        top_performers, star_counts, off_mirror_attackers = get_war_stats(war_id)

        if top_performers:
            st.subheader("Melhores Jogadores")
            df_performers = pd.DataFrame(top_performers, columns=["Jogador", "Estrelas", "Destruição Média"])
            st.bar_chart(df_performers.set_index("Jogador")[["Estrelas", "Destruição Média"]])


            st.subheader("Contagem de Estrelas")
            df_stars = pd.DataFrame(star_counts, columns=["Estrelas", "Contagem"])
            st.bar_chart(df_stars.set_index("Estrelas")["Contagem"])
            st.subheader("Contagem de Estrelas")
            st.bar_chart(df_stars.set_index('Estrelas'))

            st.subheader("Jogadores que Atacaram Fora do Espelho (Sem Estrelas)")
            if off_mirror_attackers:
                for player in off_mirror_attackers:
                    st.write(player[0])  # Exibe a tag do jogador
            else:
                st.write("Nenhum jogador atacou fora do espelho sem ganhar estrelas.")

        else:
            st.write("Nenhum dado encontrado para esta guerra.")
    else:
        st.write("Insira o ID da guerra para exibir as estatísticas.")
if __name__ == "__main__":
    main()