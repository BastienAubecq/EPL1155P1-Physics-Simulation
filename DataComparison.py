#Equipe 1155
#DataComparison : Interface graphique pour comparer des données de plusieurs fichiers textes

from tkinter import *
import tkinter.filedialog
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import json
import os


def createPlot(xValues, yValues, subplotArgs, colors, legend):
    """Creates a plot with graphs with specified parameters

    Args:
        xValues (list): A list of numpy arrays with x values
        yValues (list): A list of numpy arrays with y values
        subplotArgs (tuple): A tuple containing the arguments for the figure.add_subplot() function
        colors (tuple): A tuple of strings with the colors of the graphs
        legend (string): The legend

    Returns:
        object (matplotlib.axes._subplots.AxesSubplot): The plot
    """
    #Create sub_plot
    plot = figure.add_subplot(subplotArgs[0], subplotArgs[1], subplotArgs[2])

    #Create graphs
    for i in range(len(xValues)):
        plot.plot(xValues[i], yValues[i], color=colors[i])

    #Set ylim (better than by default)
    max = np.amax(np.array([np.amax(array) for array in yValues]))
    min = np.amin(np.array([np.amin(array) for array in yValues]))
    absMax = abs(max) if abs(max) > abs(min) else abs(min)
    max = absMax
    min = -absMax
    margin = abs(max - min) * 0.05
    plot.set_ylim([min-margin, max+margin])

    #Create y=0 and x=0 lines and a legend
    plot.axhline(y=0, color="k", linewidth=1)
    plot.axvline(x=0, color="k", linewidth=1)
    plot.text(0.99, 0.97, legend, ha='right', va='top', transform=plot.transAxes)
    return plot


def plotMovement():
    """Draws the graphs for x, v, t
    """
    global plots

    #Destroy plots
    for plot in plots:
        plot.remove()
    plots = []
    
    #Create plots
    x = []
    y = []
    legends = ["x(t)", "y(t)", "v(t)", "a(t)"]
    ylabels = ["x[m]", "y[m]", "v[m/s]", "a[m/s²]"]
    currentLegends = []
    currentYLabels = []
    for i in range(4):
        if settings["options"][i]:
            x.append([])
            y.append([])
            currentLegends.append(legends[i])
            currentYLabels.append(ylabels[i])
            for j in range(len(data)):
                x[-1].append(data[j][0])
                y[-1].append(data[j][i+1])

    
    if(len(data) > 0):
        for i in range(len(x)):
            plot = createPlot(x[i], y[i], (len(x), 1, i+1), colors, currentLegends[i])
            plot.set_ylabel(currentYLabels[i])
            plots.append(plot)
    
    #Update canvas
    canvas.draw_idle()
    toolbar.update()


def load(dictionary):
    """Tries to load settings3.json. If it doesn't exist, create it with the default settings.

    Args:
        dictionary (dict): The default settings

    Returns:
        dict: The dictionary contained in settings3.json if it existed. Else, the default settings.
    """
    filename = "settings2.json"
    try:
        with open(filename, "r") as f:
            dictionary = json.loads(f.read())
    except FileNotFoundError:
        save(dictionary)
    return dictionary

def save(dictionary):
    """Saves current settings in settings3.json

    Args:
        dictionary (dict): The settings to save
    """
    filename = "settings2.json"
    with open(filename, "w") as f:
        f.write(json.dumps(dictionary, indent=4))
    

def updateActiveGraphs(id): #
    """Updates active graphs when checkbutton value is changed

    Args:
        id (int): The id of the checkbutton that was changed
    """
    settings["options"][id] = False if checkButtonsValues[id].get() == 0 else True
    save(settings)
    plotMovement()

def addFile():
    """Asks the user to select a file to add the the data comparison
    """
    file = tkinter.filedialog.askopenfilename(initialdir=os.getcwd())
    if file != "" and len(leftColors) > 0:
        with open(file, "r") as f:
            data.append(np.array(np.loadtxt(file).T))
        colors.append(leftColors[0])
        del leftColors[0]
        settings["openedFiles"].append(file)
        save(settings)
        filesTexts.append(Label(settingsFrame, foreground=colors[-1], text=file.split("/")[-1], font=("Calibri", 12)))
        filesTexts[-1].place(x=8, y=60+40*(len(data)-1), anchor="w")
        removeButtons.append(Button(settingsFrame, text=" x ", command=lambda id=(len(data)-1): removeFile(id), font=("Calibri", 12, "bold"), background="red", activebackground="dark red"))
        removeButtons[-1].place(x=245, y=60+40*(len(data)-1), anchor="e")
        plotMovement()

