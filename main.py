import pygame as pg
from pygame.locals import *
import tkinter
from tkinter import filedialog
import sys


class Main:
	
	def __init__(self, tile_size=(32, 32)):
		pg.init()
		tkinter.Tk().withdraw()
		"""===[ WINDOW ]==="""
		self.win = pg.Vector2(pg.display.get_desktop_sizes()[0])
		self.display = pg.display.set_mode(self.win, RESIZABLE)
		pg.display.toggle_fullscreen()
		self.clock = pg.Clock()
		self.FPS = -1
		"""===[ GUI ]==="""
		self.offset = pg.Vector2(tile_size[0] * 2, tile_size[1] * 2)
		self.events = None
		self.sidebar = pg.Rect(0, 0, self.win[0] / 3, self.win[1])
		self.load = pg.Rect(self.sidebar.centerx, self.sidebar.y + self.sidebar.h / 3, self.sidebar.w / 1.5, 150)
		self.text = pg.font.SysFont('Arial', 30, False, False)
		self.header = pg.font.SysFont('Arial', 35, True, False)
		self.save_selection = self.header.render("Save selection? (name/ESC)", True, (250, 250, 250))
		self.sprite_sheet = None
		"""===[ CUSTOMIZABLE ]==="""
		try:
			self.sprite_sheet = pg.image.load(filedialog.askopenfile(filetypes=[('image', '*.png'), ('image', '*.jpg')]))\
				.convert_alpha()
		except TypeError:
			sys.exit()
		self.selected_tile = None
		self.scroll = 0
		self.sprite_sheet_grid_color = "white"
		self.grid_color = "white"
		self.selection_color = "red"
		self.selected_tile_color = "white"
		self.selection_name = ""
		self.selection = pg.Rect(0, 0, 0, 0)
		self.tiles = {}
		self.grid = {}
		self.tile_size = pg.Vector2(tile_size)
		self.zoom = 1
		self.mouse_sensitivity = 1
		self.scroll_sensitivity = .1
		self.sprite_sheet_zoom = 1
		self.sprite_sheet_offset = pg.Vector2(0, 0)
	
	def refresh(self):
		self.display.fill(0)
		x = self.offset[0] * self.zoom - self.tile_size[0] + self.sidebar.right
		y = self.offset[1] * self.zoom - self.tile_size[1]
		pg.draw.line(self.display, "white", (x, 0), (x, self.display.get_height()), 5)
		pg.draw.line(self.display, "white", (0, y), (self.display.get_width(), y), 5)
		for idx in range(int(max(self.display.get_width() / self.tile_size[0], self.display.get_height() /
		                                                                       self.tile_size[1]) / self.zoom)):
			x = idx * self.tile_size[0] * self.zoom + self.offset[0] % self.tile_size[0] * self.zoom - \
			    self.tile_size[0] + self.sidebar.right
			pg.draw.line(self.display, self.grid_color, (x, 0), (x, self.display.get_height()), 1)
			x2 = self.sidebar.right - self.offset[0] % self.tile_size[0] - self.tile_size[0]
			y = idx * self.tile_size[1] * self.zoom + self.offset[1] % self.tile_size[1] * self.zoom - self.tile_size[0]
			pg.draw.line(self.display, self.grid_color, (x2, y), (self.display.get_width(), y), 1)
		rect = self.sprite_sheet.get_rect(left=self.sidebar.centerx - self.sprite_sheet.get_width() / 2,
		                                  top=self.sidebar.centery)
		pg.draw.rect(self.display, (10, 10, 10), self.sidebar)
		pg.draw.rect(self.display, (32, 32, 32), rect)
		sp_sheet = pg.transform.scale_by(self.sprite_sheet, self.sprite_sheet_zoom)
		pg.draw.rect(sp_sheet, self.selection_color, pg.Rect(
			self.selection.x * self.sprite_sheet_zoom, self.selection.y * self.sprite_sheet_zoom,
			self.selection.w * self.sprite_sheet_zoom, self.selection.h * self.sprite_sheet_zoom), width=3)
		if self.sprite_sheet.get_width() > self.sprite_sheet.get_height():
			r = self.sprite_sheet.get_width() / self.tile_size[0]
		else:
			r = self.sprite_sheet.get_height() / self.tile_size[1]
		self.display.blit(sp_sheet, (rect.x, rect.y), pg.Rect(self.sprite_sheet_offset, (rect.w, rect.h)))
		for idx in range(int(r/self.sprite_sheet_zoom)+2):
			x = idx * self.tile_size[0] * self.sprite_sheet_zoom - self.sprite_sheet_offset.x % (self.tile_size[0]*self.sprite_sheet_zoom) + rect.left
			if rect.left <= x <= rect.right:
				pg.draw.line(self.display, self.sprite_sheet_grid_color, (x, rect.top), (x, rect.bottom), 1)
			y = rect.y + idx * self.tile_size[1] * self.sprite_sheet_zoom - self.sprite_sheet_offset.y % \
			    (self.tile_size[1] * self.sprite_sheet_zoom)
			if rect.top <= y <= rect.bottom:
				pg.draw.line(self.display, self.sprite_sheet_grid_color, (rect.left, y), (rect.right, y), 1)
		if self.selection != (0, 0, 0, 0):
			self.display.blit(self.save_selection,
			                  (rect.centerx - self.save_selection.get_width() / 2, rect.bottom + 20))
			text = self.text.render(self.selection_name, False, (120, 120, 120))
			self.display.blit(text, (rect.centerx-text.get_width()/2, rect.bottom + 50))
		tiles = pg.Surface((self.sidebar.w, self.sidebar.centery))
		for idx, (name, tile) in enumerate(zip(self.tiles.keys(), self.tiles.values())):
			pos = pg.Vector2(idx % 7 * 69+5, idx//7*109+5+self.scroll)
			text = self.text.render(name, False, (120, 120, 120), wraplength=55)
			if name == self.selected_tile:
				pg.draw.rect(tiles, self.selected_tile_color, pg.Rect(pos.x-4, pos.y-4, 72, 72))
			tiles.blit(pg.transform.scale(self.sprite_sheet.subsurface(tile), (64, 64)), pos)
			tiles.blit(text, (idx % 7 * 69+5+32-text.get_width()/2, idx//7*109+5+64+self.scroll))
		self.display.blit(tiles, (0, 0))
		tile_size = self.header.render(f'{self.tile_size[0]}x{self.tile_size[1]}', True, (200, 200, 200))
		self.display.blit(tile_size, (rect.centerx-tile_size.get_width()/2, rect.bottom + 75))
		pg.display.flip()
		self.clock.tick(self.FPS)
	
	def eventHandler(self):
		self.events = pg.event.get()
		for event in self.events:
			if event.type == QUIT:
				pg.quit()
				return 1
			elif event.type == KEYDOWN:
				if event.key == K_F11:
					pg.display.toggle_fullscreen()
				elif event.key == K_UP:
					self.tile_size *= 2
				elif event.key == K_DOWN:
					self.tile_size /= 2
				elif self.save_selection != (0, 0, 0, 0):
					if event.key == K_ESCAPE:
						self.selection = pg.Rect(0, 0, 0, 0)
						self.selection_name = ""
					elif event.key == K_BACKSPACE:
						self.selection_name = self.selection_name[:-1]
					elif event.key == K_DELETE:
						pass
					elif event.key == K_RETURN:
						self.tiles[self.selection_name] = tuple(self.selection.copy())
						self.selection = pg.Rect(0, 0, 0, 0)
						self.selection_name = ""
					else:
						self.selection_name += event.unicode
			elif event.type == MOUSEBUTTONDOWN:
				if event.button == 1:
					if event.pos[0] < self.sidebar.right:
						if event.pos[0] >= self.sidebar.centerx - self.sprite_sheet.get_width() / 2 and event.pos[1] >= self.sidebar.centery:
							self.selection.x = pg.math.clamp(
								(event.pos[0]-(self.sidebar.centerx-self.sprite_sheet.get_width()/2-self.sprite_sheet_offset.x))/self.sprite_sheet_zoom,
								0, self.sprite_sheet.get_width()
							)
							self.selection.y = pg.math.clamp(
								(event.pos[1] - self.sidebar.centery - self.sprite_sheet_offset.y) / self.sprite_sheet_zoom,
								0, self.sprite_sheet.get_height()
							)
							self.selection.w = 0
							self.selection.h = 0
						elif self.sidebar.collidepoint(event.pos):
							for idx, (name, tile) in enumerate(zip(self.tiles.keys(), self.tiles.values())):
								if pg.Rect((idx % 7 * 69+5, idx//7*109+5+self.scroll), (64, 64)).collidepoint(event.pos):
									print(name, tile)
									self.selected_tile = name
									print(name)
									break
					else:
						self.grid[
							(
								(event.pos[0]-self.offset[0])//self.tile_size[0],
								(event.pos[1]-self.offset[1])//self.tile_size[1])
						] = self.selected_tile
			elif event.type == MOUSEBUTTONUP:
				if event.button == 1:
					if event.pos[0] >= self.sidebar.centerx - self.sprite_sheet.get_width() / 2 and event.pos[
						1] >= self.sidebar.centery:
						self.selection.w = pg.math.clamp(
								(event.pos[0]-(self.sidebar.centerx-self.sprite_sheet.get_width()/2-self.sprite_sheet_offset.x))/self.sprite_sheet_zoom-self.selection.x+1,
								0, self.sprite_sheet.get_width()
							)
						self.selection.h = pg.math.clamp(
								(event.pos[1]-self.sidebar.centery-self.sprite_sheet_offset.y)/self.sprite_sheet_zoom-self.selection.y+1,
								0, self.sprite_sheet.get_height()
							)
			elif event.type == MOUSEMOTION:
				if event.pos[0] > self.sidebar.right:
					if event.buttons[1]:
						self.offset += pg.Vector2(event.rel) * self.mouse_sensitivity / self.zoom
				elif self.sprite_sheet.get_rect(left=self.sidebar.centerx - self.sprite_sheet.get_width() / 2 - 5,
				                                top=self.sidebar.centery - 5).collidepoint(event.pos):
					if event.buttons[1]:
						self.sprite_sheet_offset -= pg.Vector2(event.rel) * self.mouse_sensitivity
						self.sprite_sheet_offset.x = pg.math.clamp(self.sprite_sheet_offset.x, 0,
						                                           self.sprite_sheet_zoom *
						                                           self.sprite_sheet.get_width() -
						                                           self.sprite_sheet.get_width())
						self.sprite_sheet_offset.y = pg.math.clamp(self.sprite_sheet_offset.y, 0,
						                                           self.sprite_sheet_zoom *
						                                           self.sprite_sheet.get_height() -
						                                           self.sprite_sheet.get_height())
			elif event.type == MOUSEWHEEL:
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
	main = Main((32, 32))
	main.run()
