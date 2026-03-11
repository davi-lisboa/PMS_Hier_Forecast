import pandas as pd

from sktime.forecasting.statsforecast import StatsForecastAutoARIMA, StatsForecastAutoETS, StatsForecastAutoCES, StatsForecastAutoTBATS
from sktime.forecasting.compose import AutoEnsembleForecaster, StackingForecaster
from sklearn.linear_model import LinearRegression, Lasso, Ridge, ElasticNet
from lightgbm import LGBMRegressor

from sktime.transformations.series.detrend import STLTransformer, Detrender, Deseasonalizer, ConditionalDeseasonalizer
from sktime.transformations.series.difference import Differencer
from sktime.transformations.series.dropna import DropNA

from sktime.forecasting.compose import TransformedTargetForecaster, ForecastingPipeline
from sktime.transformations.hierarchical.reconcile import BottomUpReconciler, TopdownReconciler, OptimalReconciler, MiddleOutReconciler

def create_model():
    arima = StatsForecastAutoARIMA(sp=12)
    ets = StatsForecastAutoETS(season_length=12)
    ces = StatsForecastAutoCES(season_length=12)
    tbats = StatsForecastAutoTBATS(seasonal_periods=12)

    ensemble = AutoEnsembleForecaster(forecasters=[arima, ets, ces, tbats], regressor=LGBMRegressor(verbosity=-1))

    pipe = TransformedTargetForecaster(steps=[
        ('forecaster', ensemble),
        ('reconciler', OptimalReconciler())

    ])

    return pipe



def load_bundle(bundle_path: str):
    """
    Tenta carregar o modelo treinado, seu cutoff passado, a projecao passada 
    e o DataFrame combinado (real + proj) para calculos de variacao A/A do erro.
    """
    import joblib
    try:
        bundle = joblib.load(bundle_path)
        pipe = bundle['model']
        last_date = bundle['meta']['last_date']
        last_preds = bundle.get('last_preds', None)
        hist = bundle.get('hist', None)
        
        if hist is not None and last_preds is not None:
            previous_full_df = pd.concat([hist, last_preds]).sort_index()
        else:
            previous_full_df = None
            
        return bundle, pipe, last_date, last_preds, previous_full_df
    except FileNotFoundError:
        print("Modelo nao encontrado. Este sera um treinamento do zero.")
        return None, None, None, None, None

def save_bundle(pipe, fh, preds, pms_agg, bundle_path: str):
    """
    Salva o estado completo do pipeline hierarquico e preve para a proxima iteracao.
    """
    import joblib
    new_bundle = dict(
        model = pipe,
        fh = fh,
        meta = {
            'last_date': pipe.cutoff[0]
        },
        last_preds=preds,
        hist = pms_agg
    )
    joblib.dump(new_bundle, bundle_path)

if __name__ == '__main__':
    main()