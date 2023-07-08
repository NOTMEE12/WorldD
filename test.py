import pygame
from pygame._sdl2.window import Window
import os

os.environ['SDL_VIDEO_CENTERED'] = '1'

pygame.init()

win = pygame.Vector2(pygame.display.get_desktop_sizes()[0])
screen = pygame.display.set_mode(win, pygame.RESIZABLE)

Window().from_display_module()
