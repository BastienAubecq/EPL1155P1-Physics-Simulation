#Equipe 1155
#PhysicsSimulation : Interface graphique pour simuler le parcours du véhicule sur la pente et sur le sol

from tkinter import *
import tkinter.filedialog
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import json
import os

step = 0.001 
stepPente = 0.001


def simulation():
    """Simule la position (x et y), la vitesse, l'accélération et l'énergie sur la pente et sur le sol
    """
    global t, x, v, a, y, e_cin, e_pot, e_tot, tExpTmp, xExpTmp, yExpTmp, vExpTmp, aExpTmp
    k, m, h, w, kp, g, end = settings["k"], settings["m"], settings["hp"], settings["lp"], settings["kp"], settings["g"], settings["Fin"]

    ## Simulation pente : 
    # Découpage de la pente courbe en une multitude de petites pentes rectilignes
    xPente = np.arange(-w, 0, stepPente)
    yPente = h*np.e**((-3.5*xPente)/w-3.5) #La fonction la plus proche de notre pente
    vxPente = np.zeros_like(xPente)
    vyPente = np.zeros_like(xPente)
    aPente = np.zeros_like(xPente)
    tPente = np.zeros_like(xPente)

    vf = 0
    aPente[0] = g
    angle = np.arctan((yPente[0] - yPente[1]) / (xPente[1] - xPente[0]))

    for i in range(1, len(xPente)):
        #Analyse du petit bout de pente (supposé droit) entre le dernier point et le point actuel
        vi = vf #Vitesse précédente
        dx = np.sqrt((xPente[i]-xPente[i-1])**2+(yPente[i]-yPente[i-1])**2) #Taille du petit bout de pente
        aPente[i] = g * np.sin(angle) - (kp * vi) / m #Norme de l'accélération sur le petit bout de pente (y compris frottements)

        #Résolution d'un MRUA sur le petit bout de pente
        dt = (-vi + np.sqrt(2*aPente[i]*dx + vi**2)) / aPente[i]
        vf = np.sqrt(2*aPente[i]*dx + vi**2)

        tPente[i] = tPente[i-1] + dt

        angle = 0 if i == len(xPente) - 1 else np.arctan((yPente[i] - yPente[i+1]) / (xPente[i+1] - xPente[i])) #Angle du prochain bout de pente

        #Vitesse exprimée dans la direction du prochain bout de pente
        vxPente[i] = vf * np.cos(angle)
        vyPente[i] = - vf * np.sin(angle)
    
    ## Simulation x, v, a sur le sol
    t = np.arange(0, end, step)
    x = np.zeros_like(t)
    v = np.zeros_like(t)
    a = np.zeros_like(t)
    y = np.zeros_like(t)

    #Calcul de la position, vitesse et accélération à chaque instant (avec un dt très petit)
    x[0] = 0
    v[0] = vxPente[-1]
    for i in range(len(t)-1):
        dt = step

        #Calcul du frottement et de l'accélération
        f_frott = -k*v[i] #F = -kv
        a[i] = f_frott/m #F = ma
        
        v[i+1] = v[i] + (a[i] * dt) #Ajout de l'accélération * dt à la vitesse
        x[i+1] = x[i] + (v[i] * dt) #Ajout de la vitesse * dt à la position

    #Rassembler les données de la pente et du sol
    t = np.concatenate((-tPente[-1]+tPente, t))
    x = np.concatenate((xPente, x))
    y = np.concatenate((yPente, y))
    v = np.concatenate((np.sqrt(vxPente**2+vyPente**2), v))
    a = np.concatenate((aPente, a))

    #Energie
    e_pot = m * g * y
    e_cin = m * v**2 / 2
    e_tot = e_pot + e_cin
    
    
    #(Donnees exp)
    tExpTmp = [tExp[i] for i in range(len(tExp)) if tExp[i] <= settings["Fin"]]
    xExpTmp = [xExp[i] for i in range(len(tExp)) if tExp[i] <= settings["Fin"]]
    yExpTmp = [yExp[i] for i in range(len(tExp)) if tExp[i] <= settings["Fin"]]
    vExpTmp = [vExp[i] for i in range(len(tExp)) if tExp[i] <= settings["Fin"]]
    aExpTmp = [aExp[i] for i in range(len(tExp)) if tExp[i] <= settings["Fin"]]


