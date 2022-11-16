from tkinter import *
import tkinter.filedialog
from PIL import Image, ImageTk
import numpy as np
from scipy.optimize import curve_fit
import json
import os

tmp = None

def load(dictionary):
    """Tries to load settings3.json. If it doesn't exist, create it with the default settings.

    Args:
        dictionary (dict): The default settings

    Returns:
        dict: The dictionary contained in settings3.json if it existed. Else, the default settings.
    """
    filename = "settings3.json"
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
    filename = "settings3.json"
    with open(filename, "w") as f:
        f.write(json.dumps(dictionary, indent=4))


class CoordinateSystemConverter:
    """Create a coordinate system converter"""
    
    def __init__(self, A1, A2, B1, B2):
        """Initialize the coordinate system converter

        Args:
            A1 (tuple): First Point in current coordinate system
            A2 (tuple): First Point in new coordinate system
            B1 (tuple): Second Point in current coordinate system
            B2 (tuple): Second Point in new coordinate system
        """
        a1 = complex(A1[0], A1[1])
        b1 = complex(B1[0], B1[1])
        a2 = complex(A2[0], A2[1])
        b2 = complex(B2[0], B2[1])
        self.z1 = (a2-b2)/(a1-b1)
        self.z2 = (a1*b2 - a2*b1)/(a1-b1)
    
    def convert(self,P):
        """Converts a point in its current coordinate system into the new one based one the points given in initialization

        Args:
            P (tuple): The point to convert in the new coordinate system

        Returns:
            tuple: Coordinates of the same point in the new coordinate system
        """
        p1 = complex(P[0], P[1])
        p2 = self.z1*p1 + self.z2
        return (p2.real, p2.imag)


def buildCoordinateConverters():
    """Create two coordinate system converters to be able to convert from user coordinates to pixel coordinates and the other way around
    """
    global tkinterToUser, userToTkinter
    tkinterToUser = CoordinateSystemConverter(
        (settings["coord1"][0], canvasHeight-settings["coord1"][1]), 
        (settings["coord1"][2], settings["coord1"][3]),
        (settings["coord2"][0], canvasHeight-settings["coord2"][1]), 
        (settings["coord2"][2], settings["coord2"][3]))
    userToTkinter = CoordinateSystemConverter(
        (settings["coord1"][2], settings["coord1"][3]), 
        (settings["coord1"][0], canvasHeight-settings["coord1"][1]), 
        (settings["coord2"][2], settings["coord2"][3]), 
        (settings["coord2"][0], canvasHeight-settings["coord2"][1]))


def curve_fitting(points: list, **kwargs):
    """Find the best curve fit of a list of points

    Args:
        points (list): List of points to find the equation
        **kwargs : deg= degree_of_the_polynomial if you want a polynomial equation or exp=True if you want an exponential equation
                   oddTerms=True if you want odd power terms in your polynomial equation
    
    Returns:
        (string, list): (expression of the function, list of points)
    """
    keys = kwargs.keys()

    x_data = [float(i[0]) for i in points]
    y_data = [float(i[1]) for i in points]

    #Sort both list based on x values by ascending order
    zipped_lists = zip(x_data, y_data)
    sorted_pairs = sorted(zipped_lists)
    tuples = zip(*sorted_pairs)
    x_data, y_data = [ list(tuple) for tuple in  tuples]

    interval = (x_data[0] - (x_data[-1]-x_data[0])/20, x_data[-1] + (x_data[-1]-x_data[0])/20)
    if "interval" in keys:
        interval = kwargs["interval"]

    if 'exp' in keys and kwargs['exp']: #Exponential curve
        for i in range(len(y_data)): #Set the negative y values to 0.001 (to be able to apply the log)
            if y_data[i] <= 0:
                y_data[i] = 0.001
        exponential_equation = lambda x, a, b: a*x+b
        coefficients = curve_fit(exponential_equation, x_data, np.log(y_data), maxfev=5000)[0] #Use SciPy to find the best curve
        a, b = coefficients[0],coefficients[1]

        normal = "xEe0123456789+-()."
        super_s = "ˣᴱᵉ⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁽⁾·"
        res = f'({round(a,2)}x + {round(b,2)})'.maketrans(''.join(normal), ''.join(super_s)) #Make the expression
        return ( #Return the expression and a list of points to draw the function
            f'e' + f'{round(a,2)}x + {round(b,2)}'.translate(res).replace(' ⁺ ⁻', ' ⁻ '), 
            [(i, np.exp(a*i + b)) for i in np.arange(interval[0], interval[1]+(interval[1]-interval[0])/50, (interval[1]-interval[0])/50)]
        )
    
    elif 'deg' in keys: #Polynomial curve
        deg = kwargs['deg']
        odd = True
        if 'oddTerms' in kwargs:
            odd = kwargs['oddTerms']
        coefficients = curve_fit(polynomialBuilder(deg, odd), x_data, y_data, maxfev=5000)[0] #Use SciPy to find the best curve

        normal = "0123456789"
        super_s = "⁰¹²³⁴⁵⁶⁷⁸⁹"
        length = len(coefficients)
        #Create y(x) to be able to create a list of points to draw the function
        pow = 1
        if odd:
            y = lambda x: sum([coefficients[i]*(x**i) for i in range(length)])
            pow = 1
        else:
            y = lambda x: sum([coefficients[i]*(x**(2*i)) for i in range(length)])
            pow = 2
        #Make the expression
        expression = "".join([(str(round(coefficients[length - i - 1], 2))+ 'x' + f'{(length - i - 1)*pow}'.translate(f'{length - i - 1}'.maketrans(''.join(normal), ''.join(super_s))) + ' + ') for i in range(length)]).replace(' + -',' - ')[:-5]
        return ( #Return the expression and the list of points
            expression, 
            [(i, y(i)) for i in np.arange(interval[0], interval[1]+(interval[1]-interval[0])/50, (interval[1]-interval[0])/50)]
        )

