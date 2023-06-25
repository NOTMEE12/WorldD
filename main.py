import pygame as pg
from pygame.locals import *
import tkinter
from tkinter import filedialog


class Main:
	
	def __init__(self, tile_size=(32, 32)):
		pg.init()
		tkinter.Tk().withdraw()
		"""===[ WINDOW ]==="""
		self.win = pg.display.get_desktop_sizes()[0]
		self.display = pg.display.set_mode(self.win, flags=FULLSCREEN)
		self.clock = pg.Clock()
		self.FPS = -1
		"""===[ GUI ]==="""
		self.offset = pg.Vector2(-tile_size[0]*2, -tile_size[1]*2)
		self.events = None
		self.sidebar = pg.Rect(0, 0, self.win[0] / 3, self.win[1])
		self.load = pg.Rect(self.sidebar.centerx, self.sidebar.y + self.sidebar.h/3, self.sidebar.w/1.5, 150)
		"""===[ CUSTOMIZABLE ]==="""
		self.sprite_sheet = pg.Surface((256, 256))
		self.grid = {}
		self.tile_size = tile_size
		self.zoom = 1
		self.mouse_sensitivity = 1
		self.scroll_sensitivity = 0.1
	
	def refresh(self):
		self.display.fill(0)
		x = -self.offset[0]*self.zoom - self.tile_size[0] + self.sidebar.right
		y = -self.offset[1]*self.zoom - self.tile_size[1]
		pg.draw.line(self.display, "white", (x, 0), (x, self.display.get_height()), 5)
		pg.draw.line(self.display, "white", (0, y), (self.display.get_width(), y), 5)
		for i in range(int(35/self.zoom)):
			x = i * self.tile_size[0] * self.zoom - self.offset[0] % self.tile_size[0]*self.zoom - self.tile_size[0] + \
			    self.sidebar.right
			x2 = self.sidebar.right - self.offset[0] % self.tile_size[0] - self.tile_size[0]
			y = i * self.tile_size[1] * self.zoom - self.offset[1] % self.tile_size[1]*self.zoom - self.tile_size[0]
			w = 1
			rect = self.sprite_sheet.get_rect(left=self.sidebar.centerx-self.sprite_sheet.get_width()/2 - 5,
			                                  top=self.sidebar.centery - 5)
			rect.w += 10
			rect.h += 10
			pg.draw.line(self.display, "white", (x, 0), (x, self.display.get_height()), w)
			pg.draw.line(self.display, "white", (x2, y), (self.display.get_width(), y), w)
			pg.draw.rect(self.display, (10, 10, 10), self.sidebar)
			pg.draw.rect(self.display, (22, 22, 22), rect)
			self.display.blit(self.sprite_sheet, (rect.x+5, rect.y+5))
		pg.display.flip()
		self.clock.tick(self.FPS)

	def eventHandler(self):
		self.events = pg.event.get()
		for event in self.events:
			if event.type == QUIT:
				pg.quit()
				return 1
			if event.type == MOUSEMOTION:
				if event.buttons[1]:
					self.offset -= pg.Vector2(event.rel) * self.mouse_sensitivity / self.zoom
			if event.type == MOUSEWHEEL:
				self.zoom += event.y * self.scroll_sensitivity
				self.zoom = pg.math.clamp(self.zoom, 0.75, 5)
	
	def run(self):
		while True:
			self.refresh()
			if self.eventHandler():
				return 1
			pg.display.set_caption("{:.2f}".format(self.clock.get_fps()))


if __name__ == '__main__':
	main = Main()
	main.run()
	