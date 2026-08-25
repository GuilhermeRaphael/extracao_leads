from datetime import datetime
from pathlib import Path

from src.utils.tratamento_vinculo import tratar_nome_produto_vinculo


def obter_caminho_dropbox() -> Path:
    """Retorna o caminho do Dropbox local ou uma pasta temporaria na nuvem."""
    # Lista de caminhos locais comuns do Windows
    caminhos_locais = [
        Path.home() / "Dropbox",
        Path(
            "C:/Users/Inri Corretora 18/Dropbox"
        ),  # Ajuste com seu caminho exato se necessario
    ]

    # 1. Tenta encontrar a pasta local se estiver rodando no seu computador
    for caminho in caminhos_locais:
        if caminho.exists():
            return caminho

    # 2. Se estiver rodando no Streamlit Cloud (nuvem), cria uma pasta temporaria de saida
    caminho_nuvem = Path("/tmp/goalfy_exports")
    caminho_nuvem.mkdir(parents=True, exist_ok=True)
    return caminho_nuvem


# 1. Pasta Raiz do Dropbox detectada dinamicamente no PC do usuário
DROPBOX_DIR = obter_caminho_dropbox()

# 2. Mapeamento de Produtos, Tipo (INRI/ICX) e suas respetivas SUSEPs
PRODUTOS_CONFIG = {
    "AUTOMOVEL - INRI": {
        "tipo": "INRI",
        "susep": "CMHE2J",
        "subpasta": r"GOALFY\INRI\INRI - AUTO",
    },
    "BIKE - INRI": {
        "tipo": "INRI",
        "susep": "CMHE2J",
        "subpasta": r"GOALFY\INRI\INRI - BIKE",
    },
    "CELULAR - INRI": {
        "tipo": "INRI",
        "susep": "CMHE2J",
        "subpasta": r"GOALFY\INRI\INRI - CELULAR",
    },
    "MOTO - INRI": {
        "tipo": "INRI",
        "susep": "CMHE2J",
        "subpasta": r"GOALFY\INRI\INRI - MOTO",
    },
    "ODONTO - INRI": {
        "tipo": "INRI",
        "susep": "CMHE2J",
        "subpasta": r"GOALFY\INRI\INRI - ODONTO",
    },
    "PET - INRI": {
        "tipo": "INRI",
        "susep": "CMHE2J",
        "subpasta": r"GOALFY\INRI\INRI - PET",
    },
    "PORTATEIS - INRI": {
        "tipo": "INRI",
        "susep": "CMHE2J",
        "subpasta": r"GOALFY\INRI\INRI - PORTATEIS",
    },
    "RESID - INRI": {
        "tipo": "INRI",
        "susep": "CMHE2J",
        "subpasta": r"GOALFY\INRI\INRI - RESID",
    },
    "SAUDE - INRI": {
        "tipo": "INRI",
        "susep": "CMHE2J",
        "subpasta": r"GOALFY\INRI\INRI - SAUDE",
    },
    "VIAGEM - INRI": {
        "tipo": "INRI",
        "susep": "CMHE2J",
        "subpasta": r"GOALFY\INRI\INRI - VIAGEM",
    },
    "VIDA - INRI": {
        "tipo": "INRI",
        "susep": "CMHE2J",
        "subpasta": r"GOALFY\INRI\INRI - VIDA",
    },
    "VINCULO - INRI": {
        "tipo": "INRI",
        "susep": "CMHE2J",
        "subpasta": r"GOALFY\INRI\INRI - VINCULO",
    },
    "AUTO BONIF - ICX": {
        "tipo": "ICX",
        "susep": "CMN32J",
        "subpasta": r"GOALFY\ICX\AUTO ICX BONIF",
    },
    "AUTOMOVEL - ICX": {
        "tipo": "ICX",
        "susep": "CMN32J",
        "subpasta": r"GOALFY\ICX\ICX - AUTO",
    },
    "CELULAR - ICX": {
        "tipo": "ICX",
        "susep": "CMN32J",
        "subpasta": r"GOALFY\ICX\ICX - CELULAR",
    },
    "MOTO - ICX": {
        "tipo": "ICX",
        "susep": "CMN32J",
        "subpasta": r"GOALFY\ICX\ICX - MOTO",
    },
    "RESID - ICX": {
        "tipo": "ICX",
        "susep": "CMN32J",
        "subpasta": r"GOALFY\ICX\ICX - RESID",
    },
    "VIAGEM - ICX": {
        "tipo": "ICX",
        "susep": "CMN32J",
        "subpasta": r"GOALFY\ICX\ICX - VIAGEM",
    },
}

PRODUTOS_CORRETORA = list(PRODUTOS_CONFIG.keys())

# 3. Regras da Porto Seguro
PROGRAMA_MAP = {"390260000": "LEAD", "390260001": "VÍNCULO"}

# Mapeamento do valor do GDO segundo o tipoFiltroGDO
GDO_VALORES_MAP = {
    "7": "NOVAS OPORTUNIDADES",
    "2": "PROPOSTA",
}

# Tipos permitidos para conversão/salvamento (7 = Novas Oportunidades, 2 = Proposta)
STATUS_GDO_PERMITIDOS = ["7", "2"]


def obter_caminho_matriz(produto_selecionado: str) -> Path:
    """Gera o caminho dinâmico da planilha matriz baseado no produto selecionado."""
    config_prod = PRODUTOS_CONFIG.get(produto_selecionado)
    if not config_prod:
        raise ValueError(f"Produto '{produto_selecionado}' não configurado.")

    subpasta_limpa = config_prod["subpasta"].lstrip(r"\/")
    pasta_destino = DROPBOX_DIR / Path(subpasta_limpa)
    pasta_destino.mkdir(parents=True, exist_ok=True)

    ano_atual = datetime.now().year
    prod_limpo = produto_selecionado.split("-")[0].strip().upper()

    nome_arquivo = f"MATRIZ {prod_limpo} {ano_atual}.xlsx"

    return pasta_destino / nome_arquivo


def determinar_nome_produto_coluna(lead_json: dict, produto_selecionado: str) -> str:
    cod_programa = str(
        lead_json.get("programa") or lead_json.get("codigo_programa") or ""
    ).strip()

    # Se for VÍNCULO (390260001)
    if cod_programa == "390260001":
        produto_do_json = lead_json.get("nomeProduto")
        return tratar_nome_produto_vinculo(produto_do_json, produto_selecionado)

    # Se for LEAD normal
    return produto_selecionado.split("-")[0].strip().upper()


def determinar_gdo_coluna(lead_json: dict) -> str:
    """Define o valor da coluna GDO na planilha com base no filtro:
    - Se tipoFiltroGDO for '7' -> 'NOVAS OPORTUNIDADES'
    - Se tipoFiltroGDO for '2' -> 'PROPOSTA'
    """
    tipo_filtro = str(
        lead_json.get("tipoFiltroGDO") or lead_json.get("codigoTipoFiltro") or ""
    )

    return GDO_VALORES_MAP.get(tipo_filtro, "")
