import pygame
import random
import copy

#  utility functions
def directions(x, y, minX=0, minY=0, maxX=7, maxY=7):
    validdirections = []
    if x != minX: validdirections.append((x-1, y))
    if x != minX and y != minY: validdirections.append((x-1, y-1))
    if x != minX and y != maxY: validdirections.append((x-1, y+1))

    if x!= maxX: validdirections.append((x+1, y))
    if x != maxX and y != minY: validdirections.append((x+1, y-1))
    if x != maxX and y != maxY: validdirections.append((x+1, y+1))

    if y != minY: validdirections.append((x, y-1))
    if y != maxY: validdirections.append((x, y+1))

    return validdirections


def loadImages(path, size):
    img = pygame.image.load(f"{path}").convert_alpha()
    img = pygame.transform.scale(img, size)
    return img


def loadSpriteSheet(sheet, row, col, newSize, size):
    image = pygame.Surface((32, 32)).convert_alpha()
    image.blit(sheet, (0, 0), (row * size[0], col * size[1], size[0], size[1]))
    image = pygame.transform.scale(image, newSize)
    image.set_colorkey('Black')
    return image


# 🔥 УЛУЧШЕННАЯ ОЦЕНКА
def evaluateBoard(grid, player):
    weights = [
        [100, -20, 10, 5, 5, 10, -20, 100],
        [-20, -50, -2, -2, -2, -2, -50, -20],
        [10, -2, 5, 1, 1, 5, -2, 10],
        [5, -2, 1, 0, 0, 1, -2, 5],
        [5, -2, 1, 0, 0, 1, -2, 5],
        [10, -2, 5, 1, 1, 5, -2, 10],
        [-20, -50, -2, -2, -2, -2, -50, -20],
        [100, -20, 10, 5, 5, 10, -20, 100]
    ]

    score = 0
    for y in range(8):
        for x in range(8):
            if grid[y][x] == player:
                score += weights[y][x]
            elif grid[y][x] == -player:
                score -= weights[y][x]

    return score


#  Classes
class Othello:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1100, 800))
        pygame.display.set_caption('Othello')

        self.player1 = 1
        self.player2 = -1
        self.currentPlayer = 1

        self.time = 0
        self.rows = 8
        self.columns = 8

        self.gameOver = False

        self.grid = Grid(self.rows, self.columns, (80, 80), self)
        self.computerPlayer = ComputerPlayer(self.grid)

        self.RUN = True

    def run(self):
        while self.RUN:
            self.input()
            self.update()
            self.draw()

    def input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.RUN = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:
                    self.grid.printGameLogicBoard()

                if event.button == 1:
                    if self.currentPlayer == 1 and not self.gameOver:
                        x, y = pygame.mouse.get_pos()
                        x, y = (x - 80) // 80, (y - 80) // 80
                        validCells = self.grid.findAvailMoves(self.grid.gridLogic, self.currentPlayer)

                        if validCells and (y, x) in validCells:
                            self.grid.insertToken(self.grid.gridLogic, self.currentPlayer, y, x)

                            swappableTiles = self.grid.swappableTiles(y, x, self.grid.gridLogic, self.currentPlayer)
                            for tile in swappableTiles:
                                self.grid.animateTransitions(tile, self.currentPlayer)
                                self.grid.gridLogic[tile[0]][tile[1]] *= -1

                            self.currentPlayer *= -1
                            self.time = pygame.time.get_ticks()

                    if self.gameOver:
                        x, y = pygame.mouse.get_pos()
                        if 320 <= x <= 480 and 400 <= y <= 480:
                            self.grid.newGame()
                            self.gameOver = False

    def update(self):
        if self.currentPlayer == -1:
            new_time = pygame.time.get_ticks()
            if new_time - self.time >= 100:

                if not self.grid.findAvailMoves(self.grid.gridLogic, self.currentPlayer):
                    self.gameOver = True
                    return

                cell, score = self.computerPlayer.computerHard(
                    self.grid.gridLogic, 5, -1000, 1000, -1
                )

                self.grid.insertToken(self.grid.gridLogic, self.currentPlayer, cell[0], cell[1])

                swappableTiles = self.grid.swappableTiles(cell[0], cell[1], self.grid.gridLogic, self.currentPlayer)
                for tile in swappableTiles:
                    self.grid.animateTransitions(tile, self.currentPlayer)
                    self.grid.gridLogic[tile[0]][tile[1]] *= -1

                self.currentPlayer *= -1
                self.time = pygame.time.get_ticks()

        self.grid.player1Score = self.grid.calculatePlayerScore(self.player1)
        self.grid.player2Score = self.grid.calculatePlayerScore(self.player2)

        if not self.grid.findAvailMoves(self.grid.gridLogic, self.currentPlayer):
            self.gameOver = True
            return

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.grid.drawGrid(self.screen)
        pygame.display.update()


