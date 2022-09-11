import os
import time
import json
import pandas as pd
import numpy as np
from dateutil import parser
from datetime import datetime
from azure.ai.anomalydetector import AnomalyDetectorClient
from azure.ai.anomalydetector.models import DetectRequest, TimeSeriesPoint, TimeGranularity, \
    AnomalyDetectorError
from azure.core.credentials import AzureKeyCredential
import plotly.express as px
import plotly.graph_objects as go
from find_time import *


subscription_key = 'a2653cad6bdd4efaabf530b50d8efeca'
anomaly_detector_endpoint = 'https://mvaderic.cognitiveservices.azure.com/'

# create an Anomaly Detector client
ad_client = AnomalyDetectorClient(AzureKeyCredential(
    subscription_key), anomaly_detector_endpoint)


def detect_anomaly_last(sample_data, sensitivity, skip_point=29):
    globals()
    points = sample_data["series"]
    granularity = sample_data["granularity"]
    result = {
        "expectedValues": [None] * len(points),
        "upperMargins": [None] * len(points),
        "lowerMargins": [None] * len(points),
        "isNegativeAnomaly": [False] * len(points),
        "isPositiveAnomaly": [False] * len(points),
        "isAnomaly": [False] * len(points)
    }
    anom_count = 0

    for i in range(skip_point, len(points) + 1):
        series = [TimeSeriesPoint(
            timestamp=item["timestamp"], value=item["value"]) for item in points[i - 29: i]]
        request = DetectRequest(series=series, granularity=granularity,
                                sensitivity=sensitivity, max_anomaly_ratio=0.25)
        single_point = ad_client.detect_last_point(request)
        if single_point.is_anomaly == True:
            anom_count += 1
        result['expectedValues'][i-1] = single_point.expected_value
        result['upperMargins'][i-1] = single_point.upper_margin
        result['lowerMargins'][i-1] = single_point.lower_margin
        result['isNegativeAnomaly'][i-1] = single_point.is_negative_anomaly
        result['isPositiveAnomaly'][i-1] = single_point.is_positive_anomaly
        result['isAnomaly'][i-1] = single_point.is_anomaly

    return pd.DataFrame(result)


def build_figure(df):
    anomaly = df[df['isAnomaly']]
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['value'],
                             mode='lines',
                             name='value'))
    fig.add_trace(go.Scatter(
        x=anomaly['timestamp'], y=anomaly['value'], mode="markers"))
    return fig


def detect_anomaly_from_df(df, sensitivity=95):
    time_df = find_time(df)
    ft = time_df['Time'].apply(lambda x: len(x) > 10)
    time_df = time_df[ft]
    time_df['timestamp'] = time_df['Time'].apply(lambda x: str_to_time(str(x)))
    time_dt = time_df['timestamp'].value_counts().sort_index().to_dict()
    del time_dt['']
    sample_data = {
        "granularity": "daily",
        "series": [
            {
                "timestamp": k,
                "value": v
            }
            for k, v in time_dt.items()
        ]
    }
    res = detect_anomaly_last(sample_data, sensitivity)
    df = pd.concat([pd.DataFrame(sample_data['series']), res],
                   axis=1, join="inner")
    fig = build_figure(df.iloc[30:])
    return time_df, fig, df[df['isAnomaly']].timestamp.to_list()