def polynomialBuilder(degree, oddTerms=True):
    """Generates a polynomial function with given degree

    Args:
        degree (int): The degree of the polynomial
        oddTerms (bool, optional): Wether or not the polynomial includes odd exponents terms. Defaults to True.

    Returns:
        _type_: _description_
    """
    parameters = ",".join(f"c{i}" for i in range(degree+1) if oddTerms or i%2 == 0)
    result = "+".join(f"c{i}*x**{i}" for i in range(degree+1) if oddTerms or i%2 == 0)
    return eval(f"lambda x,{parameters}: {result}")


def getImage(filename, xMax, yMax):
    """Resizes the image to fit the canvas

    Args:
        filename (string): The path to the image
        xMax (int): The max x size of the resized image
        yMax (int): The max y size of the resized image

    Returns:
        PhotoImage: The image's PhotoImage for Tkinter
    """
    global tmp
    im = Image.open(filename)
    w, h = im.size
    ratio = w / h
    if ratio > xMax / yMax:
        resized_image = im.resize((int(xMax), int(xMax / ratio)))
    else:
        resized_image = im.resize((int(yMax * ratio), int(yMax)))

    tmp = ImageTk.PhotoImage(resized_image)
    return tmp


def openImage():
    """Asks the user to select an image and open it
    """
    global image
    file = tkinter.filedialog.askopenfilename(initialdir=os.getcwd())
    if file != "":
        if image != None:
            canvas.delete(image)
        try:
            image = canvas.create_image(450, canvasHeight/2, image=getImage(file, 900, canvasHeight))
            canvas.tag_lower(image)
            settings["file"] = file
            save(settings)
        except:
            print("Error when opening image.")


