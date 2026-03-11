# %% Bibliotecas base
import sys
import pandas as pd
import numpy as np
import datetime as dt
import warnings

# Importacoes Locais (Projeto PMS Hierarquico)
from coleta import get_pms_index, get_pesos
from tratamento import prepare_pms_data
from modelo import load_bundle, save_bundle, create_model
from reports import report_forecast_error, report_forecast_diff, report_short_term_growth, report_annual_tables

warnings.filterwarnings('ignore')

# Configura o display do Pandas para sumários textuais limpos
pd.set_option('display.max_columns', None)

# %% 1.1 - Coleta os dados mais recentes da PMS
print("1.1 - Coletando e Preparando dados mais recentes da PMS...")
pms_raw = get_pms_index()
pesos_raw = get_pesos()
pms_agg = prepare_pms_data(pms_raw, pesos_raw)

# %% 1.2 - Recupera ultimo modelo
print("1.2 - Recuperando ultimo modelo treinado...")
bundle_path = "pms_forecast_bundle.joblib"
bundle, pipe, last_date, last_preds, previous_full_df = load_bundle(bundle_path)

# %% 2 - Compara ultima data disponivel da PMS com cutoff do modelo
current_last_date = pms_raw.index.get_level_values('data').max()

if bundle is not None:
    print(f"\n2 - Data atual PMS: {current_last_date.strftime('%Y-%m')} | Cutoff do Modelo: {last_date.strftime('%Y-%m')}")
    # 2.1 se forem iguais, encerra script
    if current_last_date <= last_date:
        print("    2.1 - Datas iguais. Base ja atualizada. Encerrando o processamento.")
        sys.exit(0)
    # 2.2 se data da PMS > cutoff continua script
    else:
        print("    2.2 - Data da PMS maior que cutoff. Continuando pre-processamento.")
else:
    print("\n2 - Nenhum cutoff previo (primeira execucao).")

# %% 3 - Calcula diferença do ultimo valor para o projetado (Visao A/A)
if bundle is not None and previous_full_df is not None:
    print("\n3 - Diferenca (A/A) do ultimo valor em relacao ao q foi projetado pelo modelo antigo:")
    err_df = report_forecast_error(pms_agg, previous_full_df, last_date)
    if not err_df.empty:
        display(err_df.round(2).fillna('-'))
    else:
        print("    Nenhum novo dado para comparar o projetado x realizado.")

# %% 4 - Reestima o modelo com os novos dados
print("\n4 - Reestimando o modelo hierarquico...")
if bundle is None:
    pipe = create_model()

pipe.fit(pms_agg)

# 4.1 - Projeta 24 meses a frente (Substituido datetime estatico por h dinamico do sktime)
print("4.1 - Projetando os proximos 24 meses (fh=1 a 24)...")
fh = np.arange(1, 24 + 1)
preds = pipe.predict(fh)

# %% 5 - Persiste modelo
print("\n5 - Persistindo o modelo final para a proxima iteracao...")
save_bundle(pipe, fh, preds, pms_agg, bundle_path)


# %% 6 - Calcula diferenças das projecoes (Tabela A/A de Curto Prazo)
print("\n6 - Crescimento A/A (%) da Projecao (Proximos 3 meses):")
new_full_df = pd.concat([pms_agg, preds]).sort_index()

preds_dates_short = preds.index.get_level_values('data').unique()[:3]
# report_short_term_growth(new_full_df, preds_dates_short)
report_forecast_diff(previous_full_df, last_preds, new_full_df, preds, 'yoy') \
    .round(1) \
    .groupby(level=['Setor', 'Divisão', 'Grupo']).head(6)

# %% 7 - Gera visualizacoes a/a e crescimento anual APENAS VIA TABELA
# print("\n7 - Extracao das Tabelas de Variacao A/A e 12M...")
# report_annual_tables(new_full_df)

print("\n*** Pipeline de Forecasting Concluido. ***\n")

# %%
