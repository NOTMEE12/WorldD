import pygame as pg
from pygame.locals import *
import tkinter
from tkinter import filedialog
import json
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
		self.text = pg.font.SysFont('Arial', 30, False, False)
		self.header = pg.font.SysFont('Arial', 35, True, False)
		self.save_selection = self.header.render("Save selection? (name/ESC)", True, (250, 250, 250))
		self.sprite_sheet = None
		"""===[ CUSTOMIZABLE ]==="""
		self.destination = None
		self.path = None
		self.sprite_sheet_path = None
		self.tiles = {}
		self.grid = {}
		try:
			file = filedialog.askopenfile(filetypes=[('image/world', '*.png'), ('image/world', '*.jpg'), ('image/world', '*.world')])
			if file.name.split('.')[-1].lower() != 'world':
				self.sprite_sheet = pg.image.load(file.name).convert_alpha()
				self.sprite_sheet_path = file.name
			else:
				self.path = file.name
				self.load()
			file.close()
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
		self.tile_size = pg.Vector2(tile_size)
		self.zoom = 1
		self.mouse_sensitivity = 1
		self.scroll_sensitivity = .1
		self.sprite_sheet_zoom = 1
		self.sprite_sheet_offset = pg.Vector2(0, 0)
	
	def load(self):
		if self.destination is None:
			if self.path is None:
				self.destination = filedialog.askopenfile('r', defaultextension='.world')
				self.path = self.destination.name
			else:
				self.destination = open(self.path)
		data = json.load(self.destination)
		self.sprite_sheet_path = data['img']
		self.sprite_sheet = pg.image.load(self.sprite_sheet_path).convert_alpha()
		self.tiles = {tile: tuple(map(int, pos.lstrip('(').rstrip(')').split(','))) for pos, tile in data['data'].items()}
		self.grid = {tuple(map(int, pos.split(','))): tile for pos, tile in data['grid'].items()}
		self.destination.close()
		self.destination = None
	
	def refresh(self):
		self.display.fill(0)
		bold_x = self.offset[0] * self.zoom - self.tile_size[0] + self.sidebar.right
		bold_y = self.offset[1] * self.zoom - self.tile_size[1]
		for idx in range(int(max(self.display.get_width() / self.tile_size[0], self.display.get_height() /
		                                                                       self.tile_size[1]) / self.zoom)):
			x = idx * self.tile_size[0] * self.zoom + self.offset[0] % self.tile_size[0] * self.zoom - \
			    self.tile_size[0] + self.sidebar.right
			pg.draw.line(self.display, self.grid_color, (x, 0), (x, self.display.get_height()), 1)
			x2 = self.sidebar.right - self.offset[0] % self.tile_size[0] - self.tile_size[0]
			y = idx * self.tile_size[1] * self.zoom + self.offset[1] % self.tile_size[1] * self.zoom - self.tile_size[0]
			pg.draw.line(self.display, self.grid_color, (x2, y), (self.display.get_width(), y), 1)
		# ===[ GRID ]===
		for pos, name in self.grid.items():
			size = self.tile_size * self.zoom
			x = bold_x + size[0] * pos[0]
			y = bold_y + size[1] * pos[1]
			self.display.blit(pg.transform.scale(self.sprite_sheet.subsurface(self.tiles[name]), size), (x, y))
		# ===[ BOLD LINES ]===
		pg.draw.line(self.display, "white", (bold_x, 0), (bold_x, self.display.get_height()), 5)
		pg.draw.line(self.display, "white", (0, bold_y), (self.display.get_width(), bold_y), 5)
		pg.draw.circle(self.display, "white", (bold_x, bold_y), 15)
		"""===[ SIDEBAR ]==="""
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
		for idx, (name, tile) in enumerate(self.tiles.items()):
			pos = pg.Vector2(idx % 7 * 69+5, idx//7*109+5+self.scroll)
			text = self.text.render(name, False, (120, 120, 120), wraplength=55)
			if name == self.selected_tile:
				pg.draw.rect(tiles, self.selected_tile_color, pg.Rect(pos.x-4, pos.y-4, 72, 72))
			tiles.blit(pg.transform.scale(self.sprite_sheet.subsurface(tile), (64, 64)), pos)
			tiles.blit(text, (idx % 7 * 69+5+32-text.get_width()/2, idx//7*109+5+64+self.scroll))
		self.display.blit(tiles, (0, 0))
		tile_size = self.header.render(f'{self.tile_size[0]}x{self.tile_size[1]}', True, (200, 200, 200))
		self.display.blit(tile_size, (rect.centerx-tile_size.get_width()/2, rect.bottom + 100))
		pg.display.flip()
		self.clock.tick(self.FPS)
	
	def save(self):
		if self.destination is None:
			if self.path is None:
				self.destination = filedialog.asksaveasfile('a+', defaultextension='.world')
				self.path = self.destination.name
			else:
				self.destination = open(self.path, 'a+')
			print(self.destination.name)
		self.destination.seek(0)
		self.destination.truncate(0)
		self.destination.write(
			json.dumps(
				{
					'grid':  {f"{pos[0]},{pos[1]}": tile for pos, tile in self.grid.items()},
					'data': {f"{pos}": tile for tile, pos in self.tiles.items()},
					'img': self.sprite_sheet_path
				}
			)
		)
		self.destination.close()
		self.destination = None
			
	def eventHandler(self):
		for event in pg.event.get():
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
				elif event.mod & KMOD_CTRL and event.key == K_s:
					self.save()
				elif event.mod & KMOD_CTRL and event.key == K_o:
					self.path = None
					self.destination = None
					self.load()
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
						print(self.tiles)
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
								(event.pos[1] - self.sidebar.centery + self.sprite_sheet_offset.y) / self.sprite_sheet_zoom,
								0, self.sprite_sheet.get_height()
							)
							self.selection.w = 0
							self.selection.h = 0
						elif self.sidebar.collidepoint(event.pos):
							for idx, (name, tile) in enumerate(zip(self.tiles.keys(), self.tiles.values())):
								if pg.Rect((idx % 7 * 69+5, idx//7*109+5+self.scroll), (64, 64)).collidepoint(event.pos):
									self.selected_tile = name
									break
					else:
						if self.selected_tile is not None:
							bold_x = self.offset[0] * self.zoom - self.tile_size[0] + self.sidebar.right
							bold_y = self.offset[1] * self.zoom - self.tile_size[1]
							pos = (
								int((event.pos[0]-bold_x)//(self.tile_size[0]*self.zoom)),
								int((event.pos[1]-bold_y)//(self.tile_size[1]*self.zoom))
							)
							self.grid[pos] = self.selected_tile
			elif event.type == MOUSEBUTTONUP:
				if event.button == 1:
					if self.sidebar.centerx + self.sprite_sheet.get_width() / 2 \
							>= event.pos[0] >= \
							self.sidebar.centerx - self.sprite_sheet.get_width() / 2 and \
							event.pos[1] >= self.sidebar.centery:
						self.selection.w = pg.math.clamp(
								(event.pos[0]-(self.sidebar.centerx-self.sprite_sheet.get_width()/2-self.sprite_sheet_offset.x))/self.sprite_sheet_zoom-self.selection.x+1,
								0, self.sprite_sheet.get_width()
							)
						self.selection.h = pg.math.clamp(
								(event.pos[1] - self.sidebar.centery + self.sprite_sheet_offset.y) / self.sprite_sheet_zoom-self.selection.y+1,
								0, self.sprite_sheet.get_height()
							)
			elif event.type == MOUSEMOTION:
				if event.pos[0] > self.sidebar.right:
					if event.buttons[1]:
						self.offset += pg.Vector2(event.rel) * self.mouse_sensitivity / self.zoom
					elif event.buttons[0]:
						if self.selected_tile is not None:
							bold_x = self.offset[0] * self.zoom - self.tile_size[0] + self.sidebar.right
							bold_y = self.offset[1] * self.zoom - self.tile_size[1]
							pos = (
								int((event.pos[0] - bold_x) // (self.tile_size[0] * self.zoom)),
								int((event.pos[1] - bold_y) // (self.tile_size[1] * self.zoom))
							)
							self.grid[pos] = self.selected_tile
				elif self.sprite_sheet.get_rect(left=self.sidebar.centerx - self.sprite_sheet.get_width() / 2,
				                                top=self.sidebar.centery).collidepoint(event.pos[0], event.pos[1]):
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
					if self.sprite_sheet_zoom < 1 or self.sprite_sheet_zoom > 15:
						self.sprite_sheet_zoom = self.sprite_sheet_zoom = pg.math.clamp(self.sprite_sheet_zoom, 1, 15)
					else:
						self.sprite_sheet_offset += pg.Vector2(
							((self.sprite_sheet.get_width() * self.sprite_sheet_zoom - self.sprite_sheet.get_width()) / (self.tile_size[0] * self.sprite_sheet_zoom)) * event.y,
							((self.sprite_sheet.get_height() * self.sprite_sheet_zoom - self.sprite_sheet.get_height()) / (self.tile_size[1] * self.sprite_sheet_zoom)) * event.y
						)
						self.sprite_sheet_offset.x = pg.math.clamp(self.sprite_sheet_offset.x, 0,
						                                           self.sprite_sheet_zoom *
						                                           self.sprite_sheet.get_width() -
						                                           self.sprite_sheet.get_width())
						self.sprite_sheet_offset.y = pg.math.clamp(self.sprite_sheet_offset.y, 0,
						                                           self.sprite_sheet_zoom *
						                                           self.sprite_sheet.get_height() -
						                                           self.sprite_sheet.get_height())
					
					
	def run(self):
		while True:
			self.refresh()
			if self.eventHandler():
				return 1
			pg.display.set_caption("{:.2f}".format(self.clock.get_fps()))


if __name__ == '__main__':
	main = Main((32, 32))
	main.run()
