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
		self.offset = pg.Vector2(tile_size[0]*2, tile_size[1]*2)
		self.events = None
		self.sidebar = pg.Rect(0, 0, self.win[0] / 3, self.win[1])
		self.load = pg.Rect(self.sidebar.centerx, self.sidebar.y + self.sidebar.h/3, self.sidebar.w/1.5, 150)
		self.text = pg.font.SysFont('Comic Sans', 20, False, False)
		self.header = pg.font.SysFont('Comic Sans', 20, True, False)
		"""===[ CUSTOMIZABLE ]==="""
		self.sprite_sheet = pg.Surface((256, 256))
		self.sprite_sheet = pg.image.load(filedialog.askopenfile(filetypes=[('image', '*.png'), ('image', '*.jpg')]))\
			.convert_alpha()
		self.selection = pg.Rect(0, 0, 0, 0)
		self.tiles = {}
		self.grid = {}
		self.tile_size = tile_size
		self.zoom = 1
		self.mouse_sensitivity = 1
		self.scroll_sensitivity = 0.1
		self.sprite_sheet_zoom = 1
		self.sprite_sheet_offset = pg.Vector2(0, 0)
	
	def refresh(self):
		self.display.fill(0)
		x = self.offset[0]*self.zoom - self.tile_size[0] + self.sidebar.right
		y = self.offset[1]*self.zoom - self.tile_size[1]
		pg.draw.line(self.display, "white", (x, 0), (x, self.display.get_height()), 5)
		pg.draw.line(self.display, "white", (0, y), (self.display.get_width(), y), 5)
		for idx in range(int(35/self.zoom)):
			x = idx * self.tile_size[0] * self.zoom + self.offset[0] % self.tile_size[0] * self.zoom - self.tile_size[
				0] + \
			    self.sidebar.right
			pg.draw.line(self.display, "white", (x, 0), (x, self.display.get_height()), 1)
			x2 = self.sidebar.right - self.offset[0] % self.tile_size[0] - self.tile_size[0]
			y = idx * self.tile_size[1] * self.zoom + self.offset[1] % self.tile_size[1] * self.zoom - self.tile_size[0]
			pg.draw.line(self.display, "white", (x2, y), (self.display.get_width(), y), 1)
		rect = self.sprite_sheet.get_rect(left=self.sidebar.centerx-self.sprite_sheet.get_width()/2 - 5,
		                                  top=self.sidebar.centery - 5)
		rect.w += 10
		rect.h += 10
		pg.draw.rect(self.display, (10, 10, 10), self.sidebar)
		pg.draw.rect(self.display, (32, 32, 32), rect)
		sp_sheet = pg.transform.scale_by(self.sprite_sheet, self.sprite_sheet_zoom)
		pg.draw.rect(sp_sheet, (220, 220, 220),
		             pg.Rect(
			             self.selection.x*self.sprite_sheet_zoom,
			             self.selection.y*self.sprite_sheet_zoom,
			             self.selection.w*self.sprite_sheet_zoom,
			             self.selection.h*self.sprite_sheet_zoom
		             ), width=1)
		self.display.blit(sp_sheet, (rect.x+5, rect.y+5), pg.Rect(self.sprite_sheet_offset, (rect.w-5, rect.h-5)))
		pg.display.flip()
		self.clock.tick(self.FPS)

	def eventHandler(self):
		self.events = pg.event.get()
		for event in self.events:
			if event.type == QUIT:
				pg.quit()
				return 1
			if event.type == MOUSEBUTTONDOWN:
				if event.button == 1:
					self.selection.x = pg.math.clamp(
						(event.pos[0]-(self.sidebar.centerx-self.sprite_sheet.get_width()/2-self.sprite_sheet_offset.x))/
						self.sprite_sheet_zoom,
						0, self.sprite_sheet.get_width()
					)
					self.selection.y = pg.math.clamp(
						(event.pos[1]-self.sidebar.centery-self.sprite_sheet_offset.y)/self.sprite_sheet_zoom,
						0, self.sprite_sheet.get_height()
					)
					self.selection.w = 0
					self.selection.h = 0
			if event.type == MOUSEBUTTONUP:
				if event.button == 1:
					self.selection.w = (event.pos[0]-(self.selection.x+self.sidebar.centerx-self.sprite_sheet.get_width()/2-self.sprite_sheet_offset.x))/self.sprite_sheet_zoom+1
					self.selection.h = (event.pos[1]-(self.selection.y+self.sidebar.centery))/self.sprite_sheet_zoom+1
					print(self.selection)
			if event.type == MOUSEMOTION:
				if event.pos[0] > self.sidebar.right:
					if event.buttons[1]:
						self.offset += pg.Vector2(event.rel) * self.mouse_sensitivity / self.zoom
				elif self.sprite_sheet.get_rect(left=self.sidebar.centerx-self.sprite_sheet.get_width()/2 - 5,
		                                  top=self.sidebar.centery - 5).collidepoint(event.pos):
					if event.buttons[1]:
						self.sprite_sheet_offset -= pg.Vector2(event.rel) * self.mouse_sensitivity
						self.sprite_sheet_offset.x = pg.math.clamp(self.sprite_sheet_offset.x, 0,
						                                           self.sprite_sheet_zoom*
						                                           self.sprite_sheet.get_width()-
						                                           self.sprite_sheet.get_width())
						self.sprite_sheet_offset.y = pg.math.clamp(self.sprite_sheet_offset.y, 0,
						                                           self.sprite_sheet_zoom*
						                                           self.sprite_sheet.get_height()-
						                                           self.sprite_sheet.get_height())
			if event.type == MOUSEWHEEL:
				if pg.mouse.get_pos()[0] > self.sidebar.right:
					self.zoom += event.y * self.scroll_sensitivity
					self.zoom = pg.math.clamp(self.zoom, 0.75, 5)
				else:
					self.sprite_sheet_zoom += event.y * self.scroll_sensitivity
					self.sprite_sheet_zoom = pg.math.clamp(self.sprite_sheet_zoom, 1, 15)
	
	def run(self):
		while True:
			self.refresh()
			if self.eventHandler():
				return 1
			pg.display.set_caption("{:.2f}".format(self.clock.get_fps()))


if __name__ == '__main__':
	main = Main()
	main.run()
	