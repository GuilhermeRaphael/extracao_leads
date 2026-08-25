import re
import unicodedata

# Mapeamento estático para nomes que não dependem do produto da tela
MAPA_PRODUTOS_DIRETOS = {
    "PORTO SEGURO CELULAR": "CELULAR",
    "RISCOS DIVERSOS": "BIKE",
    "PORTO AUTOMÓVEL": "AUTOMOVEL",
    "ODONTOLÓGICO": "ODONTO",
    "PORTO PET": "PET LOVE",
    "SEGURO SMART E GAMES": "PORTATEIS",
    "SEGURO FOTO E VÍDEO": "PORTATEIS",
    "SEGURO NOTEBOOK E TABLET": "PORTATEIS",
    "EQUIPAMENTOS PORTÁTEIS": "PORTATEIS",
    "RESIDENCIAL ESSENCIAL": "RESIDENCIAL",
    "RESIDÊNCIA PREMIUM": "RESIDENCIAL",
    "SAÚDE": "SAUDE",
    "CONSÓRCIO IMÓVEL": "CONSORCIO",
    "CONSÓRCIO": "CONSORCIO",
    "SEGURO VIAGEM INTERNACIONAL": "VIAGEM",
    "SEGURO VIAGEM NACIONAL": "VIAGEM",
    "VIDA INDIVIDUAL": "VIDA",
    "VIDA PRESENTE": "VIDA",
    "VIDA ON": "VIDA",
    "VIDA EMPRESARIAL": "VIDA",
}


def remover_acentos(texto: str) -> str:
    """Remove acentos do texto mantendo as letras maiúsculas."""
    return "".join(
        c
        for c in unicodedata.normalize("NFD", texto)
        if unicodedata.category(c) != "Mn"
    )


def tratar_nome_produto_vinculo(nome_json: str, produto_selecionado: str) -> str:
    """Trata o nome do produto de VÍNCULO.

    Se vier 'PORTO AUTOMOVEL', usa o produto da tela para definir entre AUTOMOVEL, MOTO ou AUTO BONIF.
    """
    if not nome_json:
        return produto_selecionado.split("-")[0].strip().upper()

    nome_bruto = str(nome_json).strip().upper()
    prod_tela_limpo = produto_selecionado.split("-")[0].strip().upper()
    nome_sem_acento = remover_acentos(nome_bruto)

    # 1. Regra de desempate para PORTO AUTOMOVEL / PORTO AUTOMÓVEL
    if "AUTOMOVEL" in nome_sem_acento or "AUTO" in nome_sem_acento:
        if "MOTO" in prod_tela_limpo:
            return "MOTO"
        elif "BONIF" in prod_tela_limpo:
            return "AUTO BONIF"
        else:
            return "AUTOMOVEL"

    # 2. Busca direta no dicionário de produtos fixos
    if nome_bruto in MAPA_PRODUTOS_DIRETOS:
        return MAPA_PRODUTOS_DIRETOS[nome_bruto]

    if nome_sem_acento in MAPA_PRODUTOS_DIRETOS:
        return MAPA_PRODUTOS_DIRETOS[nome_sem_acento]

    # 3. Tratamento genérico caso venha um produto novo
    nome_limpo = re.sub(r"\bPORTO(\s+SEGURO)?\b", "", nome_bruto).strip()
    nome_limpo = re.split(r"[-_]", nome_limpo)[0].strip()

    return nome_limpo if nome_limpo else prod_tela_limpo
