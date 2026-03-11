# %% Bibliotecas base
import sys
import pandas as pd
import numpy as np
import datetime as dt
import warnings

# Importacoes Locais (Projeto PMS Hierarquico)
from coleta import get_pms_index, get_pesos
from tratamento import prepare_pms_data
from modelo import save_bundle, create_model

warnings.filterwarnings('ignore')

# Configura o display do Pandas para sumários textuais limpos
pd.set_option('display.max_columns', None)

# %% 1.1 - Coleta e Preparacao de dados
print("1.1 - Coletando e preparando dados da PMS...")
pms_raw = get_pms_index()
pesos_raw = get_pesos()
pms_agg = prepare_pms_data(pms_raw, pesos_raw)

# %% 1.2 - Filtro On-Demand baseado no Cutoff
cutoff_date = '2025-09'
print(f"1.2 - Aplicando filtro On-Demand. Mantendo dados ate: {cutoff_date}")
pms_agg = pms_agg.query(f"data <= '{cutoff_date}'")

# Vefirica se sobrou algum dado apos filtro
if pms_agg.empty:
    print("Base vazia apos o filtro de cutoff. Verifique a data informada.")
    sys.exit(1)

# %% 4 - Calcula e Reestima o modelo
print("\n4 - Reestimando o modelo hierarquico com base truncada...")
pipe = create_model()
pipe.fit(pms_agg)

# 4.1 - Projeta 24 meses a frente
print("4.1 - Projetando os proximos 24 meses (fh=1 a 24)...")
fh = np.arange(1, 24 + 1)
preds = pipe.predict(fh)

# %% 5 - Persiste modelo
bundle_path = "pms_forecast_bundle.joblib"
print(f"\n5 - Persistindo o modelo de teste em {bundle_path}...")
save_bundle(pipe, fh, preds, pms_agg, bundle_path)

print(f"\n*** Modelo on demand treinado e persistido com sucesso (Cutoff real: {pipe.cutoff[0].strftime('%Y-%m')}). ***\n")

# %%
