import pygame

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Carreras con la Mano")

car_x = WIDTH // 2
car_y = HEIGHT - 100
speed = 5

clock = pygame.time.Clock()
running = True

while running:
    clock.tick(60)
    screen.fill((30, 30, 30))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.draw.rect(screen, (0, 200, 0), (car_x, car_y, 50, 80))
    pygame.display.update()

pygame.quit()
