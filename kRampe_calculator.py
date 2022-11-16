import numpy as np

def simulation(kp, m, h, w, g, step):
    #Simulation pente
    xPente = np.arange(-w, 0, step)
    #Parabola : (h/w**2)*xPente**2
    #Exponential : h*np.e**((-3.5*xPente)/w-3.5)
    yPente = h*np.e**((-3.5*xPente)/w-3.5)
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
    return vxPente[-1]

def find_k(vi: float,vt: float, t: float, step: float)->float:
    #Parameters
    stepPente = 0.001
    m = 0.382
    h = 1
    l = 0.5
    g = 9.81

    k_pente, k = 0, 0
    while simulation(k_pente, m, h, l, g, stepPente) > vi:
        k_pente += step
    
    k = (-m/t)*np.log(vt/vi)

    return (k, k_pente)
    
print(find_k(3.75, 2.5, 1.5, 0.01))