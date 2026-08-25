import streamlit as st
from src.config.settings import PRODUTOS_CORRETORA
from src.controllers.converter_controller import processar_conversao_json
from src.services.formatacao_service import gerar_relatorio_formatacao

st.set_page_config(
    page_title="Conversor JSON - Porto Seguro -> Goalfy",
    page_icon="🔄",
    layout="centered",
)

# 1. Inicialização da Memória de Sessão
if "lote_jsons" not in st.session_state:
    st.session_state["lote_jsons"] = []

if "json_texto" not in st.session_state:
    st.session_state["json_texto"] = ""

if "resultado_ultimo_lote" not in st.session_state:
    st.session_state["resultado_ultimo_lote"] = None


# 2. Funções de Callback (Executadas antes do desenho da tela)
def cb_adicionar_e_proxima():
    texto = st.session_state["json_texto"].strip()
    if texto:
        st.session_state["lote_jsons"].append(texto)
        st.session_state["json_texto"] = ""  # Limpa o campo com segurança via callback


def cb_limpar_tudo():
    st.session_state["lote_jsons"] = []
    st.session_state["json_texto"] = ""
    st.session_state["resultado_ultimo_lote"] = None


def cb_salvar_lote(produto):
    # 1. Se houver algo digitado na caixa no momento de salvar, adiciona no lote
    texto = st.session_state["json_texto"].strip()
    if texto:
        st.session_state["lote_jsons"].append(texto)
        st.session_state["json_texto"] = ""

    if not st.session_state["lote_jsons"]:
        st.session_state["resultado_ultimo_lote"] = {
            "erro": "Nenhum JSON foi acumulado ainda. Cole um JSON antes de salvar."
        }
        return

    total_salvos = 0
    total_ignorados = 0
    todos_duplicados = []
    todos_registros_acumulados = []  # Lista para guardar os 40 registros
    caminho_dropbox = ""

    # 2. Processa cada JSON e acumula os registros na lista
    for json_str in st.session_state["lote_jsons"]:
        res = processar_conversao_json(json_str, produto)
        if res.get("sucesso"):
            total_salvos += res["salvos"]
            total_ignorados += res["ignorados_status"]
            todos_duplicados.extend(res["duplicados"])
            caminho_dropbox = res["caminho_arquivo"]

            # Junta os registros da página atual com a lista total
            if "registros_validos" in res:
                todos_registros_acumulados.extend(res["registros_validos"])

    # 3. Gera UMA ÚNICA planilha de formatação com todos os registros (40 clientes)
    caminho_formatacao = None
    if todos_registros_acumulados:
        caminho_formatacao = gerar_relatorio_formatacao(
            todos_registros_acumulados, produto
        )

    # 4. Guarda o resultado final para a interface
    st.session_state["resultado_ultimo_lote"] = {
        "total_salvos": total_salvos,
        "total_ignorados": total_ignorados,
        "duplicados": todos_duplicados,
        "caminho_dropbox": caminho_dropbox,
        "caminho_formatacao": caminho_formatacao,
    }

    # 5. Limpa a fila de JSONs
    st.session_state["lote_jsons"] = []


# 3. Interface Visual
st.title("⚡ EXTRAÇÃO DOS LEADS")
st.markdown(
    "Acumule as páginas colando o JSON e clicando em **Próxima Página**. Ao terminar, clique em **Salvar Lote na Matriz**."
)

produto_selecionado = st.selectbox("PRODUTO:", options=PRODUTOS_CORRETORA, index=0)

# Contador visual de páginas acumuladas
qtd_acumulada = len(st.session_state["lote_jsons"])
if qtd_acumulada > 0:
    st.info(
        f"📦 **{qtd_acumulada} página(s) de JSON** acumulada(s) na fila prontas para salvar."
    )

# Área de Texto
st.text_area(
    "Cole o JSON da página atual aqui:",
    height=200,
    placeholder='{"itens": [...]}',
    key="json_texto",
)

# 4. Botões de Ação
col1, col2, col3 = st.columns([2, 2, 1])

with col1:
    st.button(
        "➡️ Próxima Página (Acumular)",
        use_container_width=True,
        on_click=cb_adicionar_e_proxima,
    )

with col2:
    st.button(
        "🚀 Salvar Lote na Matriz",
        use_container_width=True,
        on_click=cb_salvar_lote,
        args=(produto_selecionado,),
    )

with col3:
    st.button("🗑️ Resetar", use_container_width=True, on_click=cb_limpar_tudo)

# 5. Exibição dos Resultados
res_lote = st.session_state["resultado_ultimo_lote"]
if res_lote:
    if "erro" in res_lote:
        st.error(res_lote["erro"])
    else:
        st.success(
            "✅ **Processamento concluído!** Total de"
            f" **{res_lote['total_salvos']}** registro(s) salvo(s)!"
        )

        if res_lote["caminho_dropbox"]:
            st.caption(f"📁 **Dropbox:** `{res_lote['caminho_dropbox']}`")

        # Exibição FORÇADA do caminho de Formatação
        if res_lote.get("caminho_formatacao"):
            st.success("🖥️ **Planilha de Formatação criada com sucesso no caminho:**")
            st.code(res_lote["caminho_formatacao"])
        else:
            st.error(
                "⚠️ A planilha de formatação não foi gerada pois nenhum"
                " registro válido foi retornado."
            )

        if res_lote["total_ignorados"] > 0:
            st.info(
                f"ℹ️ {res_lote['total_ignorados']} registro(s) ignorados"
                " (Status GDO diferente de 7)."
            )

        if res_lote["duplicados"]:
            st.warning(
                f"⚠️ {len(res_lote['duplicados'])} registro(s) duplicado(s) já existiam:"
            )
            for dup in res_lote["duplicados"]:
                st.write(f"- ID: `{dup['id']}` | Cliente: {dup['nome']}")
