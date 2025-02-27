import streamlit as st
import pandas as pd
import requests

# Configuração da página
st.set_page_config(page_title="Controle de Vendas e Estoque", layout="wide")

# Configurações do GitHub
GITHUB_TOKEN = "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"  # Substitua pelo seu token do GitHub
REPO_OWNER = "Degan906"
REPO_NAME = "Estoque"
BRANCH = "main"

# Função para baixar arquivo CSV do GitHub
def download_csv(file_name):
    url = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/{BRANCH}/{file_name}"
    response = requests.get(url)
    if response.status_code == 200:
        return pd.read_csv(pd.compat.StringIO(response.text))
    else:
        return pd.DataFrame()

# Função para atualizar arquivo CSV no GitHub
def update_csv(file_name, df):
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{file_name}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    # Obter o SHA do arquivo existente
    response = requests.get(url, headers=headers)
    sha = response.json().get("sha")
    # Atualizar o conteúdo do arquivo
    content = df.to_csv(index=False)
    data = {
        "message": f"Atualizar {file_name}",
        "content": content.encode("utf-8").decode("latin1"),
        "sha": sha,
        "branch": BRANCH
    }
    response = requests.put(url, headers=headers, json=data)
    if response.status_code == 200:
        st.success(f"{file_name} atualizado com sucesso!")
    else:
        st.error(f"Erro ao atualizar {file_name}: {response.text}")

# Carregar dados dos usuários
users = download_csv("usuarios.csv")
if users.empty:
    users = pd.DataFrame({"Usuario": ["admin"], "Senha": ["12345admin"]})
    update_csv("usuarios.csv", users)

# Verificar se o usuário está logado
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None

# Função para validar login
def validate_login(username, password):
    user = users[users["Usuario"] == username]
    if not user.empty and user.iloc[0]["Senha"] == password:
        return True
    return False

# Página de Login
if not st.session_state.logged_in:
    st.title("Login")
    username = st.text_input("Usuário")
    password = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if validate_login(username, password):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"Bem-vindo, {username}!")
            st.experimental_rerun()
        else:
            st.error("Usuário ou senha inválidos.")
else:
    # Se o usuário estiver logado, exibir o sistema
    st.sidebar.write(f"Logado como: {st.session_state.username}")
    if st.sidebar.button("Sair"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.experimental_rerun()

    # Menu principal
    menu = ["Cadastro de Produtos", "Registro de Vendas", "Visualizar Estoque", "Relatório de Vendas", "Gerenciar Usuários"]
    choice = st.sidebar.selectbox("Menu", menu)

    # Carregar dados do estoque
    stock = download_csv("estoque.csv")
    if stock.empty:
        stock = pd.DataFrame(columns=["Produto", "Preço", "Quantidade"])

    # Carregar dados das vendas
    sales = download_csv("vendas.csv")
    if sales.empty:
        sales = pd.DataFrame(columns=["Produto", "Quantidade", "Total"])

    # Funcionalidade: Cadastro de Produtos
    if choice == "Cadastro de Produtos":
        st.header("Cadastro de Produtos")
        with st.form("Cadastro"):
            nome = st.text_input("Nome do Produto")
            preco = st.number_input("Preço do Produto", min_value=0.0, format="%.2f")
            quantidade = st.number_input("Quantidade em Estoque", min_value=0)
            submitted = st.form_submit_button("Cadastrar")
            if submitted:
                new_product = pd.DataFrame({"Produto": [nome], "Preço": [preco], "Quantidade": [quantidade]})
                stock = pd.concat([stock, new_product], ignore_index=True)
                update_csv("estoque.csv", stock)
                st.success(f"Produto '{nome}' cadastrado com sucesso!")
        st.subheader("Estoque Atual")
        st.dataframe(stock)

    # Funcionalidade: Registro de Vendas
    elif choice == "Registro de Vendas":
        st.header("Registro de Vendas")
        if not stock.empty:
            produto = st.selectbox("Selecione o Produto", stock["Produto"].unique())
            quantidade = st.number_input("Quantidade Vendida", min_value=1)
            if st.button("Registrar Venda"):
                produto_info = stock[stock["Produto"] == produto]
                preco = produto_info["Preço"].values[0]
                estoque_atual = produto_info["Quantidade"].values[0]
                if quantidade <= estoque_atual:
                    total = quantidade * preco
                    new_sale = pd.DataFrame({"Produto": [produto], "Quantidade": [quantidade], "Total": [total]})
                    sales = pd.concat([sales, new_sale], ignore_index=True)
                    update_csv("vendas.csv", sales)
                    # Atualizar estoque
                    stock.loc[stock["Produto"] == produto, "Quantidade"] -= quantidade
                    update_csv("estoque.csv", stock)
                    st.success(f"Venda registrada! Total: R${total:.2f}")
                else:
                    st.error("Quantidade insuficiente em estoque.")
        else:
            st.warning("Nenhum produto cadastrado.")

    # Funcionalidade: Visualizar Estoque
    elif choice == "Visualizar Estoque":
        st.header("Estoque Atual")
        st.dataframe(stock)

    # Funcionalidade: Relatório de Vendas
    elif choice == "Relatório de Vendas":
        st.header("Relatório de Vendas")
        if not sales.empty:
            st.dataframe(sales)
            total_vendas = sales["Total"].sum()
            st.info(f"Total de Vendas: R${total_vendas:.2f}")
        else:
            st.warning("Nenhuma venda registrada.")

    # Funcionalidade: Gerenciar Usuários (apenas admin pode acessar)
    elif choice == "Gerenciar Usuários":
        if st.session_state.username == "admin":
            st.header("Gerenciar Usuários")
            # Exibir lista de usuários
            st.subheader("Lista de Usuários")
            st.dataframe(users)
            # Formulário para adicionar novo usuário
            with st.form("Novo Usuário"):
                new_username = st.text_input("Novo Usuário")
                new_password = st.text_input("Nova Senha", type="password")
                submitted = st.form_submit_button("Adicionar")
                if submitted:
                    if new_username in users["Usuario"].values:
                        st.error("Usuário já existe.")
                    else:
                        new_user = pd.DataFrame({"Usuario": [new_username], "Senha": [new_password]})
                        users = pd.concat([users, new_user], ignore_index=True)
                        update_csv("usuarios.csv", users)
                        st.success(f"Usuário '{new_username}' adicionado com sucesso!")
        else:
            st.error("Apenas o administrador pode gerenciar usuários.")
