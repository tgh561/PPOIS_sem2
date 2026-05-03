import pygame
import sys

pygame.init()
screen = pygame.display.set_mode((1100, 800))
pygame.display.set_caption('REVERSI - Test')

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 48)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            print(f"Клик! Кнопка: {event.button}   Позиция: {event.pos}")  # ← должно печатать

    screen.fill((0, 30, 0))  # тёмно-зелёный фон
    
    # Текст на экране
    text = font.render("Reversi Test - Кликни правой кнопкой", True, (255, 255, 255))
    screen.blit(text, (100, 100))
    
    text2 = font.render("Если видишь этот текст - всё хорошо", True, (200, 200, 100))
    screen.blit(text2, (100, 160))
    
    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()