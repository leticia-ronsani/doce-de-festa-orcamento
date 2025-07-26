import streamlit as st
import pandas as pd
import os
from fpdf import FPDF
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="DOCE DE FESTA - ORÇAMENTO", layout="centered")
st.title("🎉 DOCE DE FESTA - LOCAÇÃO")

# Caminhos dos arquivos CSV
CLIENTES_CSV = "clientes.csv"
MATERIAIS_CSV = "materiais.csv"

# Funções para carregar e salvar dados
def carregar_dados(caminho):
    if os.path.exists(caminho):
        return pd.read_csv(caminho)
    return pd.DataFrame()

def salvar_dados(df, caminho):
    df.to_csv(caminho, index=False)

# Menu lateral
menu = st.sidebar.radio("📂 Menu", ["Cadastrar Cliente", "Cadastrar Material", "Gerar Orçamento"])

# Aba 1 - Cadastro de Cliente
if menu == "Cadastrar Cliente":
    st.subheader("📋 Cadastro de Cliente")
    nome = st.text_input("Nome completo")
    telefone = st.text_input("Telefone")
    email = st.text_input("E-mail")

    if st.button("Salvar Cliente"):
        if nome and telefone:
            df = carregar_dados(CLIENTES_CSV)
            novo = pd.DataFrame([[nome, telefone, email]], columns=["nome", "telefone", "email"])
            df = pd.concat([df, novo], ignore_index=True)
            salvar_dados(df, CLIENTES_CSV)
            st.success("Cliente cadastrado com sucesso!")
        else:
            st.warning("Por favor, preencha pelo menos nome e telefone.")

# Aba 2 - Cadastro de Material
elif menu == "Cadastrar Material":
    st.subheader("📦 Cadastro de Materiais para Locação")
    categoria = st.selectbox("Categoria", ["Louça", "Toalha", "Guardanapo", "Sousplat"])
    nome_item = st.text_input("Nome do item")
    quantidade = st.number_input("Quantidade disponível", min_value=1, step=1)
    preco = st.number_input("Preço unitário (R$)", min_value=0.0, step=0.5)

    if st.button("Salvar Material"):
        if nome_item:
            df = carregar_dados(MATERIAIS_CSV)
            novo = pd.DataFrame([[categoria, nome_item, quantidade, preco]],
                                columns=["categoria", "nome", "quantidade", "preco"])
            df = pd.concat([df, novo], ignore_index=True)
            salvar_dados(df, MATERIAIS_CSV)
            st.success("Material cadastrado com sucesso!")
        else:
            st.warning("Preencha o nome do item.")

# Aba 3 - Gerar Orçamento e PDF
elif menu == "Gerar Orçamento":
    st.subheader("🧾 Gerar Orçamento")

    df_clientes = carregar_dados(CLIENTES_CSV)
    df_materiais = carregar_dados(MATERIAIS_CSV)

    if df_clientes.empty or df_materiais.empty:
        st.warning("Cadastre pelo menos um cliente e um material para gerar orçamento.")
    else:
        cliente_selecionado = st.selectbox("Selecionar Cliente", df_clientes["nome"])
        cliente_info = df_clientes[df_clientes["nome"] == cliente_selecionado].iloc[0]

        itens_selecionados = st.multiselect("Selecionar Materiais", df_materiais["nome"])

        if len(itens_selecionados) == 0:
            st.info("Selecione pelo menos um material para orçar.")
        else:
            # Montar tabela dos itens com quantidade para o orçamento
            st.write("Informe a quantidade para cada item:")
            itens_orcamento = []
            total = 0

            for item in itens_selecionados:
                row = df_materiais[df_materiais["nome"] == item].iloc[0]
                max_qtd = int(row["quantidade"])
                qtd = st.number_input(f"Quantidade para '{item}' (máx {max_qtd})", min_value=1, max_value=max_qtd, step=1, key=item)
                subtotal = qtd * row["preco"]
                total += subtotal
                itens_orcamento.append([row["categoria"], row["nome"], qtd, row["preco"], subtotal])

            st.markdown(f"### Total: R$ {total:.2f}")
            st.markdown(f"### Entrada para reserva (30%): R$ {total*0.3:.2f}")

            if st.button("Gerar PDF do Orçamento"):
                data_hoje = datetime.now().strftime("%d/%m/%Y")
                pdf = FPDF()
                pdf.add_page()

                # Logo - se tiver arquivo logo.png na pasta, mostra (opcional)
                if os.path.exists("logo.png"):
                    pdf.image("logo.png", x=10, y=8, w=33)

                pdf.set_font("Arial", "B", 14)
                pdf.cell(0, 10, "DOCE DE FESTA - ORÇAMENTO DE LOCAÇÃO", ln=True, align="C")
                pdf.set_font("Arial", "", 12)
                pdf.cell(0, 10, f"Data: {data_hoje}", ln=True)
                pdf.ln(5)

                pdf.cell(0, 10, f"Cliente: {cliente_info['nome']}", ln=True)
                pdf.cell(0, 10, f"Telefone: {cliente_info['telefone']} | Email: {cliente_info['email']}", ln=True)
                pdf.ln(5)

                pdf.set_font("Arial", "B", 12)
                pdf.cell(0, 10, "Itens Selecionados:", ln=True)
                pdf.set_font("Arial", "", 11)

                for cat, nome, qtd, preco, subtotal in itens_orcamento:
                    pdf.cell(0, 10, f"{cat} - {nome} | Qtd: {qtd} | R$: {preco:.2f} | Subtotal: R$ {subtotal:.2f}", ln=True)

                pdf.ln(5)
                pdf.set_font("Arial", "B", 12)
                pdf.cell(0, 10, f"Total: R$ {total:.2f}", ln=True)
                pdf.cell(0, 10, f"Entrada (30%): R$ {total * 0.3:.2f}", ln=True)

                pdf.ln(10)
                pdf.set_font("Arial", "", 11)
                pdf.multi_cell(0, 10,
                               "📞 Contato: (48) 99846-6161\n"
                               "🕗 Atendimento: Segunda a Sexta, das 8h às 17h (sem fechar ao meio-dia)\n"
                               "💳 PIX: 09.266.448.0001/26")

                nome_arquivo = f"orcamento_{cliente_info['nome'].replace(' ', '_')}.pdf"
                pdf.output(nome_arquivo)

                with open(nome_arquivo, "rb") as file:
                    st.download_button("📥 Baixar Orçamento em PDF", file, file_name=nome_arquivo)
