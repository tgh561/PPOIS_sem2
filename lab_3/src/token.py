import pygame

class Token:
    def __init__(self, player, gridX, gridY, image, game):
        self.player = player
        self.gridX = gridX
        self.gridY = gridY
        self.posX = 80 + gridY * 80
        self.posY = 80 + gridX * 80
        self.GAME = game
        self.image = image

    def transition(self, images, final):
        for i in range(30):
            self.image = images[min(i // 8, len(images)-1)]
            
            self.GAME.draw()
            pygame.display.update()
            pygame.time.delay(20) 
        self.image = final
    def draw(self, window, rotated=False, offset=80, cell_size=80, rows=8, columns=8):
        if not rotated:
            window.blit(self.image, (self.posX, self.posY))
            return
        draw_x = offset + (columns - 1 - self.gridY) * cell_size
        draw_y = offset + (rows - 1 - self.gridX) * cell_size
        window.blit(self.image, (draw_x, draw_y))