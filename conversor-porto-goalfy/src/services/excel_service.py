from pathlib import Path

import openpyxl
import pandas as pd
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.worksheet.table import Table, TableStyleInfo

COLUNAS_MATRIZ = [
    "Nº",
    "NOME ",
    "TELEFONE",
    "CPF",
    "E-MAIL",
    "CHEGADA DO LEAD",
    "DATA RECOLHE",
    "RESPONSAVEL",
    "PRODUTO",
    "EMPRESA",
    "MODALIDADE",
    "DATA ENTREGA",
    "PROPENSAO",
    "MODELO",
    "ANO",
    "PLACA",
    "CEP",
    "UF",
    "OBSERVAÇÕES",
    "GDO",
    "idDynamics",
]


def salvar_registros_na_matriz(
    caminho_arquivo: Path, novos_registros: list[dict]
) -> tuple[int, list[dict]]:
    if not novos_registros:
        return 0, []

    if caminho_arquivo.exists():
        try:
            df_existente = pd.read_excel(caminho_arquivo, dtype=str)
            col_id = (
                "idDynamics"
                if "idDynamics" in df_existente.columns
                else "idOportunidadeDynamics"
            )
            ids_cadastrados = (
                set(df_existente[col_id].dropna().astype(str).tolist())
                if col_id in df_existente.columns
                else set()
            )
        except Exception:
            df_existente = pd.DataFrame(columns=COLUNAS_MATRIZ)
            ids_cadastrados = set()
    else:
        df_existente = pd.DataFrame(columns=COLUNAS_MATRIZ)
        ids_cadastrados = set()

    registros_para_salvar = []
    duplicados_detectados = []

    for reg in novos_registros:
        id_dyn = str(reg.get("idDynamics") or reg.get("idOportunidadeDynamics") or "")
        if id_dyn in ids_cadastrados:
            duplicados_detectados.append({"id": id_dyn, "nome": reg.get("NOME ", "")})
        else:
            registros_para_salvar.append(reg)
            ids_cadastrados.add(id_dyn)

    if registros_para_salvar:
        df_novos = pd.DataFrame(registros_para_salvar)
        df_final = pd.concat([df_existente, df_novos], ignore_index=True)

        for col in COLUNAS_MATRIZ:
            if col not in df_final.columns:
                df_final[col] = ""
        df_final = df_final[COLUNAS_MATRIZ]

        caminho_arquivo.parent.mkdir(parents=True, exist_ok=True)

        try:
            df_final.to_excel(caminho_arquivo, index=False)
        except PermissionError:
            raise PermissionError(
                f"Feche o arquivo '{caminho_arquivo.name}' no Excel antes de salvar!"
            )

        wb = openpyxl.load_workbook(caminho_arquivo)
        ws = wb.active

        # 1. Aplica o Objeto de TABELA do Excel
        max_row = ws.max_row
        max_col_letter = openpyxl.utils.get_column_letter(ws.max_column)
        ref_tabela = f"A1:{max_col_letter}{max_row}"

        tab = Table(displayName="TabelaMatrizLeads", ref=ref_tabela)
        style_info = TableStyleInfo(
            name="TableStyleLight1",
            showFirstColumn=False,
            showLastColumn=False,
            showRowStripes=True,
            showColumnStripes=False,
        )
        tab.tableStyleInfo = style_info

        ws._tables.clear()
        ws.add_table(tab)

        # 2. Estilos visuais personalizados por cima da Tabela
        # Cabeçalho: Azul #002060, Calibri 12, Negrito, Fonte Branca
        preenchimento_cabecalho = PatternFill(
            start_color="002060", end_color="002060", fill_type="solid"
        )
        fonte_cabecalho = Font(name="Calibri", size=12, bold=True, color="FFFFFF")

        # Bordas Finas Pretas
        borda_preta = Side(style="thin", color="000000")
        estilo_borda = Border(
            left=borda_preta,
            right=borda_preta,
            top=borda_preta,
            bottom=borda_preta,
        )

        alinhamento_central = Alignment(horizontal="center", vertical="center")

        # Formata todas as células (Alinhamento + Bordas)
        for row in ws.iter_rows(
            min_row=1,
            max_row=ws.max_row,
            min_col=1,
            max_col=ws.max_column,
        ):
            for cell in row:
                cell.alignment = alinhamento_central
                cell.border = estilo_borda

        # Força o estilo do cabeçalho customizado (Azul #002060)
        for cell in ws[1]:
            cell.fill = preenchimento_cabecalho
            cell.font = fonte_cabecalho

        wb.save(caminho_arquivo)

    return len(registros_para_salvar), duplicados_detectados