def removeFile(id):
    """Removes a file from the data comparison

    Args:
        id (int): The id of the file to remove
    """
    del settings["openedFiles"][id]
    save(settings)
    del data[id]
    filesTexts[id].destroy()
    del filesTexts[id]
    removeButtons[id].destroy()
    del removeButtons[id]
    leftColors.append(colors[id])
    del colors[id]
    for i in range(id, len(filesTexts)):
        filesTexts[i].place(x=8, y=60+40*i, anchor="w")
        removeButtons[i].configure(command=lambda id=i:removeFile(id))
        removeButtons[i].place(x=245, y=60+40*i, anchor="e")
    plotMovement()

def removeAllFiles():
    """Removes all files from the data comparison
    """
    global leftColors, colors, data, filesTexts, removeButtons
    settings["openedFiles"] = []
    save(settings)
    data = []
    for i in range(len(filesTexts)):
        filesTexts[i].destroy()
        removeButtons[i].destroy()
    filesTexts = []
    removeButtons = []
    leftColors = ["blue", "green", "red", "yellow", "orange"]
    colors = []
    plotMovement()


#Get settings
defaultSettings = {"openedFiles": [], "options": [True, False, True, True]}
settings = load(defaultSettings)

try:
    (tExp, xExp, yExp, vExp, aExp) = np.loadtxt("experimentalData.txt").T
except FileNotFoundError:
    print("Error: experimentalData.txt is missing.")
    tExp, xExp, yExp, vExp, aExp = np.array((0,)), np.array((0,)), np.array((0,)), np.array((0,)), np.array((0,))

#Setting window and buttons
window = Tk()
window.title("Comparaison données physiques")
window.geometry("870x610")

#Setting up bar (CheckButtons)
optionsName = ("x(t)", "y(t)", "v(t)", "a(t)")
checkButtons = []
checkButtonsValues = []
for i in range(4):
    checkButtonsValues.append(IntVar())
    checkButtons.append(Checkbutton(window, text=optionsName[i], font=("Calibri", 12, "bold"), variable=checkButtonsValues[-1], command=lambda id=len(checkButtons): updateActiveGraphs(id)))
    checkButtons[-1].place(x=(620/5)*(i+1), y=30, anchor=CENTER)
    if settings["options"][i]:
        checkButtonsValues[-1].set(1)

#Setting files frame
settingsFrame = Frame(width=250, height=504, bd=2, relief=RIDGE)
settingsFrame.place(x=738, y=309, anchor=CENTER)
Label(settingsFrame, text="Fichiers :", font=("Calibri", 18, "bold")).place(x=5, y=20, anchor="w")
Button(settingsFrame, text="Ajouter", command=addFile, bd=3, background="yellow", activebackground= "gold", font=("Calibri", 12, "bold")).place(x=8, y=480, anchor="w")
Button(settingsFrame, text="Retirer tout", command=removeAllFiles, bd=3, background="red", activebackground= "dark red", font=("Calibri", 12, "bold")).place(x=242, y=480, anchor="e")
data = []
filesTexts = []
removeButtons = []
colors = []
leftColors = ["blue", "green", "red", "yellow", "orange"]
for i in range(len(settings["openedFiles"])):
    if len(leftColors) == 0: break
    with open(settings["openedFiles"][i], "r") as f:
        colors.append(leftColors[0])
        del leftColors[0]
        data.append(np.array(np.loadtxt(settings["openedFiles"][i]).T))
        filesTexts.append(Label(settingsFrame, text=settings["openedFiles"][i].split("/")[-1], foreground=colors[-1], font=("Calibri", 12)))
        filesTexts[-1].place(x=8, y=60+40*i, anchor="w")
        removeButtons.append(Button(settingsFrame, text=" x ", command=lambda id=i:removeFile(id), font=("Calibri", 12, "bold"), background="red", activebackground="dark red"))
        removeButtons[-1].place(x=245, y=60+40*i, anchor="e")

#Setting Matplotlib canvas and toolbar
figure = Figure(figsize = (6, 5), dpi = 100)
figure.subplots_adjust(top=0.95, bottom=0.12, left=0.12, right=0.95, hspace=0.5)
figure.supxlabel("t[s] ; t=0 : fin de la pente")
plots = []

canvas = FigureCanvasTkAgg(figure)
canvas.get_tk_widget().configure(bd=2, relief=GROOVE)
canvas.get_tk_widget().place(x=307, y=310, anchor=CENTER)

toolbar = NavigationToolbar2Tk(canvas, window)
toolbar.update()
toolbar.pack(side=BOTTOM, padx=5, pady=3)

plotMovement()
window.mainloop()