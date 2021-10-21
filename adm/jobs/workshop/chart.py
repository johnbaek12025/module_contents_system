import datetime

from matplotlib import pyplot as plt
from matplotlib import font_manager
from matplotlib.ticker import FuncFormatter
from matplotlib.ticker import MultipleLocator

from adm import to_int


def set_bar(bar):
    if None in [bar.tick, bar.value]:
        return False
    month = bar.tick[4:6]
    day = bar.tick[6:8]
    bar.tick = f"{month}/{day}"
    if bar.value < 0:
        bar.color = "lightblue"
    else:
        bar.color = "salmon"
    return True


def get_bar_chart(rows, local_image_whole_path):
    chart_dict = {
        "face_color": "whitesmoke",
        "grid_color": "silver",
        "spine_top": False,
        "spine_left": False,
        "xaxis_format": "%m/%d",
        "tick_position": "right",
        "tick_interval": 5,
    }
    bc = Chart(**chart_dict)    
    bar_chart_data = get_bar_chart_data(rows=rows, func=set_bar)    
    bc.add_data(bar_chart_data, chart_type="bar", xhline=0)
    bc.finalize_chart(local_image_whole_path)
    


def get_bar_chart_data(rows, func):
    set_bar_chart_data = []
    for tick in rows:
        bar = Bar()
        bar.tick = tick
        bar.value = rows[tick]
        if func(bar):
            set_bar_chart_data.append(bar)
    return set_bar_chart_data


class Chart(object):
    def __init__(self, **kwargs):
        self.grid_color = kwargs.get("grid_color", None)
        self.face_color = kwargs.get("face_color", "white")

        self.tick_position = kwargs.get("tick_position", "right")
        self.tick_interval = kwargs.get("tick_interval", 1)

        self.spine_top = kwargs.get("spine_top", True)
        self.spine_bottom = kwargs.get("spine_bottom", True)
        self.spine_left = kwargs.get("spine_left", True)
        self.spine_right = kwargs.get("spine_right", True)
        self.xaxis_format = kwargs.get("xaxis_format")

        self.xhline = kwargs.get("xhline")

        self.ax = None
        self.ax2 = None

        self.initialize_chart()

    def initialize_chart(self):
        f = plt.figure(figsize=(8, 2))

        font_name = font_manager.FontProperties(
            fname="../analysis_data/fonts/arial/arial.ttf"
        ).get_name()
        plt.rc("font", family=font_name)

        self.ax = f.add_subplot()

        if self.tick_position == "right":
            self.ax.yaxis.tick_right()

        if self.grid_color:
            self.ax.grid(color=self.grid_color)

    def add_data(self, lo, chart_type="plot", twinx=False, xhline=None):
        ticks = [x.tick for x in lo]
        values = [x.value for x in lo]

        formatter = FuncFormatter(lambda x, p: format(int(x), ","))
        if twinx:
            ax = self.ax.twinx()
        else:
            ax = self.ax

        ax.yaxis.set_major_formatter(formatter)
        ax.spines["top"].set_visible(self.spine_top)
        ax.spines["bottom"].set_visible(self.spine_bottom)
        ax.spines["left"].set_visible(self.spine_left)
        ax.spines["right"].set_visible(self.spine_right)

        if chart_type == "plot":
            ax.plot(ticks, values)
        elif chart_type == "bar":
            color = [x.color for x in lo]
 
            ax.bar(ticks, values, color=color)

        if xhline is not None:
            ax.axhline(y=xhline, color="grey", linewidth=1)

    def finalize_chart(self, image_path, count=5, yaxis=None):        
        self.ax.xaxis.set_major_locator(MultipleLocator(count))        
        plt.gca().patch.set_facecolor(self.face_color)
        plt.savefig(image_path, bbox_inches="tight")


class Bar:
    def __init__(self):
        self.value = ""
        self.tick = ""
        self.color = ""

    def to_dict(self):
        return {
            "value": self.value,
            "tick": self.tick,
            "color": self.color,
        }
