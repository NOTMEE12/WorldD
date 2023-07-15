import pygame
pygame.init()


display = pygame.display.set_mode((500, 500))
width = 600
height = 200
zoom = 1

offset = pygame.Vector2(0, 0)

rect = pygame.Surface((100, 100))


def draw():
	display.fill("white")
	rect.fill("black")
	dis_rect = display.get_rect()
	txt = pygame.Surface(pygame.Vector2(rect.get_size())*3)
	txt.fill("blue")
	sp = pygame.transform.scale_by(rect, zoom)
	txt.blit(sp, ((txt.get_width()-sp.get_width())/2, (txt.get_height()-sp.get_height())/2)+offset)
	display.blit(txt, pygame.Vector2((dis_rect.w-txt.get_width())/2, (dis_rect.h-txt.get_height())/2))
	pygame.display.flip()


def events():
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			exit()
		elif event.type == pygame.MOUSEWHEEL:
			global rect, zoom
			zoom_diff = event.y * 0.2
			zoom += zoom_diff  # event.y means the scroll
			if zoom < 1 or zoom > 15:
				zoom = pygame.math.clamp(zoom, 1, 15)
		elif event.type == pygame.MOUSEMOTION:
			print(event.buttons)
			if event.buttons[1]:
				global offset
				offset += event.rel
	
	
while True:
	draw()
	events()