#Equipe 1155
#FrictionCoefficientsFinder : Affiche les coefficients de frottement sur la pente et sur le sol à partir de quelques données expérimentales

import numpy as np

def simulation(kp, m, h, w, g, step):
    """Simule la vitesse en fin de pente pour un certain coefficient de frottement
        (copié-collé d'une partie de la fonction simulation() de PhysicsSimulation.py)

    Args:
        kp (float): Le coefficient de frottement (sur la pente)
        m (float): La masse du véhicule [kg]
        h (float): La hauteur de la pente [m]
        w (float): La largeur de la pente [m]
        g (float): La constante de gravitation
        step (int): La taille des découpes de la pente

    Returns:
        _type_: _description_
    """
    #Simulation pente
    xPente = np.arange(-w, 0, step)
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


def find_k(vi: float,vt: float, t: float, step: float)->tuple:
    """Calcules le coefficient de frottement sur le sol et celui sur la pente

    Args:
        vi (float): La vitesse en bas de pente
        vt (float): La vitesse à un certain temps t sur le sol
        t (float): Le temps
        step (float): Le nombre à incrémenter à chaque itération pour trouver le coefficient sur la pente

    Returns:
        tuple (float, float): Le coefficient sur le sol, Le coefficient sur la pente
    """
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