import datetime
import matplotlib as mpl
from matplotlib import pyplot as plt
from matplotlib import font_manager
from matplotlib.ticker import FuncFormatter
from matplotlib.ticker import MultipleLocator
from adm import to_int
font_manager._rebuild()


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
        self.grid = kwargs.get("grid", False)
        self.rotation = kwargs.get("rotation", None)
        self.ax = None
        self.ax2 = None
        self.initialize_chart()

    def initialize_chart(self):
        font_list = font_manager.findSystemFonts(fontpaths='../anaconda3/envs/analysis/lib/python3.8/site-packages/matplotlib/mpl-data/matplotlibrc', fontext='ttf')
        f = plt.figure(figsize=(8, 2))        
        font_name = font_manager.FontProperties(
            fname="../analysis_data/fonts/korean/NanumGothic.ttf"
        ).get_name()
        plt.rc("font", family=font_name)
        self.ax = f.add_subplot()
        if self.tick_position == "right":
            self.ax.yaxis.tick_right()
        if self.grid_color:
            self.ax.grid(color=self.grid_color, axis=self.grid)

    def add_data(self, lo, chart_type="plot", colors=None, label=None, twinx=False, xhline=None, exval=None):
        self.ticks = [x.tick for x in lo]
        values = [x.value for x in lo]        
        formatter = FuncFormatter(lambda x, p: format(int(x), ","))
        if not exval:            
            if twinx:
                ax = self.ax.twinx()                                    
            else:
                ax = self.ax        
        else:            
            if twinx:
                ax = self.ax.twinx()                                    
                ax.set_ylim(exval[0], exval[1])
            else:
                ax = self.ax
        ax.yaxis.set_major_formatter(formatter)
        ax.spines["top"].set_visible(self.spine_top)
        ax.spines["bottom"].set_visible(self.spine_bottom)
        ax.spines["left"].set_visible(self.spine_left)
        ax.spines["right"].set_visible(self.spine_right)

        if chart_type == "plot":            
            if colors and label:                
                ax.plot(self.ticks, values, color=colors, label=label)                    
            elif colors:                
                ax.plot(self.ticks, values, color=colors)                                                       
            else:                
                ax.plot(self.ticks, values)                                    
        elif chart_type == "bar":
            color = [x.color for x in lo]
            if not label:                
                ax.bar(self.ticks, values, color=color)                                    
            else:                
                ax.bar(self.ticks, values, color=color, label=label)                
        if xhline is not None:
            ax.axhline(y=xhline, color="grey", linewidth=1)

    def finalize_chart(self, image_path, leg=None, grid=None,line=None, ticks=False, loc='lower right', loc_position = (0.85, -0.4), le_frame=False):
        self.ax.xaxis.set_major_locator(MultipleLocator(self.tick_interval))        
        if self.rotation:
            plt.xticks(rotation = self.rotation)
        if ticks == True:
            plt.xticks(self.ticks)
        if self.grid:
            if grid == 'xgrid':
                plt.grid(self.grid, axis='x')
        elif not self.grid :
            plt.grid(False)
        if leg:
            plt.legend(loc = loc, ncol=len(leg), bbox_to_anchor= loc_position, frameon=le_frame)
        else:            
            plt.legend(leg, loc ='lower left')                            
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