def createPlot(xValues, yValues, labels, subplotArgs, colors, ySymetry):
    """Creates a plot with graphs with specified parameters

    Args:
        xValues (list): A list of numpy arrays with x values
        yValues (list): A list of numpy arrays with y values
        labels (list): A list of strings with the names of the graphs
        subplotArgs (tuple): A tuple containing the arguments for the figure.add_subplot() function
        colors (tuple): A tuple of strings with the colors of the graphs
        ySymetry (bool): Wether the y axis ticks must be symetrical or not

    Returns:
        object (matplotlib.axes._subplots.AxesSubplot): The plot
    """
    #Create sub_plot
    plot = figure.add_subplot(subplotArgs[0], subplotArgs[1], subplotArgs[2])

    #Create graphs
    for i in range(len(labels)):
        plot.plot(xValues[i], yValues[i], label=labels[i], color=colors[i])

    #Set ylim (better than by default)
    max = np.amax(np.array([np.amax(array) for array in yValues]))
    min = np.amin(np.array([np.amin(array) for array in yValues]))
    if ySymetry:
        absMax = abs(max) if abs(max) > abs(min) else abs(min)
        max = absMax
        min = -absMax
    margin = abs(max - min) * 0.05
    plot.set_ylim([min-margin, max+margin])

    #Create y=0 and x=0 lines and a legend
    plot.axhline(y=0, color="k", linewidth=1)
    plot.axvline(x=0, color="k", linewidth=1)
    plot.legend(loc="upper right")

    return plot


def plotMovement(recalculate=True):
    """Draws the graphs for x, v, t
    """
    global plots, currentGraph
    if recalculate:
        currentGraph = "movement"
        updateCheckbuttons((("x(t)", "v(t)"), ("a(t)", "y(t)")))

    #Destroy plots
    for plot in plots:
        plot.remove()
    plots = []
    
    #Create plots
    activeOptions = []
    for option in ("x(t)", "v(t)", "a(t)", "y(t)"):
        if settings["options"][option]:
            activeOptions.append(option)
    if settings["options"]["[Exp]"]: 
        params = {"x(t)": (x, "blue", xExpTmp, "orange", "x[s]"), "v(t)": (v, "red", vExpTmp, "orange", "v[m/s]"), "a(t)": (a, "green", aExpTmp, "orange", "a[m/s²]"), "y(t)": (y, "blue", yExpTmp, "orange", "y[m]")}
    else:
        params = {"x(t)": (x, "blue", "x[s]"), "v(t)": (v, "red", "v[m/s]"), "a(t)": (a, "green", "a[m/s²]"), "y(t)": (y, "blue", "y[m]")}
    for i in range(len(activeOptions)):
        if len(params[activeOptions[i]]) > 3:
            plot = createPlot([t, tExpTmp], [params[activeOptions[i]][0], params[activeOptions[i]][2]], [activeOptions[i], activeOptions[i] + " Exp"], (len(activeOptions), 1, i+1), [params[activeOptions[i]][1], params[activeOptions[i]][3]], True)
        else:
            plot = createPlot([t], [params[activeOptions[i]][0]], [activeOptions[i]], (len(activeOptions), 1, i+1), [params[activeOptions[i]][1]], True)
        plot.set_ylabel(params[activeOptions[i]][-1])
        plots.append(plot)

    #Update canvas
    canvas.draw_idle()
    toolbar.update()


