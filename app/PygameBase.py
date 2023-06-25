import pygame as pg
from pygame.locals import *
import sys

pg.init()


class PgBase:
	
	def __init__(self, win_size: pg.Vector2 | list[int, int] | tuple[int, int], fps: int = 60, *, flags=FULLSCREEN):
		self.win = win_size
		self.display = pg.display.set_mode(win_size, flags)
		self.headers = pg.font.SysFont('Arial', 20, bold=True)
		self.events = ()
		self.clock = pg.time.Clock()
		self.FPS = fps
	
	@staticmethod
	def exit():
		sys.exit()
	
	def refresh(self):
		self.clock.tick(self.FPS)
		pg.display.flip()
