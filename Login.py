import streamlit as st

# Configuração da página
st.set_page_config(page_title="Login - Sistema de Controle", layout="centered")

# Função para carregar usuários (inicialmente apenas admin)
@st.cache_data
def load_users():
    try:
        users = pd.read_csv("usuarios.csv")
    except FileNotFoundError:
        # Criar usuário admin inicial
        users = pd.DataFrame({"Usuario": ["admin"], "Senha": ["admin"]})
        users.to_csv("usuarios.csv", index=False)
    return users

# Função para validar login
def validate_login(username, password):
    users = load_users()
    user = users[users["Usuario"] == username]
    if not user.empty and user.iloc[0]["Senha"] == password:
        return True
    return False

# Tela de Login
st.markdown(
    """
    <style>
    .logo {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 20px;
    }
    .logo img {
        width: 150px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Exibir logo centralizado
st.markdown('<div class="logo"><img src="https://via.placeholder.com/150" alt="Logo"></div>', unsafe_allow_html=True)

# Campos de login
st.title("Login")
username = st.text_input("Usuário")
password = st.text_input("Senha", type="password")

# Botão de login
if st.button("Entrar"):
    if validate_login(username, password):
        st.session_state.logged_in = True
        st.session_state.username = username
        st.success(f"Bem-vindo, {username}!")
        st.experimental_rerun()
    else:
        st.error("Usuário ou senha inválidos.")