def plotEnergy(recalculate=True):
    """Draws the graphs for the energy
    """
    global plots, currentGraph
    if recalculate:
        currentGraph = "energy"
        updateCheckbuttons((("Ec(t)", "Ep(t)"), ("Et(t)",)))

    #Destroy plots
    for plot in plots:
        plot.remove()
    plots = []

    #Create plot with the 3 graphs
    params = {"Ec(t)": (e_cin, "red"), "Ep(t)": (e_pot, "blue"), "Et(t)": (e_tot, "green")}
    activeOptions = []
    yValues = []
    colors = []
    for option in ("Ec(t)", "Ep(t)", "Et(t)"):
        if settings["options"][option]:
            activeOptions.append(option)
            yValues.append(params[option][0])
            colors.append(params[option][1])
    
    plot = createPlot([t] * len(yValues), yValues, activeOptions, (1, 1, 1), colors, False)
    plot.set_ylabel("E[J]")
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
    filename = "settings.json"
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
    filename = "settings.json"
    with open(filename, "w") as f:
        f.write(json.dumps(dictionary, indent=4))


def updateCheckbuttons(options):
    """Updates the checkbuttons for the options (when switching between movement graphs and energy graphs)

    Args:
        options (tuple): All the options
    """
    global checkButtons, checkButtonsValues
    for button in checkButtons:
        button.destroy()
    checkButtons = []
    checkButtonsValues = []

    for i in range(2):
        for j in range(len(options[i])):
            checkButtonsValues.append(IntVar())
            checkButtons.append(Checkbutton(window, text=options[i][j], font=("Calibri", 12, "bold"), variable=checkButtonsValues[-1], command=lambda id=len(checkButtons): updateActiveGraphs(id)))
            checkButtons[-1].place(x=500+80*i, y=15+28*j, anchor="w")
            if settings["options"][options[i][j]]:
                checkButtonsValues[-1].set(1)
    

def clearEntry(id):
    """Clears an entry's value when we click on it

    Args:
        id (int): The id of the entry
    """
    settingsEntries[id].delete(0, END)

def replot(id):
    """Plot the graphs again when an entry's value changed

    Args:
        id (int): The id of the entry wich changed
    """
    newValue = settingsEntries[id].get()
    try:
        newValue = int(newValue)
    except:
        newValue = float(newValue)
    settings[list(settings.keys())[id]] = newValue
    simulation()
    if currentGraph == "movement":
        plotMovement()
    else:
        plotEnergy()
    save(settings)
    window.focus_set()

def resetSettings():
    """Reset settings to default
    """
    global settings
    settings = defaultSettings
    settingNames = list(settings.keys())
    settingNames.remove("options")
    for i in range(len(settingNames)):
        settingsEntries[i].delete(0, END)
        settingsEntries[i].insert(0, str(settings[settingNames[i]]))
    simulation()
    if currentGraph == "movement":
        plotMovement()
    else:
        plotEnergy()
    save(settings)

def updateActiveGraphs(id):
    """Update active graphs when checkbutton value is changed

    Args:
        id (int): The id of the checkbutton wich changed
    """
    if id == -1:
        settings["options"]["[Exp]"] = False if experimentalButtonValue.get() == 0 else True
    else: 
        settings["options"][checkButtons[id].cget("text")] = False if checkButtonsValues[id].get() == 0 else True
    if currentGraph == "movement":
        plotMovement(False)
    else:
        plotEnergy(False)
    save(settings)

def export():
    """Asks the user to choose a file to export the theoretical data to
    """
    filename = tkinter.filedialog.asksaveasfilename(initialdir=os.getcwd(), defaultextension=".txt", filetypes=(("Text files", "*.txt"),))
    if filename != "":
        if not filename.endswith(".txt"):
            filename += ".txt"
        np.savetxt(filename, np.array((t, x, y, v, a)).T)