def updateFunction():
    """Updates the function when something changes
    """
    global functionLines, xAxis, yAxis
    corners = np.matrix(( #Corners of canvas in user coordinates
        tkinterToUser.convert((0, 0)), 
        tkinterToUser.convert((900, 0)), 
        tkinterToUser.convert((0, canvasHeight)), 
        tkinterToUser.convert((900, canvasHeight))
    )).T
    if (settings["function"] == "polynomial" and len(pointsUserCoordinates) > settings["polynomialDegree"]) or (settings["function"] == "exponential" and len(pointsUserCoordinates) > 2):
        if settings["maxInterval"] == 1:
            #Find the best curve and ask points on the whole canvas
            (expression, functionPoints) = curve_fitting(pointsUserCoordinates, deg=settings["polynomialDegree"], oddTerms=settings["polynomialOddTerms"], exp=settings["function"]=="exponential", interval=(np.min(corners[0]), np.max(corners[0])))
        else:
            #Find the best curve
            (expression, functionPoints) = curve_fitting(pointsUserCoordinates, deg=settings["polynomialDegree"], oddTerms=settings["polynomialOddTerms"], exp=settings["function"]=="exponential")
        
        #Update the expression text
        lines = []
        while len(expression) > 21:
            lines.append(expression[:21])
            expression = expression[21:]
        lines.append(expression)
        expression = "\n".join(lines)
        functionText.configure(text=expression)
        window.update()
        maxIntervalButton.place(x=5, y=196+functionText.winfo_height(), anchor="w")
        showAxisButton.place(x=5, y=226+functionText.winfo_height(), anchor="w")
        showCoordinatesButton.place(x=5, y=256+functionText.winfo_height(), anchor="w")

        #Redraw the function
        for line in functionLines:
            canvas.delete(line)
        functionLines = []
        functionPoints = [userToTkinter.convert(point) for point in functionPoints]
        for i in range(1, len(functionPoints)):
            functionLines.append(canvas.create_line(functionPoints[i-1][0], canvasHeight-functionPoints[i-1][1], functionPoints[i][0], canvasHeight-functionPoints[i][1], fill="green", width=4))
    else:
        #Delete function
        functionText.configure(text="y = /")
        maxIntervalButton.place(x=5, y=225, anchor="w")
        showAxisButton.place(x=5, y=255, anchor="w")
        showCoordinatesButton.place(x=5, y=285, anchor="w")
        for line in functionLines:
            canvas.delete(line)
    
    #Update axis
    if settings["showAxis"] == 1:
        xMin = userToTkinter.convert((np.min(corners[0]), 0))
        xMax = userToTkinter.convert((np.max(corners[0]), 0))
        yMin = userToTkinter.convert((0, np.min(corners[1])))
        yMax = userToTkinter.convert((0, np.max(corners[1])))
        canvas.coords(xAxis, xMin[0], canvasHeight-xMin[1], xMax[0], canvasHeight-xMax[1])
        canvas.coords(yAxis, yMin[0], canvasHeight-yMin[1], yMax[0], canvasHeight-yMax[1])
    else:
        canvas.coords(xAxis, -5, -5, -5, -5)
        canvas.coords(yAxis, -5, -5, -5, -5)


def updateFunctionType():
    """Updates the function type (exponential or polynomial)
    """
    settings["function"] = functionType.get()
    updateFunction()
    save(settings)


def updateOddTerms():
    """Updates wether odd terms are included or not in the polynomial
    """
    settings["polynomialOddTerms"] = oddTerms.get()
    settings["function"] = "polynomial"
    functionType.set("polynomial")
    updateFunction()
    save(settings)


def updateMaxInterval():
    """Updates wether or not the function is drawn on the whole canvas
    """
    settings["maxInterval"] = maxInterval.get()
    updateFunction()
    save(settings)


def updateShowAxis():
    """Updates wether or not axis are shown
    """
    settings["showAxis"] = showAxis.get()
    updateFunction()
    save(settings)


def clearEntry(entry):
    """Clears the entry when we click on it ; Selects the corresponding action

    Args:
        entry (Entry): The entry
    """
    entry.delete(0, END)
    if entry == coord1X or entry == coord1Y:
        currentAction.set("coord1")
    elif entry == coord2X or entry == coord2Y:
        currentAction.set("coord2")
    elif entry == degree:
        functionType.set("polynomial")
        updateFunctionType()


def updateEntry(entry):
    """Tries to update everything when an entry's value changes ; Rollback to the old value if it fails

    Args:
        entry (Entry): The entry
    """
    window.focus_set()
    #Try to update the function
    try:
        #Get old value in settings and set settings to new value
        if entry == coord1X:
            oldValue = settings["coord1"][2]
            settings["coord1"][2] = float(entry.get())
        elif entry == coord1Y:
            oldValue = settings["coord1"][3]
            settings["coord1"][3] = float(entry.get())
        elif entry == coord2X:
            oldValue = settings["coord2"][2]
            settings["coord2"][2] = float(entry.get())
        elif entry == coord2Y:
            oldValue = settings["coord2"][3]
            settings["coord2"][3] = float(entry.get())
        elif entry == degree:
            oldValue = settings["polynomialDegree"]
            settings["polynomialDegree"] = int(entry.get())

        #Update the function and the points coordinates and then save the new settings
        if entry == coord1X or entry == coord1Y or entry == coord2X or entry == coord2Y:
            buildCoordinateConverters()
            updateText(coord1Point, coord1Text)
            updateText(coord2Point, coord2Text)
            for i in range(len(points)):
                updateText(points[i], texts[i])
        updateFunction()
        save(settings)

    except:
        #If it failed : rollback to the old value
        if entry == coord1X:
            settings["coord1"][2] = oldValue
        elif entry == coord1Y:
            settings["coord1"][3] = oldValue
        elif entry == coord2X:
            settings["coord2"][2] = oldValue
        elif entry == coord2Y:
            settings["coord2"][3] = oldValue
        elif entry == degree:
            settings["polynomialDegree"] = oldValue
        entry.delete(0, END)
        entry.insert(0, oldValue)


