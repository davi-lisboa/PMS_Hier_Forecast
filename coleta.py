# %% Bibliotecas base

import os
from pathlib import Path

import pandas as pd
import sidrapy as sidra

# %% get_pms_index
def get_pms_index():

    import pandas as pd
    import sidrapy as sidra

    # https://apisidra.ibge.gov.br/values/t/8688/n1/all/v/7167/p/last%208/c11046/56726/c12355/31399,31426,106869,106874,106876/d/v7167%205
    # https://apisidra.ibge.gov.br/values/t/8688/n1/all/v/7167/p/all/c11046/56726/c12355/allxt/d/v7167%205
    pms_secao = sidra.get_table(
                                table_code=8688,
                                territorial_level='1',
                                ibge_territorial_code='all',
                                variable='7167',#,7168',
                                period='all',
                                classification='11046/56726/c12355/allxt'
                            )

    # Ajuste das colunas
    pms_secao.columns = pms_secao.iloc[0, :]
    pms_secao = pms_secao.iloc[1:, :].reset_index(drop=True)
    pms_secao = pms_secao[['Mês (Código)', 'Atividades de serviços', 'Valor']] 
    pms_secao.columns = ['data', 'atividade', 'nindice']

    # # Ajuste nos tipos de dados
    pms_secao['data'] = pd.to_datetime(pms_secao['data'], format='%Y%m')
    pms_secao['nindice'] = pd.to_numeric(pms_secao['nindice'], errors='coerce')

    # # Agrupa dados
    pms_secao = pms_secao.groupby(['atividade', 'data']).last()


    return pms_secao


# %% get_pesos

def get_pesos(path: Path | str | None =  None):

    import os

    # path = r"C:\Users\dsilva52\OneDrive - UNIVERSO ONLINE S.A\Davi - Projetos\PMS\PMS Pesos Base 2022.xlsx"
    if path is None:
        try:
            path = os.path.join( os.getcwd(), "PMS Pesos Base 2022.xlsx" )

        except:
            raise TypeError("`path` arg should be Path-type or path-like string.")

    pesos = pd.read_excel(path, sheet_name="ADs_Setores e Subsetores").dropna()

    pesos['Códigos'] = pesos['Códigos'].str.replace("AD", "").str.strip()

    pesos['Códigos'] = pesos['Códigos'].apply(
        lambda x:
            x[0] + '.' + x[1:] if len(x) in [1, 2] 
            else x[0] + '.' + x[1] + '.' + x[2:]
    )

    pesos['Atividades'] = pesos['Códigos'] + ' ' + pesos['Setores e Subsetores']
    pesos = pesos[['Atividades', 'Participação Vol (Base 2022)']]
    pesos.columns = ['Atividades', 'Pesos']
    pesos['Pesos'] = pesos['Pesos'] * 100

    return pesos


# %% if name
if __name__ == '__main__':
    main()