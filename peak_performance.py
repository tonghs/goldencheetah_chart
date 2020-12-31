import datetime
from typing import List, Tuple
import numpy as np
import plotly
from plotly.graph_objs import Scatter
from plotly.subplots import make_subplots
import tempfile
import pathlib
import time
import _thread as thread


duration = 20 * 60  # default 20 min
top_n = 20
recent = 20  # default show recnet 7th data
all_data = False


class DataField(object):
    HEART_RATE = 'heart.rate'
    POWER = 'power'

    @classmethod
    def get_list(cls):
        return [cls.POWER, cls.HEART_RATE]

    @classmethod
    def get_name_by_field(cls, field):
        data = {
            cls.POWER: 'Power',
            cls.HEART_RATE: 'Heart Rate',
        }

        return data.get(field)


def get_top_10_data(series, filter=""):
    power20min = GC.seasonPeaks(all=all_data, filter=filter, series=series, duration=duration)

    data_list: List[Tuple[datetime.datetime, float]] = []
    for t, value in zip(power20min['datetime'], power20min[f'peak_{series}_{duration}']):
        if value > 0:
            data_list.append((t, int(value)))

    top_data_list = sorted(data_list, key=lambda x: x[1])[-1 * top_n:]
    recent_data_list = sorted(data_list, key=lambda x: x[0])[-1 * recent:]

    return [o[0].strftime('%Y.%m.%d') for o in top_data_list], [o[1] for o in top_data_list], [o[0].strftime('%Y.%m.%d') for o in recent_data_list], [o[1] for o in recent_data_list]


def delete_temp_file(t):
    time.sleep(t)
    temp_file.close()


def get_fig():
    subplot_titles = [f"{DataField.get_name_by_field(DataField.POWER)} ({duration // 60} min) Top {top_n}",
                      f"{DataField.get_name_by_field(DataField.POWER)} ({duration // 60} min) Recent {recent} days",
                      f"{DataField.get_name_by_field(DataField.HEART_RATE)} ({duration // 60} min) Top {top_n}",
                      f"{DataField.get_name_by_field(DataField.HEART_RATE)} ({duration // 60} min) Recent {recent} days"]

    fig = make_subplots(rows=2, cols=2,
                        subplot_titles=subplot_titles)
    fig.update_layout(title=f"Peak Performances ({duration // 60} min)", legend_title_text='Peak Performances')

    for i, field in enumerate([('power', 'Data contains "P"'), ('heart.rate', '')]):
        _top_xx, _top_yy, _recent_xx, _recent_yy = get_top_10_data(field[0], field[1])

        top_xx = np.asarray(_top_xx)
        top_yy = np.asarray(_top_yy)
        recent_xx = np.asarray(_recent_xx)
        recent_yy = np.asarray(_recent_yy)

        title = DataField.get_name_by_field(field[0])

        fig.append_trace(Scatter(x=top_xx, y=top_yy, mode='lines+markers', name=f"{title} ({duration // 60} min) Top {top_n}"),
                         row=i + 1, col=1)
        fig.append_trace(Scatter(x=recent_xx, y=recent_yy, mode='lines+markers', name=f"{title} ({duration // 60} min) Recent {recent} days"),
                         row=i + 1, col=2)

    return fig


temp_file = tempfile.NamedTemporaryFile(mode="w+t", prefix="GC_", suffix=".html", delete=True)

plotly.offline.plot(get_fig(), auto_open=False, filename=temp_file.name)
GC.webpage(pathlib.Path(temp_file.name).as_uri())

thread.start_new_thread(delete_temp_file, (5,))