class Grid:
    def __init__(self, rows, columns, size, main):
        self.GAME = main
        self.y = rows
        self.x = columns
        self.size = size

        self.whitetoken = loadImages('lab_3/assets/WhiteToken.png', size)
        self.blacktoken = loadImages('lab_3/assets/BlackToken.png', size)

        self.transitionWhiteToBlack = [loadImages(f'lab_3/assets/BlackToWhite{i}.png', self.size) for i in range(1, 4)]
        self.transitionBlackToWhite = [loadImages(f'lab_3/assets/WhiteToBlack{i}.png', self.size) for i in range(1, 4)]

        self.bg = self.loadBackGroundImages()
        self.tokens = {}

        self.gridBg = self.createbgimg()
        self.gridLogic = self.regenGrid(self.y, self.x)

        self.player1Score = 0
        self.player2Score = 0

        self.font = pygame.font.SysFont('Arial', 20, True, False)

    def newGame(self):
        self.tokens.clear()
        self.gridLogic = self.regenGrid(self.y, self.x)

    def loadBackGroundImages(self):
        alpha = 'ABCDEFGHI'
        spriteSheet = pygame.image.load('lab_3/assets/wood.png').convert_alpha()
        imageDict = {}
        for i in range(3):
            for j in range(7):
                imageDict[alpha[j]+str(i)] = loadSpriteSheet(spriteSheet, j, i, (self.size), (32, 32))
        return imageDict

    def createbgimg(self):
        gridBg = [
            ['C0','D0','D0','D0','D0','D0','D0','D0','D0','E0'],
            ['C1','A0','B0','A0','B0','A0','B0','A0','B0','E1'],
            ['C1','B0','A0','B0','A0','B0','A0','B0','A0','E1'],
            ['C1','A0','B0','A0','B0','A0','B0','A0','B0','E1'],
            ['C1','B0','A0','B0','A0','B0','A0','B0','A0','E1'],
            ['C1','A0','B0','A0','B0','A0','B0','A0','B0','E1'],
            ['C1','B0','A0','B0','A0','B0','A0','B0','A0','E1'],
            ['C1','A0','B0','A0','B0','A0','B0','A0','B0','E1'],
            ['C1','B0','A0','B0','A0','B0','A0','B0','A0','E1'],
            ['C2','D2','D2','D2','D2','D2','D2','D2','D2','E2'],
        ]
        image = pygame.Surface((960, 960))
        for j, row in enumerate(gridBg):
            for i, img in enumerate(row):
                image.blit(self.bg[img], (i * self.size[0], j * self.size[1]))
        return image

    def regenGrid(self, rows, columns):
        grid = [[0 for _ in range(columns)] for _ in range(rows)]
        self.insertToken(grid, 1, 3, 3)
        self.insertToken(grid, -1, 3, 4)
        self.insertToken(grid, 1, 4, 4)
        self.insertToken(grid, -1, 4, 3)
        return grid

    def calculatePlayerScore(self, player):
        return sum(row.count(player) for row in self.gridLogic)

    def drawScore(self, player, score):
        return self.font.render(f'{player} : {score}', 1, 'White')

    def drawGrid(self, window):
        window.blit(self.gridBg, (0, 0))

        window.blit(self.drawScore('White', self.player1Score), (900, 100))
        window.blit(self.drawScore('Black', self.player2Score), (900, 200))

        for token in self.tokens.values():
            token.draw(window)

        availMoves = self.findAvailMoves(self.gridLogic, self.GAME.currentPlayer)
        if self.GAME.currentPlayer == 1:
            for move in availMoves:
                pygame.draw.rect(window, 'White',
                    (80 + move[1]*80 + 30, 80 + move[0]*80 + 30, 20, 20)
                )

    def printGameLogicBoard(self):
        print('  | A | B | C | D | E | F | G | H |')
        for i, row in enumerate(self.gridLogic):
            print(f'{i} |' + '|'.join(f'{c:^3}' for c in row) + '|')
        print()

    def findValidCells(self, grid, curPlayer):
        valid = []
        for x in range(8):
            for y in range(8):
                if grid[x][y] != 0:
                    continue
                for nx, ny in directions(x, y):
                    if grid[nx][ny] not in (0, curPlayer):
                        valid.append((x, y))
                        break
        return valid

    def swappableTiles(self, x, y, grid, player):
        tiles = []
        for nx, ny in directions(x, y):
            dx, dy = nx-x, ny-y
            cx, cy = nx, ny
            line = []
            while 0 <= cx < 8 and 0 <= cy < 8:
                if grid[cx][cy] == -player:
                    line.append((cx, cy))
                elif grid[cx][cy] == player:
                    tiles.extend(line)
                    break
                else:
                    break
                cx += dx
                cy += dy
        return tiles

    def findAvailMoves(self, grid, player):
        return [cell for cell in self.findValidCells(grid, player)
                if self.swappableTiles(cell[0], cell[1], grid, player)]

    def insertToken(self, grid, player, y, x):
        img = self.whitetoken if player == 1 else self.blacktoken
        self.tokens[(y, x)] = Token(player, y, x, img, self.GAME)
        grid[y][x] = player

    def animateTransitions(self, cell, player):
        if player == 1:
            self.tokens[cell].transition(self.transitionWhiteToBlack, self.whitetoken)
        else:
            self.tokens[cell].transition(self.transitionBlackToWhite, self.blacktoken)


class Token:
    def __init__(self, player, gridX, gridY, image, main):
        self.player = player
        self.posX = 80 + gridY*80
        self.posY = 80 + gridX*80
        self.GAME = main
        self.image = image

    def transition(self, images, final):
        for i in range(30):
            self.image = images[i//10]
            self.GAME.draw()
        self.image = final

    def draw(self, window):
        window.blit(self.image, (self.posX, self.posY))


class ComputerPlayer:
    def __init__(self, gridObject):
        self.grid = gridObject

    # 🔥 УЛУЧШЕННЫЙ MINIMAX
    def computerHard(self, grid, depth, alpha, beta, player):
        moves = self.grid.findAvailMoves(grid, player)

        if depth == 0 or not moves:
            return None, evaluateBoard(grid, player)

        bestMove = None

        if player < 0:
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


if __name__ == '__main__':
    game = Othello()
    game.run()
    pygame.quit()