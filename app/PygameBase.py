import pygame as pg
from pygame.locals import *
import sys

pg.init()


class PgBase:
	
	def __init__(self, win_size):
		self.win = win_size
		self.screen = pg.display.set_mode(win_size, RESIZABLE + SCALED)
		self.events = ()
		self.clock = pg.time.Clock()
		self.FPS = 60
	
	def exit(self):
		sys.exit()
	
	def refresh(self):
		self.clock.tick(self.FPS)
		pg.display.flip()
		