def updateCursor():
    """Updates the mouse's cursor for the canvas depending on the current action
    """
    canvas.configure(cursor={"coord1": "exchange DarkOrange1", "coord2": "exchange DarkOrange1", "point": "dot blue", "remove": "X_cursor red"}[currentAction.get()])


def onMouseClick(event):
    """Executed when we click on the canvas
    """
    action = currentAction.get()
    if action == "coord1" or action == "coord2":
        oldValue = settings[action]
        settings[action] = [event.x, event.y, oldValue[2], oldValue[3]]
        try: #Try to update everything
            #Update the function and the points coordinates and then save the new settings
            buildCoordinateConverters()
            for i in range(len(points)):
                updateText(points[i], texts[i])
            updateFunction()
            canvas.coords(coord1Point, settings["coord1"][0]-10, settings["coord1"][1]-10, settings["coord1"][0]+10, settings["coord1"][1]+10)
            canvas.coords(coord2Point, settings["coord2"][0]-10, settings["coord2"][1]-10, settings["coord2"][0]+10, settings["coord2"][1]+10)
            canvas.coords(coord1Text, settings["coord1"][0]+10, settings["coord1"][1]-4)
            canvas.coords(coord2Text, settings["coord2"][0]+10, settings["coord2"][1]-4)
            updateText(coord1Point, coord1Text)
            updateText(coord2Point, coord2Text)
            save(settings)
        except: #If it failed : rollback to the old value
            settings[action] = oldValue

    elif action == "point": #Adds a point to the canvas
        (point, text, coordinates) = drawPoint(event.x, event.y, "blue", 8)
        points.append(point)
        texts.append(text)
        pointsUserCoordinates.append(coordinates)
        updateFunction()
        settings["points"].append([event.x, event.y])
        save(settings)

    elif action == "remove": #Removes a point from the canvas if there is one where the user clicked
        for i in range(len(points)):
            coords = canvas.coords(points[i])
            if coords[0] <= event.x <= coords[2] and coords[1] <= event.y <= coords[3]:
                canvas.delete(points[i])
                canvas.delete(texts[i])
                del points[i], texts[i], pointsUserCoordinates[i]
                updateFunction()
                for j in range(len(settings["points"])):
                    if settings["points"][j][0] == (coords[0]+coords[2])/2 and settings["points"][j][1] == (coords[1]+coords[3])/2:
                        del settings["points"][j]
                        break
                save(settings)
                break


def removeAllPoints():
    """Removes all blue points placed on the canvas
    """
    global points, texts, pointsUserCoordinates, functionLines
    for i in range(len(points)):
        canvas.delete(points[i])
        canvas.delete(texts[i])
    for line in functionLines:
        canvas.delete(line)
    functionText.configure(text="y = /")
    points = []
    texts = []
    pointsUserCoordinates = []
    functionLines = []
    settings["points"] = []
    save(settings)


def updateShowCoordinates():
    """Show/hide all of the points coordinates
    """
    settings["coordinates"] = showCoordinates.get()
    updateText(coord1Point, coord1Text)
    updateText(coord2Point, coord2Text)
    for i in range(len(points)):
        updateText(points[i], texts[i])
    

def drawPoint(x, y, color, size): 
    """Draws a point at given coordinates with given color and size in the canvas with the coordinates text if activated in settings

    Args:
        x (int): x coordinate in canvas coordinates system
        y (int): y coordinate in canvas coordinates system
        color (string): the point's color
        size (int): the radius of the point

    Returns:
        (object, object, (float, float)): (the circle object, the text object, the x and y coordinates in user coordinates system)
    """
    circle = canvas.create_oval(x-size, y-size, x+size, y+size, outline=color, fill=color)
    userCoordinates = tkinterToUser.convert((x, canvasHeight-y))
    text = canvas.create_text(x+size, y-size+6, text="", fill=color, font=("Calibri", 14), anchor="sw")
    updateText(circle, text)
    return (circle, text, userCoordinates)


