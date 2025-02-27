import streamlit as st
import pandas as pd

# Configuração da página
st.set_page_config(page_title="Controle de Vendas e Estoque", layout="wide")

# Funções para carregar e salvar dados dos usuários
@st.cache_data
def load_users():
    try:
        users = pd.read_csv("usuarios.csv")
    except FileNotFoundError:
        # Criar usuário admin inicial
        users = pd.DataFrame({"Usuario": ["admin"], "Senha": ["12345admin"]})
        users.to_csv("usuarios.csv", index=False)
    return users

def save_users(users):
    users.to_csv("usuarios.csv", index=False)

# Carregar dados dos usuários
users = load_users()

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
            st.rerun()
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
    @st.cache_data
    def load_stock():
        try:
            stock = pd.read_csv("estoque.csv")
        except FileNotFoundError:
            stock = pd.DataFrame(columns=["Produto", "Preço", "Quantidade"])
        return stock

    def save_stock(stock):
        stock.to_csv("estoque.csv", index=False)

    # Carregar dados das vendas
    @st.cache_data
    def load_sales():
        try:
            sales = pd.read_csv("vendas.csv")
        except FileNotFoundError:
            sales = pd.DataFrame(columns=["Produto", "Quantidade", "Total"])
        return sales

    def save_sales(sales):
        sales.to_csv("vendas.csv", index=False)

    # Funcionalidade: Cadastro de Produtos
    if choice == "Cadastro de Produtos":
        st.header("Cadastro de Produtos")
        stock = load_stock()

        with st.form("Cadastro"):
            nome = st.text_input("Nome do Produto")
            preco = st.number_input("Preço do Produto", min_value=0.0, format="%.2f")
            quantidade = st.number_input("Quantidade em Estoque", min_value=0)
            submitted = st.form_submit_button("Cadastrar")

            if submitted:
                new_product = pd.DataFrame({"Produto": [nome], "Preço": [preco], "Quantidade": [quantidade]})
                
                if stock.empty:
                    # Inicializa o estoque com o novo produto
                    stock = new_product
                else:
                    # Concatena o novo produto ao estoque existente
                    stock = pd.concat([stock, new_product], ignore_index=True)
                
                save_stock(stock)
                st.success(f"Produto '{nome}' cadastrado com sucesso!")

        st.subheader("Estoque Atual")
        st.dataframe(stock)

    # Funcionalidade: Registro de Vendas
    elif choice == "Registro de Vendas":
        st.header("Registro de Vendas")
        stock = load_stock()
        sales = load_sales()

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
                    
                    if sales.empty:
                        sales = new_sale
                    else:
                        sales = pd.concat([sales, new_sale], ignore_index=True)
                    
                    save_sales(sales)

                    # Atualizar estoque
                    stock.loc[stock["Produto"] == produto, "Quantidade"] -= quantidade
                    save_stock(stock)
                    st.success(f"Venda registrada! Total: R${total:.2f}")
                else:
                    st.error("Quantidade insuficiente em estoque.")
        else:
            st.warning("Nenhum produto cadastrado.")

    # Funcionalidade: Visualizar Estoque
    elif choice == "Visualizar Estoque":
        st.header("Estoque Atual")
        stock = load_stock()
        st.dataframe(stock)

    # Funcionalidade: Relatório de Vendas
    elif choice == "Relatório de Vendas":
        st.header("Relatório de Vendas")
        sales = load_sales()
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
            users = load_users()

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
                        
                        if users.empty:
                            users = new_user
                        else:
                            users = pd.concat([users, new_user], ignore_index=True)
                        
                        save_users(users)
                        st.success(f"Usuário '{new_username}' adicionado com sucesso!")
        else:
            st.error("Apenas o administrador pode gerenciar usuários.")
