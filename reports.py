import pandas as pd
import numpy as np

def report_forecast_error(pms_agg: pd.DataFrame, previous_full_df: pd.DataFrame, last_date: pd.Timestamp):
    """
    Retorna o DataFrame vetorizado do Erro YoY real vs projetado pelo modelo antigo (Passo 3).
    """
    from tratamento import transform_to_yoy, format_output_table
    
    previous_yoy = transform_to_yoy(previous_full_df)
    new_dates = pms_agg.index.get_level_values('data')[pms_agg.index.get_level_values('data') > last_date].unique()
    
    if len(new_dates) == 0:
        return pd.DataFrame()

    new_yoy = transform_to_yoy(pms_agg)
    
    proj_new_yoy = previous_yoy[previous_yoy.index.get_level_values('data').isin(new_dates)]
    real_new_yoy = new_yoy[new_yoy.index.get_level_values('data').isin(new_dates)]
    
    # Vetorizacao do calculo de diferencas
    real_val = real_new_yoy.rename(columns={'indice_pond': 'Realizado'})
    proj_val = proj_new_yoy.rename(columns={'indice_pond': 'Previsto'})
    
    diff = proj_val.join(real_val, how='inner')
    diff['Erro'] = diff['Previsto'] - diff['Realizado']

    # Formata nome e datas
    df_err = format_output_table(diff, name=True, dates=False) \
            .reorder_levels(order=[1,0], axis=1) \
            .sort_index(axis=1)
    
    ordem_lvl2 = ["Previsto", "Realizado", "Erro"]
    df_err = df_err.reindex(columns=pd.MultiIndex.from_product(
                                [
                                    df_err.columns.levels[0], # mantém a ordem original das datas (nível 0)
                                    ordem_lvl2                # nova ordem do nível 1
                                ]
                                                            )
                            )
    df_err.columns = pd.MultiIndex.from_tuples([(d.strftime('%b/%y'), t) for d,t in df_err.columns])
    
    return df_err

def report_short_term_growth(new_full_df: pd.DataFrame, preds_dates_short: pd.DatetimeIndex):
    """
    Gera print vetorizado do crescimento A/A (curto prazo) da projecao atual (Passo 6).
    """
    from tratamento import transform_to_yoy
    
    full_yoy = transform_to_yoy(new_full_df)
    
    for tsd in preds_dates_short:
        try:
            val = full_yoy.xs(tsd, level='data')[['indice_pond']].rename(columns={'indice_pond': 'A/A(%)_Projetado'})
            
            print(f"---> Projecao A/A para {tsd.strftime('%Y-%m')}:")
            if '__total' in val.index.get_level_values('Setor'):
                print(val.xs('__total', level='Setor', drop_level=False).round(2).to_string())
            else:
                print(val.head(2).round(2).to_string())
        except KeyError:
            print(f"Métrica ignorada para a data {tsd.strftime('%Y-%m')}")

def report_annual_tables(new_full_df: pd.DataFrame):
    """
    Gera prints formatados do Crescimento YoY (Dez/Dez) e Acumulado 12M (Passo 7).
    """
    from tratamento import format_output_table
    
    df_yoy_raw = (
        new_full_df
        .groupby(level=['Setor', 'Divisão', 'Grupo'])[['indice_pond']]
        .pct_change(12).multiply(100)
        .round(1)
        .query("data.dt.month == 12")
        .groupby(level=['Setor', 'Divisão', 'Grupo'])[['indice_pond']].tail(3)
    )
    df_yoy = format_output_table(df_yoy_raw, name=True, dates=True)

    print("\n------------------------------")
    print(" VARIACAO ANO A ANO (DEZ P/ DEZ)")
    print("------------------------------")
    print(df_yoy.fillna('-'))

    df_12m_raw = (
        new_full_df
        .groupby(level=['Setor', 'Divisão', 'Grupo'])[['indice_pond']]
        .rolling(12).sum()
        .groupby(level=['Setor', 'Divisão', 'Grupo'])[['indice_pond']]
        .pct_change(12).multiply(100).round(1)
        .droplevel(level=[3, 4, 5], axis=0) # Remove duplicatas geradas pelo rolling
        .query("data.dt.month == 12")
        .groupby(level=['Setor', 'Divisão', 'Grupo'])[['indice_pond']].tail(3)
    )
    df_12m = format_output_table(df_12m_raw, name=True, dates=True)

    print("\n------------------------------")
    print(" CRESCIMENTO ACUMULADO 12 MESES ")
    print("------------------------------")
    print(df_12m.fillna('-'))


def report_forecast_diff(old_full_df, old_preds, new_full_df, new_preds, transformation='yoy'):

    from tratamento import transform_to_yoy, format_output_table

    if transformation in ['yoy', 'YoY', 'a/a', 'A/A']:
        old = transform_to_yoy(old_full_df)
        new = transform_to_yoy(new_full_df)

    old_n_new = pd.merge(old, new, left_index=True, right_index=True, how='inner')
    old_n_new.columns = ['Projeção Anterior', 'Nova Projeção']

    old_n_new = old_n_new.query(
                    "data in @new_preds.index.get_level_values('data').unique()"
                                )

    old_n_new['Diff'] = old_n_new['Nova Projeção'] - old_n_new['Projeção Anterior']
    
    old_n_new.dropna(inplace=True)

    old_n_new = format_output_table(old_n_new, name=True, dates=True, transpose=False)

    return old_n_new

