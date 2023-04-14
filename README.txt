-------------------------------------------------------------

Team :  Mohamed Seddiq ELALAOUI - Atman BOZ   --  G2

-------------------------------------------------------------



# 1. Joueur officiel ( myPlayer.py )

Il s'agit du joueur fourni dans myPlayer.py. Ce programme concerne un joueur de Go qui utilise un réseau neuronal pour prédire le meilleur coup à jouer. 
Le réseau neuronal a été entraîné en combinant trois ensembles de données distincts. Pour importer et traiter les données, exécutez le script ImportAndExtract.py. 
Ce script générera l'ensembles des données d'entraînement, de validation et de test traités à l'aide de pickle. Ensuite, le fichier opNeuralNetwork.py utilisera 
ces données pour créer le modèle my_op_model.h5.


# 2. Joueur MCTS ( MonteCarloPlayer.py )


Nous avons implémenté l'algorithme Monte Carlo Tree Search (MCTS), qui est une technique populaire pour jouer au Go. Cette méthode est très efficace pour explorer 
de grandes profondeurs d'arbre de jeu et pour estimer les chances de victoire de chaque joueur à chaque étape.

Nous avons également utilisé une fonction de prédiction de position (position_predict) pour améliorer l'évaluation des nœuds de l'arbre de jeu. Cette fonction utilise
notre  model d'aprentissage conçu pour le tp ML_GO pour renvoyer une évaluation de la position actuelle du jeu. Cette évaluation est utilisée 
pour ajuster les scores d'exploration et d'exploitation de chaque nœud.

Nous avons utilisé une classe Node pour représenter les nœuds de l'arbre de jeu. Chaque nœud contient une copie du plateau de jeu actuel, ainsi que des informations
sur les mouvements précédents et les statistiques de jeu associées.

Nous avons également utilisé des techniques d'optimisation pour améliorer les performances de notre joueur. En particulier, nous avons utilisé un ThreadPoolExecutor
pour paralléliser les simulations de jeu et une fonction is_fully_expanded pour éviter de simuler des parties inutiles.


# 3.  Joueur alpha-beta ( AlphaBetaPlayer.py )

L'heuristique dans cette implémentation calcule plusieurs caractéristiques du plateau et leur attribue des poids différents pour obtenir une évaluation globale.

Les caractéristiques prises en compte sont :

    * La différence de score entre les joueurs.
    * La différence entre le nombre de mouvements légaux du joueur actuel et de son adversaire.
    * La différence entre le nombre de libertés des groupes de pierres du joueur actuel et de son adversaire.
    * La différence entre le nombre de groupes de pierres du joueur actuel et de son adversaire.
    * La différence entre le nombre total de libertés des groupes de pierres du joueur actuel et de son adversaire.
    * La différence entre la "influence" du joueur actuel et de son adversaire. La "influence" est une mesure de la force relative de chaque joueur sur le plateau.
    * La différence entre le nombre de pierres capturées par le joueur actuel et par son adversaire.

Ces caractéristiques sont pondérées différemment, avec des poids qui peuvent être ajustés pour obtenir une évaluation plus fine et plus précise.

l'heuristique est conçue de manière à minimiser les mouvements risqués et à favoriser les mouvements qui sont plus susceptibles de conduire à la victoire. 
Par exemple, elle accorde une importance plus élevée aux groupes ayant plus de libertés, car cela signifie qu'ils sont plus difficiles à capturer. De même, 
elle prend en compte l'influence des pierres sur le plateau, car cela peut affecter la façon dont les groupes se développent.


# 4. Après avoir organisé plusieurs matchs entre nos différents joueurs, nous avons constaté que le premier joueur était le meilleur, pour cela , il est élu 
pour participer au tournoi ;/




