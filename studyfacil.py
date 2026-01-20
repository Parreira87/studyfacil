import streamlit as st
import pandas as pd
from supabase import create_client
import os

# 1. Configuração da Página
st.set_page_config(page_title="StudyFacil Pro", page_icon="🎓", layout="wide")

# CSS para os Cards Profissionais
st.markdown("""
    <style>
    .course-card {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 0.5rem solid #2E7D32;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# 2. Conexão com Supabase
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(URL, KEY)

# --- LISTA DE CATEGORIAS ORGANIZADA ---
categorias_estudo = [
    "--- 1. TECNOLOGIA E DADOS ---",
    "IA e Machine Learning", "Desenvolvimento de Software (Web/Mobile)", "Ciência de Dados", "Segurança da Informação", "Cloud Computing", "UX/UI Design",
    "--- 2. NEGÓCIOS E GESTÃO ---",
    "Administração e Gestão", "Marketing Digital e E-commerce", "Finanças e Contabilidade", "RH e Gestão de Pessoas", "Gestão de Projetos", "Logística e Supply Chain",
    "--- 3. SAÚDE E BEM-ESTAR ---",
    "Enfermagem", "Psicologia e Saúde Mental", "Educação Física", "Nutrição", "Gestão Hospitalar",
    "--- 4. EDUCAÇÃO E HUMANIDADES ---",
    "Pedagogia", "Idiomas", "Psicopedagogia", "História/Filosofia/Sociologia",
    "--- 5. ENGENHARIA E INFRAESTRUTURA ---",
    "Engenharia Civil e Arquitetura", "Automação e Mecatrônica", "Engenharia de Segurança", "BIM e Construção",
    "--- 6. CRIATIVIDADE E MÍDIA ---",
    "Design Gráfico", "Edição de Vídeo", "Artes e Moda",
    "--- 7. TÉCNICOS E PROFISSIONALIZANTES ---",
    "Técnico (Adm/Log/Eletro)", "Técnico (Enfermagem/Clínicas)", "Consultoria Regulatória",
    "--- 8. DESENVOLVIMENTO PESSOAL ---",
    "Liderança e Gestão de Tempo", "Comunicação e Oratória", "Inteligência Emocional",
    "--- 9. CURSOS DO GOVERNO E ACADÊMICOS ---",
    "Curso Preparatório", "Curso de Extensão", "Horas Complementares", "Cursos de Verão", "Outros"
]

# --- CABEÇALHO ---
col_logo, col_text = st.columns([1, 5])
if os.path.exists("logo.png"):
    with col_logo: st.image("logo.png", width=120)
    with col_text:
        st.title("StudyFacil")
        st.subheader("Sua Central de Estudos Profissional")
else:
    st.title("🎓 StudyFacil")

st.divider()

# --- BARRA LATERAL ---
st.sidebar.header("📝 Novo Cadastro")
with st.sidebar.form("form_cadastro", clear_on_submit=True):
    nome = st.text_input("Nome do Curso")
    url = st.text_input("Link (URL)")
    cat = st.selectbox("Selecione a Categoria", categorias_estudo)
    
    if st.form_submit_button("Salvar no Banco"):
        if nome and url and not cat.startswith("---"):
            if not url.startswith("http"): url = "https://" + url
            data = {"nome": nome, "url": url, "categoria": cat, "concluido": False}
            supabase.table("cursos").insert(data).execute()
            st.success("Curso adicionado!")
            st.rerun()
        elif cat.startswith("---"):
            st.error("Por favor, selecione uma categoria válida (não os títulos).")

# --- BUSCA E FILTROS ---
st.write("### 🔍 Seus Cursos")
col_busca, col_filtro = st.columns([2, 1])
busca = col_busca.text_input("Buscar por nome...", placeholder="Ex: Python, IA, Enfermagem...")
filtro_cat = col_filtro.selectbox("Filtrar Categoria", ["Todas"] + categorias_estudo)

# --- LISTAGEM ---
try:
    response = supabase.table("cursos").select("*").order("created_at", desc=True).execute()
    df = pd.DataFrame(response.data)
except Exception:
    df = pd.DataFrame()

if not df.empty:
    if busca: df = df[df['nome'].str.contains(busca, case=False)]
    if filtro_cat != "Todas": df = df[df['categoria'] == filtro_cat]

    for _, row in df.iterrows():
        st.markdown(f"""<div class="course-card">
            <h4 style="margin:0;">{'✅ ' if row['concluido'] else '📖 '} {row['nome']}</h4>
            <small><b>Área:</b> {row['categoria']}</small>
        </div>""", unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns([3, 1, 0.5])
        c1.link_button("🚀 Acessar Aula", row['url'], use_container_width=True)
        
        label_btn = "Refazer" if row['concluido'] else "Concluir"
        if c2.button(label_btn, key=f"btn_{row['id']}", use_container_width=True):
            supabase.table("cursos").update({"concluido": not row['concluido']}).eq("id", row['id']).execute()
            st.rerun()
            
        if c3.button("🗑️", key=f"del_{row['id']}"):
            supabase.table("cursos").delete().eq("id", row['id']).execute()
            st.rerun()
else:
    st.info("Nenhum curso encontrado com esses filtros.")