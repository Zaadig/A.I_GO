Team :  Mohammed Seddiq ELALAOUI - Atman BOZ   --  G2

# 1. Description de l'implémentation de l'algorithme MCTS

# 1.1  l'implémentation de l'algorithme MCTS

Nous avons implémenté l'algorithme Monte Carlo Tree Search (MCTS), qui est une technique populaire pour jouer au Go. Cette méthode est très efficace pour explorer 
de grandes profondeurs d'arbre de jeu et pour estimer les chances de victoire de chaque joueur à chaque étape.

Nous avons également utilisé une fonction de prédiction de position (position_predict) pour améliorer l'évaluation des nœuds de l'arbre de jeu. Cette fonction prend 
en entrée les positions des pierres noires et blanches sur le plateau de jeu et renvoie une évaluation de la position actuelle du jeu. Cette évaluation est utilisée 
pour ajuster les scores d'exploration et d'exploitation de chaque nœud.

Nous avons utilisé une classe Node pour représenter les nœuds de l'arbre de jeu. Chaque nœud contient une copie du plateau de jeu actuel, ainsi que des informations

sur les mouvements précédents et les statistiques de jeu associées.

Nous avons également utilisé des techniques d'optimisation pour améliorer les performances de notre joueur. En particulier, nous avons utilisé un ThreadPoolExecutor

pour paralléliser les simulations de jeu et une fonction is_fully_expanded pour éviter de simuler des parties inutiles.

Nous avons implémenté un joueur alpha-beta pour tester notre joueur qui utilise MCTS.


# 1.2  l'implémentation de l'algorithme alpha-beta

Nous avons implémenté un joueur alpha-beta pour tester notre joueur qui utilise MCTS.

Nous sommes particulièrement fiers de notre méthode d'évaluation de fin de partie, qui utilise une méthode plus sophistiquée que la simple différence de score pour 
déterminer le gagnant de la partie.

Enfin, nous avons inclus des commentaires détaillés dans notre code pour faciliter la compréhension et la maintenance à long terme.


# 2. Description de l'implémentation des heuristiques


# 2.1 l'heuristique  de joueur MCTS

L'heuristique est une fonction appelée "position_predict" qui prend en entrée un plateau de jeu de Go et renvoie une valeur d'évaluation du plateau.

Cette fonction fait des predictions selon le model que nous avons concu pour le tp_ml_go


# 2.2  l'heuristique  de joueur alpha_beta

L'heuristique est une fonction appelée "ImprovedEvaluation" qui prend en entrée un plateau de jeu de Go et renvoie une valeur d'évaluation du plateau.

Si le jeu est terminé, la fonction retourne une valeur infinie si le joueur actuel a gagné, une valeur moins l'infini s'il a perdu, et 0 en cas d'égalité.

Si le jeu n'est pas terminé, la fonction calcule plusieurs caractéristiques du plateau et leur attribue des poids différents pour obtenir une évaluation globale.

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


