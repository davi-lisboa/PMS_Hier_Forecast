# %% Bibliotecas base

import joblib
import pandas as pd
import numpy as np
import datetime as dt

import matplotlib.pyplot as plt
plt.style.use('seaborn-v0_8-darkgrid')

import warnings
warnings.filterwarnings('ignore')


# %% Coletas

from coleta import get_pms_index, get_pesos

pms_raw = get_pms_index()
pesos_raw = get_pesos()

bundle = joblib.load("pms_forecast_bundle.joblib")
pipe = bundle['model']
last_date = bundle['meta']['last_date']


if pms_raw.index.get_level_values('data').max() <= last_date:
    break

else:


# %%
    from tratamento import order_levels, ponderar_pms, agregar_pms

    pms_ordered = order_levels(
                        df= pms_raw.reset_index(), 
                        hier_col_name= 'atividade',
                        date_col= 'data', 
                        keep_cols= ['nindice']
                    ).dropna()

    pms_pond = ponderar_pms(pms_ordered, pesos_raw)

    pms_agg = agregar_pms(pms_pond)


# %%

# from modelo import create_model

# pipe = create_model()
pipe.fit(pms_agg)

# fh = range(1, 13)
fh = pd.date_range(
                start = pipe.cutoff[0],
                end = dt.date(pipe.cutoff[0].year + 2, 12, 1),
                freq='MS',
                inclusive='right'
                )

preds = pipe.predict(fh)

# %%

final_df = pd.concat([pms_agg, preds]).sort_index()
final_df

# %%

df_yoy = (
    final_df
    
    .groupby(level=['Setor', 'Divisão', 'Grupo', ])[['indice_pond']]
    .pct_change(12).multiply(100)
    .round(1)
    
    .query("data.dt.month == 12")
    
    .groupby(level=['Setor', 'Divisão', 'Grupo', ])[['indice_pond']].tail(3)
    
    .reset_index()
    .assign( data = lambda df: df['data'].dt.strftime('%b/%y'))
    .map(lambda x: np.nan if x == '__total' else x)
    .ffill(axis=1)
    .fillna('0. PMS Total')
    .set_index(['Setor', 'Divisão', 'Grupo', 'data'])
    
    .unstack(level='data')
    # .reset_index()
)

df_yoy

# %%

(

    final_df
    
    .groupby(level=['Setor', 'Divisão', 'Grupo', ])[['indice_pond']]
    .rolling(12).sum()#
    
    .groupby(level=['Setor', 'Divisão', 'Grupo', ])[['indice_pond']]
    .pct_change(12,).multiply(100).round(1)

    .droplevel(level=[3, 4,5])

    .query("data.dt.month == 12")
    
    .groupby(level=['Setor', 'Divisão', 'Grupo', ])[['indice_pond']].tail(3)
    
    .reset_index()
    .assign( data = lambda df: df['data'].dt.strftime('%b/%y'))
    .map(lambda x: np.nan if x == '__total' else x)
    .ffill(axis=1)
    .fillna('0. PMS Total')
    .set_index(['Setor', 'Divisão', 'Grupo', 'data'])
    
    .unstack(level='data')

 )

# %% 

bundle = dict(
    model = pipe,
    fh = range(1, 24 + 1),

    meta = {
            'last_date': pipe.cutoff[0],
            # 'freq': pms_raw.index.get_level_values('data').unique().inferred_freq
    }
)



joblib.dump(bundle, "pms_forecast_bundle.joblib")