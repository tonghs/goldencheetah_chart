from typing import Tuple, List
import numpy as np
import plotly
from plotly.graph_objs import Scatter
from plotly.subplots import make_subplots
import tempfile
import pathlib
import time
import _thread as thread


mm_data = GC.activityMeanmax()


class DataField(object):
    HEART_RATE = 'heart.rate'
    CADENCE = 'cadence'
    SPEED = 'speed'
    POWER = 'power'

    @classmethod
    def get_list(cls):
        return [cls.POWER, cls.HEART_RATE, cls.SPEED, cls.CADENCE]

    @classmethod
    def get_name_by_field(cls, field):
        data = {
            cls.POWER: 'Power',
            cls.HEART_RATE: 'Heart Rate',
            cls.SPEED: 'Speed',
            cls.CADENCE: 'Cadence',
        }

        return data.get(field)


def get_data_by_field(field: str) -> Tuple[List[str], List[int]]:
    serials = mm_data.get(field)
    xx: List[str] = []
    yy: List[int] = []
    for i, s in enumerate([5, 10, 12, 20, 30, 60, 120, 300, 360, 600, 720, 1200, 1800, 3600, 5400]):
        if s > len(serials):
            break

        if s >= 60:
            s_h = f"{int(s // 60)} min"
        else:
            s_h = f"{str(s)} s"
        xx.append(s_h)
        value = int(serials[s]) if field != DataField.SPEED else float("{:.2f}".format(serials[s]))   
        yy.append(value)

    return xx, yy


def delete_temp_file(t):
    time.sleep(t)
    temp_file.close()


def get_fig():
    subplot_titles = [DataField.get_name_by_field(o) for o in DataField.get_list()]

    cols = 2
    fig = make_subplots(rows=len(DataField.get_list()) // cols, cols=cols,
                        subplot_titles=subplot_titles,  x_title="Time")

    fig.update_layout(title="Peak Data", legend_title_text='Mean Max Curve')

    data_list: List[Scatter] = []
    for i, field in enumerate(DataField.get_list()):
        _xx, _yy = get_data_by_field(field)
        xx = np.asarray(_xx)
        yy = np.asarray(_yy)

        title = DataField.get_name_by_field(field)
        fig.append_trace(Scatter(x=xx, y=yy, mode='lines+markers', fill="tonextx", name=title),
                         row=i // cols + 1, col=i % cols + 1)
    return fig


temp_file = tempfile.NamedTemporaryFile(mode="w+t", prefix="GC_", suffix=".html", delete=True)
plotly.offline.plot(get_fig(), auto_open=False, filename=temp_file.name)
GC.webpage(pathlib.Path(temp_file.name).as_uri())
thread.start_new_thread(delete_temp_file, (5,))

