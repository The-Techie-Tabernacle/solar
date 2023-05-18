import matplotlib.pyplot as plt
from datetime import datetime as DT

# Create x and y coordinates
x = []
y = []


def UserFriendlyTitle():
    for i in x:
        n = i.replace("_", " ").title()
        d = x.index(i)
        x[d] = n


def PopulateXAxis(officers: list):
    x.clear()
    for i in officers:
        x.append(i)
    UserFriendlyTitle()


def PopulateYAxis(non_endorsements: list):
    y.clear()
    for i in non_endorsements:
        y.append(i)


# Set titles
plt.title("Percentage of non-endorsers in Delegate and Officers")
plt.xlabel("Officers")
plt.ylabel("Percentage of WA nations")

# ---------BAR------------
# Create left edges (x-axis) and heights (y-axis)
left_edges = []
heights = []

# Y-Axis limit
plt.ylim(0, 100)

# Space in x-axis and rotate
plt.xticks(rotation=10)
plt.tick_params(axis="x", which="major", labelsize=7)


def GraphTheGraph(target: str):
    try:
        if len(x) == len(y):
            # Plot the bar graph
            plt.bar(x, y)

            # Save the image
            plt.savefig(f"graphic-{DT.now().date().isoformat()}-{target}.png")

            # Show plot
            plt.show(block=False)
    except Exception as e:
        print(e)
