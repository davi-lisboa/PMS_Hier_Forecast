import os

import pandas as pd
import numpy as np

def order_levels(
                    df: pd.DataFrame, 
                    hier_col_name: str | None = None,
                    date_col: str | None = None, 
                    keep_cols: list | None = None,
                    ) -> pd.DataFrame:
    """
    Transforma um DataFrame da PMS (Pesquisa Mensal de Serviços/IBGE) que contém
    uma coluna hierárquica de "Atividades" em uma estrutura ao nível de
    (Setor, Divisão, Grupo), preservando colunas de interesse e resolvendo
    duplicidades de "folhas" por regras de preenchimento e consolidação.

    ----------------------------------------------------------------------------
    Contexto (PMS/IBGE)
    ----------------------------------------------------------------------------
    Nas tabelas/quadros da PMS, os rótulos hierárquicos de atividades costumam
    apresentar níveis que podem ser identificados por padrões de pontuação e
    espaços. Este procedimento foi desenhado especificamente para esse layout
    textual, detectando:

      • Setor    → strings cujo padrão satisfaça: x[1:3] == '. '
      • Divisão  → strings cujo padrão satisfaça: x[1] == '.' e x[3] == ' '
      • Grupo    → strings cujo padrão satisfaça: x[3] == '.'

    A função:
      1) Normaliza espaços dos rótulos;
      2) Cria colunas "Setor", "Divisão" e "Grupo" com base no padrão acima;
      3) Propaga (ffill) níveis superiores para linhas subsequentes;
      4) Garante a presença de um rótulo de "Grupo" por (Setor, Divisão) via
         última ocorrência não nula no bloco (regra do "last");
      5) Mantém apenas as linhas cuja linha original seja efetivamente o "Grupo"
         (folha) — evitando duplicidade da hierarquia;
      6) Retorna, para as colunas `keep_cols`, ou:
         • um DataFrame com índice multi-nível (Setor, Divisão, Grupo, data)
           se `date_col` for informada; ou
         • um DataFrame agregado por (Setor, Divisão, Grupo) com agregação
           `last` (ordem natural do DataFrame) se `date_col` for None.

    ----------------------------------------------------------------------------
    Parâmetros
    ----------------------------------------------------------------------------
    df : pd.DataFrame
        DataFrame de entrada contendo a coluna hierárquica e as colunas de
        interesse a serem preservadas.
    hier_col_name : str
        Nome da coluna com os rótulos hierárquicos de "Atividades" (formato PMS).
    date_col : str | None, padrão None
        Nome da coluna de data. Se fornecida, o retorno vem indexado por
        (Setor, Divisão, Grupo, date_col) e ordenado.
    keep_cols : list[str] | None
        Lista de colunas a manter/retornar (e.g., medidas, pesos, valores).
        Deve existir em `df`.

    ----------------------------------------------------------------------------
    Retorno
    ----------------------------------------------------------------------------
    pd.DataFrame
        • Se `date_col` não for None:
            DataFrame com índice (Setor, Divisão, Grupo, date_col), contendo
            `keep_cols`, ordenado por índice.
        • Caso contrário:
            DataFrame agregado em (Setor, Divisão, Grupo) usando agregação
            `last` para `keep_cols`.

    ----------------------------------------------------------------------------
    Pré-condições e Assunções
    ----------------------------------------------------------------------------
    • `hier_col_name` existe em `df` e contém strings com o layout de pontuação
      típico da PMS (detecção por posições x[1], x[3], etc.).
    • As colunas listadas em `keep_cols` existem em `df`.
    • Se informada, `date_col` existe em `df`.
    • A agregação `last` depende da ordem das linhas no DataFrame (última
      ocorrência no agrupamento). Se a ordem importa, garanta que `df` já esteja
      ordenado previamente.
    • A função é especializada no layout da PMS; não é genérica para
      hierarquias arbitrárias.

    ----------------------------------------------------------------------------
    Efeitos Colaterais
    ----------------------------------------------------------------------------
    • Não modifica `df` original (trabalha sobre uma cópia).
    • Constrói colunas auxiliares ("Setor", "Divisão", "Grupo", "grupo_fill",
      "flag_duplicate") na cópia interna, descartadas no retorno final.

    ----------------------------------------------------------------------------
    Exemplos (esquemático)
    ----------------------------------------------------------------------------
    >>> # Supondo df com colunas: ["Atividades", "Data", "Valor"]
    >>> # e strings de "Atividades" no padrão PMS
    >>> order_levels(
    ...     df,
    ...     hier_col_name="Atividades",
    ...     date_col="Data",
    ...     keep_cols=["Valor"]
    ... )
    # Retorna um DataFrame indexado por (Setor, Divisão, Grupo, Data) com a
    # coluna "Valor" consolidada na folha "Grupo".

    """
    # Trabalhar sobre cópia para não alterar o DataFrame original
    temp = df.copy(deep=True)

    # Normaliza espaços à esquerda/direita nos rótulos hierárquicos
    temp[hier_col_name] = temp[hier_col_name].str.strip()

    # ----------------------------------------------------------------------
    # Identificação dos níveis hierárquicos segundo o padrão textual da PMS
    # ----------------------------------------------------------------------

    # "Setor": linhas cujo rótulo atende ao padrão x[1:3] == '. '
    temp['Setor'] = temp[hier_col_name].map(lambda x: x if x[1:3] == '. ' else np.nan)
    # Propaga o último "Setor" válido para baixo
    temp['Setor'] = temp['Setor'].ffill()

    # "Divisão": linhas cujo rótulo atende ao padrão x[1] == '.' e x[3] == ' '
    temp['Divisão'] = temp[hier_col_name].map(lambda x: x if x[1]=='.' and x[3]==' ' else np.nan)
    # Propaga a "Divisão" por bloco de "Setor"
    temp['Divisão'] = temp.groupby(['Setor'])[['Divisão']].ffill()

    # "Grupo": linhas cujo rótulo atende ao padrão x[3] == '.'
    temp['Grupo'] = temp[hier_col_name].map(lambda x: x if x[3] == '.' else np.nan)

    # ----------------------------------------------------------------------
    # Mantém apenas linhas com Divisão válida (garante bloco hierárquico)
    # ----------------------------------------------------------------------
    temp.dropna(subset=['Divisão'], inplace=True)

    # Para cada (Setor, Divisão), captura a última ocorrência não nula de "Grupo"
    # e cria "grupo_fill" para preencher lacunas
    grupo_fill = (
                    temp
                    .groupby(['Setor', 'Divisão'], as_index=False)[['Grupo']]
                    .last()
                    .ffill(axis=1)
                    .rename(columns={'Grupo': 'grupo_fill'})
                )

    # Junta "grupo_fill" de volta ao DataFrame, por (Setor, Divisão)
    temp = (
                temp
                .merge(
                            grupo_fill,
                            left_on=['Setor', 'Divisão'],
                            right_on=['Setor', 'Divisão'],
                            how='left'
                        )
            )

    # Se "Grupo" estiver nulo numa linha válida, usa "grupo_fill" para completar
    temp['Grupo'] = temp[['Grupo', 'grupo_fill']].bfill(axis=1)['Grupo']

    # Sinaliza linhas que representam efetivamente o "Grupo" (folhas)
    temp['flag_duplicate'] = (temp[hier_col_name] == temp['Grupo'])

    # Mantém apenas as linhas marcadas como folhas
    temp = temp.loc[temp['flag_duplicate'] == True]

    # Se houver coluna de data, define índice multi-nível e ordena;
    # caso contrário, agrega por (Setor, Divisão, Grupo) usando "last"
    if date_col is not None:
        temp = temp.set_index(['Setor', 'Divisão', 'Grupo', date_col])[keep_cols].sort_index()
    else:
        temp = temp.groupby(['Setor', 'Divisão', 'Grupo'])[keep_cols].last()

    # Retorna estrutura consolidada ao nível de "Grupo"
    return temp


