# EPL1155P1-Physics-Simulation
Groupe 1155 EPL : simulation informatique pour le projet 1

Membres de l'équipe : Samy Adda, Lucas Ahou, Geoffroy Amory, Bastien Aubecq, Romain Bellens
\
\
\
INTRODUCTION :

Ce dossier contient tous les programmes écrits dans le cadre de la simulation physique du projet 1 du groupe 1155 (EPL).
Ils permettent de :

-Simuler la position, la vitesse, l'accélération et l'énergie d'un véhicule roulant sur une pente courbée et continuant ensuite sur le sol.

-Estimer les coefficients de frottement (sur la pente et sur le sol) à partir de quelques valeurs expérimentales données.

-Comparer des données expérimentales avec des données théoriques calculées précédemment.

-Trouver la fonction mathématique approchant le mieux une pente à partir d'une image de celle-ci.

\
\
PROGRAMMES :

1) PhysicsSimulation.py :
Le programme PhysicsSimulation permet de simuler le mouvement du véhicule (position x, position y, vitesse et accélération), ainsi que l'énergie qu'il contient (potentielle, cinétique et totale) à tout instant sur la pente et puis sur le sol.
Les résultats sont présentés sous forme de graphiques, le tout dans une interface graphique permettant de mettre à jour en temps réel l'entièreté des paramètres de la simulation (dimensions de la pente, coefficients de frottement, masse du véhicule, etc.).
Le programme permet également d'exporter les résultats sous forme d'un fichier texte pour pouvoir comparer les résultats dans un deuxième temps.

2) FrictionCoefficientsFinder.py :
Le programme FrictionCoefficientsFinder permet d'estimer les coefficients de frottement sur la pente ainsi que sur le sol à partir de valeurs expérimentales (trouvées par exemple grâce à une expérience).
Ces coefficients peuvent ensuite être utilisé pour le programme de simulation ci-dessus.
Le coefficient de frottement sur le sol est calculé en isolant k dans nos équations théoriques et en remplaçant v(t) et t par une valeur expérimentale donnée.
Le coefficient de frottement sur la pente est estimé en simulant le mouvement (grâce au programme de simulation ci-dessus) de multiples fois avec chaque fois un k de plus en plus grand jusqu'à arriver à une vitesse en fin de pente similaire à la valeur expérimentale donnée.

3) DataComparison.py :
Le programme DataComparison permet de comparer les données contenues dans plusieurs fichiers (par exemple les données théoriques exportées par le programme de simulation et les données expérimentales trouvées grâce à une expérience).
Le tout est une interface graphique permettant d'ouvrir et de fermer un/plusieurs fichier et de comparer les données grâce à des graphiques.

4) FunctionFinder.py :
Le programme FunctionFinder permet de trouver la meilleure fonction mathématique (polynôme ou exponentielle) afin d'approcher la forme de notre pente pour le programme de simulation.
Dans l'interface graphique, il est possible de :
-Ouvrir une image.  
-Positionner 2 points de coordonnées connues sur l'image pour former le repère.  
-Placer des points sur l'image pour indiquer au programme où est la pente.  
-Choisir quelle type de fonction doit être utilisé pour approximer la pente (exponentielle ou polynôme de degré quelconque, avec ou sans termes d'exposant impair).  
-Voir la fonction trouvée par le programme sur l'image et en connaitre son équation.

\
\
AUTRES FICHIERS :

1) experimentalData.txt :
Contient les données expérimentales récoltées lors d'une expérience réalisée avec notre véhicule et notre pente.

2) imagePente.jpg :
Une image de notre pente pour le programme FunctionFinder1155.
