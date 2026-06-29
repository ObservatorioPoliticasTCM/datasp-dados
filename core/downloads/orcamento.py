"""Downloads budget execution data from the São Paulo city government.

Provides two loaders:
- :func:`load_orcamento`: budget execution (despesa) data published by SEPLAN.
- :func:`load_orcamento_r`: budget execution (despesa) with administrative
  region data published by SEPLAN.

Both functions return a :class:`pandas.DataFrame` with an extra ``ANO`` column
containing the requested year.
"""

import requests
from io import BytesIO
import pandas as pd
from logging import info


from ..downloads import DEFAULT_HEADERS


def load_orcamento(year: int,
                   headers: dict = DEFAULT_HEADERS,
                   pandas_kwargs: dict | None = None,
                   request_timeout: int = 600) -> pd.DataFrame:
    """Download budget execution (despesa) data for a given year.

    Fetches the CSV file published by SEPLAN at
    ``prefeitura.sp.gov.br/documents/d/planejamento/basedadosexecucao_12{YY}-csv``
    and returns it as a DataFrame.

    Parameters
    ----------
    year : int
        The fiscal year to download (e.g. ``2024``).
    headers : dict
        HTTP request headers. Defaults to :data:`DEFAULT_HEADERS`.
    pandas_kwargs : dict, optional
        Extra keyword arguments forwarded to :func:`pandas.read_csv`,
        overriding the defaults (``sep=';'``, ``decimal=','``,
        ``encoding='latin1'``, ``dtype=str``).
    request_timeout : int
        Timeout in seconds for the HTTP request. Defaults to ``600``.

    Returns
    -------
    pandas.DataFrame
        Parsed CSV data with an additional ``ANO`` column set to *year*.

    Raises
    ------
    Exception
        Re-raises any :class:`requests.exceptions.RequestException` with a
        descriptive message.
    """
    url = f'https://prefeitura.sp.gov.br/documents/d/planejamento/basedadosexecucao_12{str(year)[-2:]}-csv'
    info(f"Fetching data from URL: {url}")
    try:
        response = requests.get(url, headers=headers, timeout=request_timeout)
        response.raise_for_status()
        csv_default_kwargs = {
            'sep': ';',
            'decimal': ',',
            'encoding': 'latin1',
            'dtype': str
        }
        if pandas_kwargs:
            csv_default_kwargs.update(pandas_kwargs)
        df = pd.read_csv(BytesIO(response.content), **csv_default_kwargs)
        df['ANO'] = year

        info(f"Data for year {year} loaded successfully with shape {df.shape}")
        return df
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error fetching data: {str(e)}")

def load_orcamento_r(year: int,
                     headers: dict = DEFAULT_HEADERS,
                     pandas_kwargs: dict | None = None,
                     request_timeout: int = 600) -> pd.DataFrame:
    """Download budget execution (despesa) with administrative region data for a given year.

    Fetches the CSV file published by SEPLAN at
    ``prefeitura.sp.gov.br/cidade/secretarias/upload/seplan/arquivos/Exercicio_{year}/basedadosDA_{year}.csv``
    and returns it as a DataFrame.

    Parameters
    ----------
    year : int
        The fiscal year to download (e.g. ``2024``).
    headers : dict
        HTTP request headers. Defaults to :data:`DEFAULT_HEADERS`.
    pandas_kwargs : dict, optional
        Extra keyword arguments forwarded to :func:`pandas.read_csv`,
        overriding the defaults (``sep=';'``, ``decimal=','``,
        ``thousands='.'``, ``encoding='latin1'``, ``dtype=str``).
    request_timeout : int
        Timeout in seconds for the HTTP request. Defaults to ``600``.

    Returns
    -------
    pandas.DataFrame
        Parsed CSV data with an additional ``ANO`` column set to *year*.

    Raises
    ------
    Exception
        Re-raises any :class:`requests.exceptions.RequestException` with a
        descriptive message.
    """
    url = f'https://prefeitura.sp.gov.br/cidade/secretarias/upload/seplan/arquivos/Exercicio_{year}/basedadosDA_{year}.csv'
    if year < 2024:
        url = f'https://prefeitura.sp.gov.br/cidade/secretarias/upload/seplan/arquivos/Exercicio_{year}/basedadosDA_12{str(year)[-2:]}.csv'
    info(f"Fetching data from URL: {url}")
    try:
        response = requests.get(url, headers=headers, timeout=request_timeout)
        response.raise_for_status()
        csv_default_kwargs = {
            'sep': ';',
            'decimal': ',',
            'thousands': '.',
            'encoding': 'latin1',
            'dtype': str
        }
        if pandas_kwargs:
            csv_default_kwargs.update(pandas_kwargs)
        df = pd.read_csv(BytesIO(response.content), **csv_default_kwargs)
        df['ANO'] = year

        info(f"Data for year {year} loaded successfully with shape {df.shape}")
        return df
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error fetching data: {str(e)}")