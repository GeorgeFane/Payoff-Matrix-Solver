This repo contains code that can solve payoff matrices with any number of players and strategies. It finds Nash equilibria.

The matrix that is often taught in intro economics courses is a 2-player 2-strategy game, shown as a grid containing four cells that each contain 2 payoffs. Handling more strategies means increasing the 'side length' of the matrix, which would result in a square matrix but larger. Handling more players means expanding that square into higher dimensions, like a payoff tensor or 'cube' for 3 players or a 'hypercube' for even higher numbers of players.

This code is deployed as a Heroku web app, which can be found at: https://payoff-matrix-solver.herokuapp.com/.
Its documentation can be found at https://gist.github.com/GeorgeFane/1fe25aeeeff3dfb396940d07c19b7a4e.
