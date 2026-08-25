import json
import re

# 1. Altere a importação para usar STATUS_GDO_PERMITIDOS e as funções auxiliares do settings
from src.config.settings import (
    PROGRAMA_MAP,
    STATUS_GDO_PERMITIDOS,
    determinar_gdo_coluna,
    determinar_nome_produto_coluna,
)


def formatar_cpf_cic(cpf_raw) -> str:
    """Formata o CPF no padrão 9 dígitos + hífen + 2 dígitos (ex: 123456789-11)."""
    if not cpf_raw:
        return ""
    numeros = re.sub(r"\D", "", str(cpf_raw)).zfill(11)
    if len(numeros) == 11:
        return f"{numeros[:9]}-{numeros[9:]}"
    return str(cpf_raw).upper()


def formatar_telefone(tel_raw) -> str:
    """Formata o telefone no padrão (##)#####-#### ou (##)####-####."""
    if not tel_raw:
        return ""
    numeros = re.sub(r"\D", "", str(tel_raw))

    if len(numeros) > 11 and numeros.startswith("55"):
        numeros = numeros[2:]

    if len(numeros) == 11:
        return f"({numeros[:2]}){numeros[2:7]}-{numeros[7:]}"
    elif len(numeros) == 10:
        return f"({numeros[:2]}){numeros[2:6]}-{numeros[6:]}"

    return str(tel_raw)


def limpar_observacao(obs_raw) -> str:
    """Valida se a observação possui conteúdo útil e limpa mensagens automáticas/indesejadas."""
    if not obs_raw:
        return ""

    obs_str = str(obs_raw).strip()

    if obs_str.lower() in ["undefined", "null", "none"]:
        return ""

    # 1. Remove qualquer menção à corretora indesejada (incluindo o prefixo '>>', códigos e variações)
    obs_str = re.sub(
        r"(>>\s*)?CMHE2J\s*-\s*INRI CORRETORA DE SEGUROS E CONSORCIO LTDA",
        "",
        obs_str,
        flags=re.IGNORECASE,
    ).strip()

    # 2. Remove palavras reservadas do sistema
    texto_limpo = re.sub(r"\bundefined\b", "", obs_str, flags=re.IGNORECASE)
    texto_limpo = re.sub(
        r"(Número do pedido|Logradouro|Número|Bairro|Cidade|Complemento|Uf|Sexo|Observações):",
        "",
        texto_limpo,
        flags=re.IGNORECASE,
    )
    texto_limpo = re.sub(r"[.\s:-]", "", texto_limpo)

    # Se após a limpeza não sobrar nenhum conteúdo real, retorna vazio
    if not texto_limpo:
        return ""

    return obs_str.upper()


def extrair_e_formatar_itens(json_texto: str, nome_produto_selecionado: str):
    try:
        dados = json.loads(json_texto)
        itens = dados.get("itens", [])
    except Exception as e:
        raise ValueError(f"Formato JSON inválido: {e!s}")

    registros_validos = []
    ignorados_count = 0

    for item in itens:
        # Pega o tipo de filtro do GDO (pode vir como tipoFiltroGDO ou codigoTipoFiltro)
        tipo_filtro = str(
            item.get("tipoFiltroGDO") or item.get("codigoTipoFiltro") or ""
        )

        # Regra 1: Filtro de Status GDO (Permite 7 = Novas Oportunidades e 2 = Proposta)
        if tipo_filtro not in STATUS_GDO_PERMITIDOS:
            ignorados_count += 1
            continue

        # Regra 2: Filtro por Origem (Ignora apenas "Indicação Oportunidade" e aceita todo o resto)
        nome_origem = str(item.get("nomeOrigem", "")).strip()
        if nome_origem == "Indicação Oportunidade":
            ignorados_count += 1
            continue

        # Determina o produto dinamicamente conforme a regra (se for PROPOSTA/VÍNCULO pega do JSON, senão da tela)
        produto_final = determinar_nome_produto_coluna(item, nome_produto_selecionado)

        # Regra de Empresa e Susep baseada no produto selecionado na tela
        susep_or_prod = (
            str(item.get("susep", "")) + " " + nome_produto_selecionado
        ).upper()
        if "ICX" in susep_or_prod:
            empresa = "ICX"
        elif "INRI" in susep_or_prod:
            empresa = "INRI"
        else:
            empresa = item.get("empresa", "").upper()

        cod_programa = str(item.get("programa"))
        modalidade_raw = PROGRAMA_MAP.get(cod_programa, "OUTRO").upper()
        modalidade = modalidade_raw.replace("VÍNCULO", "VINCULO")

        data_raw = str(item.get("dataCriacao") or "")
        data_chegada = data_raw.split("T")[0] if "T" in data_raw else data_raw

        def upper_val(val):
            return str(val).upper() if val is not None else ""

        tel_obj = item.get("telefoneContato") or {}
        tel_bruto = (
            tel_obj.get("telefoneCelular") or tel_obj.get("telefoneResidencial") or ""
        )

        cep_bruto = str(item.get("contatoCep") or "")
        cep_limpo = re.sub(r"\D", "", cep_bruto)

        # Determina o valor da coluna GDO ("NOVAS OPORTUNIDADES" ou "PROPOSTA")
        gdo_valor = determinar_gdo_coluna(item)

        registro = {
            "Nº": "",
            "NOME ": upper_val(item.get("nomeCliente")),
            "TELEFONE": formatar_telefone(tel_bruto),
            "CPF": formatar_cpf_cic(item.get("cpfCnpjCliente")),
            "E-MAIL": upper_val(item.get("emailCliente")),
            "CHEGADA DO LEAD": data_chegada,
            "DATA RECOLHE": "",
            "RESPONSAVEL": "",
            "PRODUTO": produto_final,
            "EMPRESA": empresa,
            "MODALIDADE": modalidade,
            "DATA ENTREGA": "",
            "PROPENSAO": upper_val(item.get("propensao")),
            "MODELO": upper_val(item.get("modelo")),
            "ANO": upper_val(item.get("modeloAno")),
            "PLACA": upper_val(item.get("placa")),
            "CEP": cep_limpo,
            "UF": upper_val(item.get("contatoEstado")),
            "OBSERVAÇÕES": limpar_observacao(item.get("observacoes")),
            "GDO": gdo_valor,
            "idDynamics": str(item.get("idOportunidadeDynamics", "")),
        }

        registros_validos.append(registro)

    return registros_validos, ignorados_count
