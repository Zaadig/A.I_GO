Team :  Mohammed Seddiq ELALAOUI - Atman BOZ   --  G2

Nous avons implémenté l'algorithme Monte Carlo Tree Search (MCTS), qui est une technique populaire pour jouer au Go. Cette méthode est très efficace pour explorer de grandes profondeurs d'arbre de jeu et pour estimer les chances de victoire de chaque joueur à chaque étape.

Nous avons également utilisé une fonction de prédiction de position (position_predict) pour améliorer l'évaluation des nœuds de l'arbre de jeu. Cette fonction prend en entrée les positions des pierres noires et blanches sur le plateau de jeu et renvoie une évaluation de la position actuelle du jeu. Cette évaluation est utilisée pour ajuster les scores d'exploration et d'exploitation de chaque nœud.

Nous avons utilisé une classe Node pour représenter les nœuds de l'arbre de jeu. Chaque nœud contient une copie du plateau de jeu actuel, ainsi que des informations sur les mouvements précédents et les statistiques de jeu associées.

Nous avons également utilisé des techniques d'optimisation pour améliorer les performances de notre joueur. En particulier, nous avons utilisé un ThreadPoolExecutor pour paralléliser les simulations de jeu et une fonction is_fully_expanded pour éviter de simuler des parties inutiles.

Nous sommes particulièrement fiers de notre méthode d'évaluation de fin de partie, qui utilise une méthode plus sophistiquée que la simple différence de score pour déterminer le gagnant de la partie.

Enfin, nous avons inclus des commentaires détaillés dans notre code pour faciliter la compréhension et la maintenance à long terme.
