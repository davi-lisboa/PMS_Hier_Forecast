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




if __name__ == '__main__':
    main()