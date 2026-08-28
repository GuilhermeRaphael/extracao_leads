from src.config.settings import obter_caminho_matriz
from src.services.excel_service import salvar_registros_na_matriz
from src.utils.formatters import extrair_e_formatar_itens


def processar_conversao_json(json_texto: str, produto_selecionado: str) -> dict:
    """Orquestra o processo de conversão e salvamento na matriz."""
    caminho_excel = obter_caminho_matriz(produto_selecionado)

    registros, ignorados_status = extrair_e_formatar_itens(
        json_texto, produto_selecionado
    )

    if not registros and ignorados_status == 0:
        return {
            "sucesso": False,
            "mensagem": "Nenhum registro encontrado no JSON informado.",
            "salvos": 0,
            "duplicados": [],
            "caminho_arquivo": str(caminho_excel),
            "ignorados_status": 0,
            "registros_validos": [],
        }

    # 1. Salva na planilha matriz do Dropbox
    salvos_count, duplicados = salvar_registros_na_matriz(
        caminho_excel, registros, produto_selecionado
    )

    # 2. Retorna os dados processados para acúmulo no app.py
    return {
        "sucesso": True,
        "caminho_arquivo": str(caminho_excel),
        "salvos": salvos_count,
        "duplicados": duplicados,
        "ignorados_status": ignorados_status,
        "registros_validos": registros,
    }
