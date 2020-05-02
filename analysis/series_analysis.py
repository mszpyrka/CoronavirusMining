import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import json
import glob
import dateutil
import datetime
from pycountry import countries


def decompose(pd_series, mean_window_size):
    """
    Decompose time series into trend and residuals component.
    Trend is calculated by convolving the singal with average filter.
    """
    if mean_window_size % 2 == 0:
        raise Exception('mean window must have odd length')
    
    data = pd_series.values
    index = pd_series.index.values
    
    margin = mean_window_size // 2
    data_cut = data[margin:-margin]
    index_cut = index[margin:-margin]
    
    kernel = np.ones(mean_window_size) / mean_window_size
    trend = np.convolve(data, kernel, mode='valid')
    residuals = data_cut - trend
    
    trend_series = pd.Series(trend, index_cut)
    residuals_series = pd.Series(residuals, index_cut)
    
    return {
        'trend': trend_series,
        'residuals': residuals_series
    }