#Get settings and declare simulation variables
defaultSettings = {"m": 0.5, "k": 0.22, "kp": 0, "Fin": 20, "hp": 1, "lp": 0.55, "g": 9.81, "options": {"[Exp]": False, "x(t)": True, "v(t)": True, "a(t)": True, "y(t)": False, "Ec(t)": True, "Ep(t)": True, "Et(t)": True}}
settings = load(defaultSettings)
t, x, v, a, y, e_cin, e_pot, e_tot = None, None, None, None, None, None, None, None

#Read experimental data
#(Experimental data were taken with tracker with those parameters : m=0.382, l=0.5, h=1, g=9.81, kp=0.3, k=0.1)
#(^Try the program with those settings, it looks perfect :) )
try:
    (tExp, xExp, yExp, vExp, aExp) = np.loadtxt("experimentalData.txt").T
except FileNotFoundError:
    print("Error: experimentalData.txt is missing.")
    tExp, xExp, yExp, vExp, aExp = np.array((0,)), np.array((0,)), np.array((0,)), np.array((0,)), np.array((0,))
tExpTmp, xExpTmp, yExpTmp, vExpTmp, aExpTmp = None, None, None, None, None

simulation() #Simulate

#Setting window and buttons
window = Tk()
window.title("Simulation physique")
window.geometry("800x610")

#Setting up bar (buttons)
plotMovementButton = Button(window, command=plotMovement, text="Mouvement", bd=3, font=("Calibri", 12, "bold"), background="blue", activebackground="dark blue")
plotMovementButton.place(x=290, y=30, anchor="e")
plotEnergyButton = Button(window, command=plotEnergy, text="Energie", bd=3, font=("Calibri", 12, "bold"), background="green", activebackground="dark green")
plotEnergyButton.place(x=310, y=30, anchor="w")
experimentalButtonValue = IntVar()
experimentalButton = Checkbutton(window, command=lambda: updateActiveGraphs(-1), text="Données exp.", font=("Calibri", 12, "bold"), variable=experimentalButtonValue)
experimentalButton.place(x=7, y=30, anchor="w")
if settings["options"]["[Exp]"]:
    experimentalButtonValue.set(1)
checkButtons = []
checkButtonsValues = []

#Setting settings frame
settingsFrame = Frame(width=180, height=504, bd=2, relief=RIDGE)
settingsFrame.place(x=703, y=309, anchor=CENTER)
Label(settingsFrame, text="Paramètres :", font=("Calibri", 18, "bold")).place(x=8, y=20, anchor="w")
Button(settingsFrame, text="Reset", command=resetSettings, bd=3, background="red", activebackground= "dark red", font=("Calibri", 12, "bold")).place(x=8, y=480, anchor="w")
Button(settingsFrame, text="Exporter", command=export, bd=3, background="yellow", activebackground= "gold", font=("Calibri", 12, "bold")).place(x=172, y=480, anchor="e")
settingsEntries = []
settingNames = list(settings.keys())
settingNames.remove("options")
settingsUnits = {"m": "[kg]", "k": "[kg/s]", "kp": "[kg/s]", "Fin": "[s]", "hp": "[m]", "lp": "[m]", "g": "[m/s²]"}
for i in range(len(settingNames)):
    l = Label(settingsFrame, text=settingNames[i] + " = ", font=("Calibri", 15, "bold"))
    l.place(x=12, y=60+40*i, anchor="w")
    window.update()
    settingsEntries.append(Entry(settingsFrame, width=5, background="white", relief=GROOVE, bd=2, font=("Calibri", 15, "bold")))
    settingsEntries[i].insert(0, str(settings[settingNames[i]]))
    settingsEntries[i].place(x=12+l.winfo_width(), y=60+40*i, anchor="w")
    settingsEntries[i].bind("<Button-1>", lambda event, id=i: clearEntry(id))
    settingsEntries[i].bind("<Return>", lambda event, id=i: replot(id))
    Label(settingsFrame, text=settingsUnits[settingNames[i]], font=("Calibri", 14, "bold")).place(x=68+l.winfo_width(), y=60+40*i, anchor="w")

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

currentGraph = ""
plotMovement()
window.mainloop()
