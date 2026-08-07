# Matplotlib Methods Used

This file lists every Matplotlib method used in `app.py` with a one-line explanation

- `matplotlib.use()` : Sets the Matplotlib backend (here `'Agg'`) so plots can be rendered to files without a display.
- `plt.figure()` : Creates a new figure object and sets the figure size for subsequent plotting commands.
- `plt.bar()` : Draws a bar chart for the provided x and height values.
- `plt.title()` : Adds a title string to the current axes.
- `plt.ylabel()` : Sets the label text for the y-axis.
- `plt.xticks()` : Configures the x-axis tick labels and their appearance (rotation, alignment, font size).
- `plt.tight_layout()` : Adjusts subplot parameters to give specified padding and avoid label overlap.
- `plt.savefig()` : Saves the current figure to an image file on disk (PNG in this project).
- `plt.close()` : Closes the current figure to free memory.
- `plt.pie()` : Draws a pie chart for parts of a whole and supports customization (colors, start angle, autopct, etc.).
- `plt.text()` : Places text at an arbitrary position on the axes (used here for pass percentage and caption).
- `plt.legend()` : Adds a legend to the axes describing plotted elements.

Below are the keyword-argument names used in `app.py` with a beginner-friendly one-line explanation for each usage.

- `figsize` (in `plt.figure(figsize=(w, h))`) : Sets the figure width and height in inches so the plot has the desired aspect and space.
- `color` : Sets the fill color(s) for bars or pie slices; can be a single color or a list matching each bar/slice.
- `rotation` (in `plt.xticks`) : Rotates the x-axis tick labels by degrees so long names don't overlap.
- `ha` (horizontal alignment) : Aligns text or tick labels horizontally (`'left'`, `'center'`, `'right'`).
- `va` (vertical alignment) : Aligns text vertically (`'top'`, `'center'`, `'bottom'`).
- `fontsize` : Sets the font size for text elements like tick labels or annotations.
- `fontweight` : Sets text boldness (e.g., `'bold'`) for emphasis on numbers or titles.
- `startangle` (in `plt.pie`) : Rotates the start position of the first pie slice so the chart orientation is clearer.
- `autopct` (in `plt.pie`) : A format string (`'%1.1f%%'`) that tells Matplotlib to draw percentage labels on slices.
- `pctdistance` (in `plt.pie`) : Controls how far the `autopct` percentage text is placed from the center of the pie.
- `wedgeprops` (in `plt.pie`) : A dictionary of properties for pie wedges; `{'width': x}` creates a donut by reducing slice radius.
- `edgecolor` / `linewidth` (inside `wedgeprops`) : Set wedge border color and border thickness to make slices visually distinct.
- `bbox_inches` (in `plt.savefig`) : When `'tight'`, trims extra whitespace around the saved figure so images are neatly cropped.
- `bbox_to_anchor` (in `plt.legend`) : Positions the legend box relative to the axes using coordinates or tuples (useful to place the legend outside the plot).
- `loc` (in `plt.legend`) : Chooses which corner/edge of the `bbox_to_anchor` the legend should attach to (e.g., `'lower center'`).
- `ncol` (in `plt.legend`) : Sets how many columns the legend should use, useful for compact horizontal legends.