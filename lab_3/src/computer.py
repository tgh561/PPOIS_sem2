import copy
from src.utils import evaluateBoard

class ComputerPlayer:
    def __init__(self, gridObject):
        self.grid = gridObject

    def computerHard(self, grid, depth, alpha, beta, player):
        moves = self.grid.findAvailMoves(grid, player)
        if depth == 0 or not moves:
            return None, evaluateBoard(grid, player)

        bestMove = None
        if player < 0:  # AI (Black)
            bestScore = -float('inf')
            for move in moves:
                newGrid = copy.deepcopy(grid)
                x, y = move
                flips = self.grid.swappableTiles(x, y, newGrid, player)
                newGrid[x][y] = player
                for fx, fy in flips:
                    newGrid[fx][fy] = player
                _, val = self.computerHard(newGrid, depth-1, alpha, beta, -player)
                if val > bestScore:
                    bestScore, bestMove = val, move
                alpha = max(alpha, bestScore)
                if beta <= alpha:
                    break
            return bestMove, bestScore
        else:
            bestScore = float('inf')
            for move in moves:
                newGrid = copy.deepcopy(grid)
                x, y = move
                flips = self.grid.swappableTiles(x, y, newGrid, player)
                newGrid[x][y] = player
                for fx, fy in flips:
                    newGrid[fx][fy] = player
                _, val = self.computerHard(newGrid, depth-1, alpha, beta, -player)
                if val < bestScore:
                    bestScore, bestMove = val, move
                beta = min(beta, bestScore)
                if beta <= alpha:
                    break
            return bestMove, bestScore