# %%

def ponderar_pms(nindice_df, pesos_df):
    
  pond_df = (
    nindice_df.reset_index()
    .merge(pesos_df, left_on='Grupo', right_on='Atividades', how='left')
    .assign(
            indice_pond = lambda df: df['nindice'] * df['Pesos']/100
            )
    .set_index(['Setor', 'Divisão', 'Grupo', 'data'])[['indice_pond']]
  )

  return pond_df 


# %%

from sktime.transformations.hierarchical.aggregate import Aggregator

def agregar_pms(pond_pms):
    
  pms_agg = Aggregator().fit_transform(pond_pms)

  return pms_agg

def prepare_pms_data(pms_raw: pd.DataFrame, pesos_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Encapsula o pipeline sequencial de tratamento bruto para o input do Sktime.
    (1) Ordering (2) Ponderacao (3) Agregacao Hierarquica OLS.
    """
    pms_ordered = order_levels(
        df= pms_raw.reset_index(), 
        hier_col_name= 'atividade',
        date_col= 'data', 
        keep_cols= ['nindice']
    ).dropna()

    pms_pond = ponderar_pms(pms_ordered, pesos_raw)
    pms_agg = agregar_pms(pms_pond)
    return pms_agg

# %%
def transform_to_yoy(df: pd.DataFrame, col_name: str = 'indice_pond') -> pd.DataFrame:
    """Aplica a transformação Ano a Ano (YoY) na série histórica respeitando a hierarquia."""
    df_yoy = (
        df.groupby(level=['Setor', 'Divisão', 'Grupo'])[[col_name]]
        .pct_change(12).multiply(100)
    )
    return df_yoy


def format_output_table(
        df: pd.DataFrame, 
        name: bool = True, 
        dates: bool = True, 
        transpose: bool = True) -> pd.DataFrame:
    """
    Formata um DataFrame retornado das projeções.
    Se name=True, formata '__total' para '0. PMS Total'.
    Se dates=True, formata as datas para string '%b/%y'.
    """
    temp = df.copy()
    
    if name:
        temp = temp.reset_index()
        temp[['Setor', 'Divisão', 'Grupo']] = temp[['Setor', 'Divisão', 'Grupo']].map(lambda x: np.nan if x == '__total' else x)
        # Preenche possiveis NaNs nos agrupamentos pais e renomeia o Total
        temp = temp.ffill(axis=1).fillna('0. PMS Total')
        temp = temp.set_index(['Setor', 'Divisão', 'Grupo', 'data'])
        temp = temp.sort_index()
    
    if dates:
        temp = temp.reset_index()
        temp['data'] = temp['data'].dt.strftime('%b/%y')
        temp = temp.set_index(['Setor', 'Divisão', 'Grupo', 'data'])
    
    if transpose:
        temp = temp.unstack(level='data')
    
    return temp

if __name__ == '__main__':
    main()
