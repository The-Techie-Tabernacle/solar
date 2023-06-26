"""
The plotting module which creates the based graphs for solar!
"""
import matplotlib.pyplot as plt


# ---------BAR------------
class Graph:
    def __init__(self, x=[], y=[], ylimMax=100):
        self.x = []
        self.y = []
        self.left_edges = []
        self.heights = []

        self.ylimMax = ylimMax

        if x:
            self.PopulateXAxis(x)
        else:
            self.x = []
        if y:
            self.PopulateYAxis(y)
        else:
            self.y = []

        self.setPlotLim()

    def setPlotLim(self):
        plt.ylim(0, self.ylimMax)

        # Space in x-axis and rotate
        plt.xticks(rotation=self.ylimMax / 10)
        plt.tick_params(axis="x", which="major", labelsize=7)  # Set x-axis label sizes

    def PopulateXAxis(self, listIn: list):
        self.x.clear()
        for i in listIn:
            self.x.append(i.replace("_", " ").title())

    def PopulateYAxis(self, listIn: list):
        self.y.clear()
        for i in listIn:
            self.y.append(i)

    # musa plz generalize ur code i am going to die -A
    # never. -M
    def setTitles(self, title, x, y):
        plt.title(title)
        plt.xlabel(x)
        plt.ylabel(y)

    def show(self, save=False, saveFile="graph.png"):  # target: str):
        try:
            if len(self.x) == len(self.y):
                # Plot the bar graph
                plt.bar(self.x, self.y)

                # Save the image
                if save:
                    plt.savefig(saveFile)

                # Show plot
                plt.show(block=False)
        except Exception as e:
            print(e)
