from pandas import Series
from unidecode import unidecode

def clean_subprefeitura(series:Series) -> Series:
    return (
        series
        .apply(unidecode)
        .str.upper()
        .str.replace("'", ' ')
    )