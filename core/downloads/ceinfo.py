import requests
from io import BytesIO
import pandas as pd
from logging import info


from ..downloads import DEFAULT_HEADERS

SAUDE_EM_DADOS_URL = {
    2024: 'https://prefeitura.sp.gov.br/documents/d/saude/tabelas_ceinfo_dados_sub_2024_v3_rev09012025'
}

def load_consultas(year: int,
                   headers: dict = DEFAULT_HEADERS,
                   pandas_kwargs: dict | None = None,
                   request_timeout: int = 600) -> pd.DataFrame:
    url = SAUDE_EM_DADOS_URL.get(year)
    if not url:
        raise ValueError(f"No URL defined for year {year}.")
    info(f'Downloading CEINFO data from {url}')

    response = requests.get(url, headers=headers, timeout=request_timeout)
    response.raise_for_status()
    xlsx_file = BytesIO(response.content)

    # A tabela desejada é a `Consultas Medicas_Odontológicas`,
    # então vamos abri-la como um dataframe.
    sheet_name = 'Consultas Medicas_Odontológicas'
    default_kwargs = {
        'sheet_name': sheet_name,
        'skiprows': 5,
        'header': [0, 1],
        'thousands': '.',
    }
    if pandas_kwargs:
        default_kwargs.update(pandas_kwargs)

    df = pd.read_excel(xlsx_file, **default_kwargs)

    # Como a tabela original vem em um formato amigável para humanos,
    # precisamos ajustá-la para melhorar a sua utilização computacional.
    # A primeira coisa é filtrar linhas e colunas carregadas por engano,
    # por conter informações de fonte ou caracteres não imprimíveis.
    df = df.iloc[:32, 1:]

    # Depois, precisamos remover as colunas de totais, que resultariam
    # em duplicação dos valores caso fossem mantidas.
    cols_total_level0 = df.columns.get_level_values(0).str.contains('total', case=False)
    cols_total_level1 = df.columns.get_level_values(1).str.contains('total', case=False)
    df = df.loc[:, ~cols_total_level0 & ~cols_total_level1]

    # Agora, vamos transformar os níveis das colunas em novas colunas de
    # valores (despivotar a tabela).
    id_col = df.columns[0]
    df = pd.melt(df, id_vars=[id_col])

    # Renomeamos as colunas
    df.columns = ['Subprefeitura', 'Categoria', 'Subcategoria', 'Qtd_Consultas']

    # E removemos as linhas de consultas odontológicas
    df = df[~df['Categoria'].str.contains('Odontológica')]

    # Ainda, substituímos os `-` por 0 na coluna de quantidade de
    # consultas.
    hifen = df['Qtd_Consultas'] == '-'
    df.loc[hifen, 'Qtd_Consultas'] = 0
    df['Qtd_Consultas'] = df['Qtd_Consultas'].astype(int)
    
    # Por último, vamos corrigir os nomes das categorias.
    df['Categoria'] = df['Categoria'].apply(
        lambda c: 'Consulta Médica na Atenção Básica' if 'Atenção Básica' in c else c
    )
    df['Categoria'] = df['Categoria'].apply(
        lambda c: 'Consulta Médica/Atendimento em Urgência/Emergência' if 'Urgência' in c else c
    )

    return df
