# import matplotlib
import matplotlib.pyplot as plt
from datetime import datetime as DT

# ---------LINE------------
# Create x and y coordinates
x = [
    "Beaverdam Hollow",
    "counterfeit_kyrusia_puppet",
    "jurait",
    "lockeport",
    "major_nice",
    "quebec_land",
]
y = [23.30, 54.37, 42.72, 39.81, 43.69, 54.37]

for i in x:
    n = i.replace("_", " ").title()
    d = x.index(i)
    x[d] = n

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
plt.xticks(rotation=15)
plt.tick_params(axis="x", which="major", labelsize=7)

# Plot the bar graph
plt.bar(x, y)

# Save the image
plt.savefig(f"graphic-{DT.now().date().isoformat()}-DEBUG.png")

# Show plot
plt.show()