def updateText(point, text):
    """Update a point's coordinates text.

    Args:
        point (object): The point
        text (object): The text
    """
    coords = canvas.coords(point)
    coords = tkinterToUser.convert(((coords[0] + coords[2]) / 2, canvasHeight - (coords[1] + coords[3]) / 2))
    for i in range(len(pointsUserCoordinates)):
        if points[i] == point:
            pointsUserCoordinates[i] = (round(coords[0], 2), round(coords[1], 2))
            break
    if settings["coordinates"] == 1:
        canvas.itemconfigure(text, text=f"({round(coords[0], 2)};{round(coords[1], 2)})")
    else:
        canvas.itemconfigure(text, text="")


### Main program ###

#Create window
window = Tk()
canvasHeight = window.winfo_screenheight() - 150
window.title("Function finder")
window.geometry(f"1100x{50+canvasHeight}+0+0")

#Get settings
defaultSettings = {"file": "", "function": "polynomial", "polynomialDegree": 2, "polynomialOddTerms": 1, "points": [], "coord1": [12, canvasHeight-12, 0, 0], "coord2": [112, canvasHeight-12, 1, 0], "coordinates": 1, "maxInterval": 0, "showAxis": 0}
settings = load(defaultSettings)

#Create the coordinates converters
tkinterToUser, userToTkinter = None, None
buildCoordinateConverters()


## Create canvas
canvas = Canvas(width=900, height=canvasHeight, cursor="exchange DarkOrange1", background="white")
canvas.place(x=450, y=canvasHeight/2+50, anchor=CENTER)
canvas.bind("<Button-1>", onMouseClick)

#Show image
image = None
if settings["file"] != "":
    try:
        image = canvas.create_image(450, canvasHeight/2, image=getImage(settings["file"], 900, canvasHeight))
        canvas.tag_lower(image)
    except:
        print("Error when opening image.")

points = [] #List containing all blue points objects
texts = [] #List containing all texts (coordinates of the points) objects
pointsUserCoordinates = [] #List containing the coordinates (in user coordinate system) of all blue points

#Set reference coordinates
(coord1Point, coord1Text, _) = drawPoint(settings["coord1"][0], settings["coord1"][1], "DarkOrange1", 10)
(coord2Point, coord2Text, _) = drawPoint(settings["coord2"][0], settings["coord2"][1], "DarkOrange1", 10)

#Set points
for point in settings["points"]:
    (point, text, coordinates) = drawPoint(point[0], point[1], "blue", 8)
    points.append(point)
    texts.append(text)
    pointsUserCoordinates.append(coordinates)


## Top frame
topFrame = Frame(width=888, height=45, bd=2, relief=GROOVE)
topFrame.place(x=8, y=25, anchor="w")

#Reference coordinate 1
currentAction = StringVar(value="coord1")
coord1Button = Radiobutton(topFrame, text="Coord. 1 (", value="coord1", variable=currentAction, command=updateCursor, foreground="DarkOrange1", activeforeground="DarkOrange1", font=("Calibri", 12, "bold"))
coord1Button.place(x=5, y=22, anchor="w")
coord1X = Entry(topFrame, width=4, font=("Calibri", 12, "bold"))
coord1X.place(x=97, y=22, anchor="w")
coord1X.insert(0, settings["coord1"][2])
coord1X.bind("<Button-1>", lambda event: clearEntry(coord1X))
coord1X.bind("<Return>", lambda event: updateEntry(coord1X))
Label(topFrame, text=";", foreground="DarkOrange1", font=("Calibri", 12, "bold")).place(x=133, y=22, anchor="w")
coord1Y = Entry(topFrame, width=4, font=("Calibri", 12, "bold"))
coord1Y.place(x=143, y=22, anchor="w")
coord1Y.insert(0, settings["coord1"][3])
coord1Y.bind("<Button-1>", lambda event: clearEntry(coord1Y))
coord1Y.bind("<Return>", lambda event: updateEntry(coord1Y))
Label(topFrame, text=")", foreground="DarkOrange1", font=("Calibri", 12, "bold")).place(x=179, y=22, anchor="w")

#Reference coordinate 2
coord2Button = Radiobutton(topFrame, text="Coord. 2 (", value="coord2", variable=currentAction, command=updateCursor, foreground="DarkOrange1", activeforeground="DarkOrange1", font=("Calibri", 12, "bold"))
coord2Button.place(x=215, y=22, anchor="w")
coord2X = Entry(topFrame, width=4, font=("Calibri", 12, "bold"))
coord2X.place(x=307, y=22, anchor="w")
coord2X.insert(0, settings["coord2"][2])
coord2X.bind("<Button-1>", lambda event: clearEntry(coord2X))
coord2X.bind("<Return>", lambda event: updateEntry(coord2X))
Label(topFrame, text=";", foreground="DarkOrange1", font=("Calibri", 12, "bold")).place(x=343, y=22, anchor="w")
coord2Y = Entry(topFrame, width=4, font=("Calibri", 12, "bold"))
coord2Y.place(x=353, y=22, anchor="w")
coord2Y.insert(0, settings["coord2"][3])
coord2Y.bind("<Button-1>", lambda event: clearEntry(coord2Y))
coord2Y.bind("<Return>", lambda event: updateEntry(coord2Y))
Label(topFrame, text=")", foreground="DarkOrange1", font=("Calibri", 12, "bold")).place(x=389, y=22, anchor="w")

