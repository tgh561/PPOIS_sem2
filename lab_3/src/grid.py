import pygame
from src.utils import loadImages, loadSpriteSheet
from src.token import Token
from src.utils import directions


class Grid:
    def __init__(self, main, rows=8, columns=8, settings=None):
        self.GAME = main
        self.settings = settings or {}
        self.y = rows
        self.x = columns
        board_settings = self.settings.get("board", {})
        self.cell_size = board_settings.get("cell_size", 80)
        self.offset = board_settings.get("offset", 80)
        self.size = (self.cell_size, self.cell_size)
        image_settings = self.settings.get("assets", {}).get("images", {})
        self.whitetoken = loadImages(image_settings.get("white_token", "assets/WhiteToken.png"), self.size)
        self.blacktoken = loadImages(image_settings.get("black_token", "assets/BlackToken.png"), self.size)
        self.transitionWhiteToBlack = [loadImages(path, self.size) for path in image_settings.get("black_to_white", [])]
        self.transitionBlackToWhite = [loadImages(path, self.size) for path in image_settings.get("white_to_black", [])]
        if not self.transitionWhiteToBlack:
            self.transitionWhiteToBlack = [self.whitetoken] * 3
        if not self.transitionBlackToWhite:
            self.transitionBlackToWhite = [self.blacktoken] * 3

        self.bg = self.loadBackGroundImages()
        self.gridBg = self.createbgimg()
        self.tokens = {}
        self.gridLogic = self.regenGrid(self.y, self.x)
        self.player1Score = 0
        self.player2Score = 0
        self.font = pygame.font.SysFont('Arial', 20, True, False)

    def newGame(self):
        self.tokens.clear()
        self.gridLogic = self.regenGrid(self.y, self.x)

    def loadBackGroundImages(self):
        alpha = 'ABCDEFGHI'
        board_texture = self.settings.get("assets", {}).get("images", {}).get("board_texture", "assets/wood.png")
        spriteSheet = pygame.image.load(board_texture).convert_alpha()
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

    # def drawGrid(self, window, rotated=False):
    #     window.blit(self.gridBg, (0, 0))

    #     window.blit(self.drawScore('White', self.player1Score), (900, 100))
    #     window.blit(self.drawScore('Black', self.player2Score), (900, 200))

    #     for token in self.tokens.values():
    #         token.draw(window, rotated=rotated, offset=self.offset, cell_size=self.cell_size, rows=self.y, columns=self.x)

    #     availMoves = self.findAvailMoves(self.gridLogic, self.GAME.currentPlayer)
    #     for move in availMoves:
    #         row, col = move
    #         if rotated:
    #             row = self.y - 1 - row
    #             col = self.x - 1 - col
    #         pygame.draw.circle(
    #                         window, 
    #                         'Green', 
    #                         (self.offset + col * self.cell_size + 30, 
    #                         self.offset + row * self.cell_size + 30), 
    #                         20
    #                     )

    def drawGrid(self, window, rotated=False):
        window.blit(self.gridBg, (0, 0))
        window.blit(self.drawScore('White', self.player1Score), (900, 100))
        window.blit(self.drawScore('Black', self.player2Score), (900, 200))

        # Отрисовка фишек
        for token in self.tokens.values():
            token.draw(window, rotated=rotated, offset=self.offset, 
                    cell_size=self.cell_size, rows=self.y, columns=self.x)

        # Подсветка доступных ходов
        availMoves = self.findAvailMoves(self.gridLogic, self.GAME.currentPlayer)
        
        for row, col in availMoves:
            if rotated:
                row = self.y - 1 - row
                col = self.x - 1 - col

            center_x = self.offset + col * self.cell_size + self.cell_size // 2
            center_y = self.offset + row * self.cell_size + self.cell_size // 2

            # Основной круг (чуть меньше, как ты просил)
            pygame.draw.circle(window, (0, 255, 0), (center_x, center_y), 16)
            
            # Опционально: красивая обводка
            pygame.draw.circle(window, (0, 200, 0), (center_x, center_y), 16, width=3)

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


    