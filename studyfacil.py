import streamlit as st
import pandas as pd
from supabase import create_client
import os

# 1. Configuração da Página
st.set_page_config(
    page_title="StudyFacil Pro", 
    page_icon="🎓", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS de Limpeza Total e Responsividade
st.markdown("""
    <style>
    /* Esconde menus e ícones técnicos do Streamlit Cloud */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stAppDeployButton {display:none !important;}
    [data-testid="stStatusWidget"] {display:none !important;}
    div[data-testid="stDecoration"] {display:none !important;}
    
    /* Estilo dos Cards */
    .course-card {
        background-color: #ffffff;
        padding: 1.2rem;
        border-radius: 0.5rem;
        border-left: 0.5rem solid #2E7D32;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }
    
    /* Ajuste Mobile */
    @media (max-width: 640px) {
        .stButton>button { width: 100% !important; height: 45px; margin-bottom: 8px; }
    }
    </style>
""", unsafe_allow_html=True)

# 2. Conexão com Supabase
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(URL, KEY)

# --- CATEGORIAS ---
categorias_estudo = [
    "IA e Machine Learning", "Desenvolvimento de Software", "Ciência de Dados", 
    "Segurança da Informação", "Cloud Computing", "UX/UI Design", "Administração e Gestão", 
    "Marketing Digital", "Finanças e Contabilidade", "Logística", "Enfermagem", 
    "Psicologia", "Educação Física", "Nutrição", "Pedagogia", "Idiomas", 
    "Engenharia e Arquitetura", "Design Gráfico", "Edição de Vídeo", 
    "Curso Preparatório", "Curso Técnico", "Horas Complementares", "Outros"
]

# Inicializa a sessão do usuário se não existir
if 'user' not in st.session_state:
    st.session_state.user = None

# --- LÓGICA DE TELAS ---

# SE NÃO ESTIVER LOGADO -> MOSTRA LOGIN
if st.session_state.user is None:
    col_l = st.columns([0.1, 0.8, 0.1])[1]
    with col_l:
        st.title("🎓 StudyFacil")
        tab1, tab2 = st.tabs(["Entrar", "Criar Conta"])
        
        with tab1:
            with st.form("login"):
                email = st.text_input("E-mail")
                senha = st.text_input("Senha", type="password")
                if st.form_submit_button("Acessar"):
                    try:
                        res = supabase.auth.sign_in_with_password({"email": email, "password": senha})
                        if res.user:
                            st.session_state.user = res.user
                            st.rerun()
                    except Exception as e:
                        st.error(f"Erro: {e}")
        
        with tab2:
            with st.form("cadastro"):
                new_email = st.text_input("E-mail para cadastro")
                new_senha = st.text_input("Senha (mín. 6 dígitos)", type="password")
                if st.form_submit_button("Cadastrar"):
                    try:
                        supabase.auth.sign_up({"email": new_email, "password": new_senha})
                        st.success("Conta criada! Tente fazer o login.")
                    except Exception as e:
                        st.error(f"Erro: {e}")

# SE ESTIVER LOGADO -> MOSTRA O APP
else:
    user_id = st.session_state.user.id
    
    # Barra Lateral com botão de Sair (Para a tela de login voltar a aparecer)
    st.sidebar.markdown(f"👤 **{st.session_state.user.email}**")
    if st.sidebar.button("🔴 Sair da Conta", use_container_width=True):
        supabase.auth.sign_out()
        st.session_state.user = None
        st.rerun() # Isso faz a tela de login reaparecer
    
    st.sidebar.divider()
    st.sidebar.header("📝 Novo Curso")
    with st.sidebar.form("add_curso", clear_on_submit=True):
        nome = st.text_input("Nome")
        url = st.text_input("Link URL")
        cat = st.selectbox("Área", categorias_estudo)
        if st.form_submit_button("Salvar"):
            if nome and url:
                if not url.startswith("http"): url = "https://" + url
                # Salva vinculado ao seu ID único
                data = {"nome": nome, "url": url, "categoria": cat, "user_id": user_id, "concluido": False}
                supabase.table("cursos").insert(data).execute()
                st.rerun()

    # Conteúdo Principal
    st.title("Meus Estudos")
    c_busca, c_filtro = st.columns([1, 1])
    busca = c_busca.text_input("🔍 Buscar", placeholder="Nome...")
    filtro_cat = c_filtro.selectbox("Área", ["Todas"] + categorias_estudo)

    # Listagem Protegida
    try:
        response = supabase.table("cursos").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
        df = pd.DataFrame(response.data)
    except:
        df = pd.DataFrame()

    if not df.empty:
        if busca: df = df[df['nome'].str.contains(busca, case=False)]
        if filtro_cat != "Todas": df = df[df['categoria'] == filtro_cat]

        for _, row in df.iterrows():
            st.markdown(f"""<div class="course-card">
                <h4 style="margin:0;">{'✅ ' if row['concluido'] else '📖 '} {row['nome']}</h4>
                <p style="font-size: 0.8rem; color: gray;">{row['categoria']}</p>
            </div>""", unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns([2, 1, 0.5])
            c1.link_button("🚀 Abrir", row['url'], use_container_width=True)
            
            label_btn = "Refazer" if row['concluido'] else "Concluir"
            if c2.button(label_btn, key=f"ch_{row['id']}", use_container_width=True):
                supabase.table("cursos").update({"concluido": not row['concluido']}).eq("id", row['id']).execute()
                st.rerun()
                
            if c3.button("🗑️", key=f"del_{row['id']}", use_container_width=True):
                supabase.table("cursos").delete().eq("id", row['id']).execute()
                st.rerun()
    else:
        st.info("Nenhum curso cadastrado ainda.")