#Other options
addPointButton = Radiobutton(topFrame, text="Ajouter points", value="point", variable=currentAction, command=updateCursor, foreground="blue", activeforeground="blue", font=("Calibri", 12, "bold"))
addPointButton.place(x=425, y=22, anchor="w")
removePointButton = Radiobutton(topFrame, text="Retirer points", value="remove", variable=currentAction, command=updateCursor, foreground="red", activeforeground="red", font=("Calibri", 12, "bold"))
removePointButton.place(x=589, y=22, anchor="w")
removeAllPointsButton = Button(topFrame, text="Retirer tout", command=removeAllPoints, bd=2, relief=RAISED, background="red", activebackground="red", font=("Calibri", 12, "bold"))
removeAllPointsButton.place(x=770, y=20, anchor="w")


## Left frame
leftFrame = Frame(width=190, height=canvasHeight-10, bd=2, relief=GROOVE)
leftFrame.place(x=1000, y=canvasHeight/2+47, anchor=CENTER)
Button(text="Ouvrir image", command=openImage, background="yellow", activebackground="gold", bd=3, relief=RAISED, font=("Calibri", 12, "bold")).place(x=1000, y=25, anchor=CENTER)
Label(leftFrame, text="Fonction :", font=("Calibri", 18, "bold")).place(x=8, y=20, anchor="w")

#Function type
functionType = StringVar(value=settings["function"])
Radiobutton(leftFrame, text="Polynome", value="polynomial", variable=functionType, command=updateFunctionType, font=("Calibri", 14, "bold")).place(x=8, y=55, anchor="w")
Label(leftFrame, text="Degré : ", font=("Calibri", 13, "bold")).place(x=31, y=80, anchor="w")
degree = Entry(leftFrame, width=2, font=("Calibri", 13, "bold"))
degree.place(x=93, y=80, anchor="w")
degree.insert(0, settings["polynomialDegree"])
degree.bind("<Button-1>", lambda event: clearEntry(degree))
degree.bind("<Return>", lambda event: updateEntry(degree))
oddTerms = IntVar(value=settings["polynomialOddTerms"])
oddTermsButton = Checkbutton(leftFrame, text="Termes impairs", command=updateOddTerms, variable=oddTerms, font=("Calibri", 13, "bold"))
oddTermsButton.place(x=31, y=105, anchor="w")
Radiobutton(leftFrame, text="Exponentielle", value="exponential", variable=functionType, command=updateFunctionType, font=("Calibri", 14, "bold")).place(x=8, y=135, anchor="w")

#Others
functionText = Label(leftFrame, text="y = /", justify=LEFT, background="light green", font=("Calibri", 14, "bold"))
functionText.place(x=8, y=165, anchor="nw")
maxInterval = IntVar(value=settings["maxInterval"])
maxIntervalButton = Checkbutton(leftFrame, text="Intervalle max", command=updateMaxInterval, variable=maxInterval, font=("Calibri", 11, "bold"))
maxIntervalButton.place(x=5, y=225, anchor="w")
showAxis = IntVar(value=settings["showAxis"])
showAxisButton = Checkbutton(leftFrame, text="Afficher repère", command=updateShowAxis, variable=showAxis, font=("Calibri", 11, "bold"))
showAxisButton.place(x=5, y=255, anchor="w")
showCoordinates = IntVar(value=settings["coordinates"])
showCoordinatesButton = Checkbutton(leftFrame, text="Afficher coordonnées", command=updateShowCoordinates, variable=showCoordinates, font=("Calibri", 11, "bold"))
showCoordinatesButton.place(x=5, y=285, anchor="w")

xAxis = canvas.create_line(-5, -5, -5, -5, width=3)
yAxis = canvas.create_line(-5, -5, -5, -5, width=3)
functionLines = [] #List containing all the small line objects to draw the function
updateFunction()

window.mainloop()