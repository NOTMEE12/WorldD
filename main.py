import os
import sys
import json
import tkinter
from tkinter import filedialog
import pygame as pg
from pygame.locals import *
import tomllib


def draw_rect(surf, color, rect, width=0, *args):
	"""custom function to draw rect with negative size"""
	new_rect = pg.Rect(
		rect.x + (rect.w if rect.w < 0 else 0),
		rect.y + (rect.h if rect.h < 0 else 0),
		rect.w - ((rect.w * 2) if rect.w < 0 else 0),
		rect.h - ((rect.h * 2) if rect.h < 0 else 0)
	)
	pg.draw.rect(surf, color, new_rect, width, *args)


class Key:
	
	def __init__(self, keycode: str, mod: str):
		self.key = pg.key.key_code(keycode)
		self.mod = self.get_mode(mod)
	
	@staticmethod
	def mode_name(mod: int) -> str:
		mods = {
			KMOD_SHIFT: 'shift',
			KMOD_LSHIFT: 'lshift',
			KMOD_RSHIFT: 'rshift',
			KMOD_CTRL: 'ctrl',
			KMOD_LCTRL: 'lctrl',
			KMOD_RCTRL: 'rctrl',
			KMOD_ALT: 'alt',
			KMOD_LALT: 'lalt',
			KMOD_RALT: 'ralt',
			KMOD_CAPS: 'caps',
			KMOD_NUM: 'num',
			KMOD_GUI: 'gui',
			KMOD_LGUI: 'lgui',
			KMOD_RGUI: 'rgui',
			KMOD_NONE: 'NO MODE'
		}
		return mods[mod] if mod in mods else 'MODE UNKNOWN'
	
	@staticmethod
	def get_mode(mod: str) -> int:
		mods = {
			'shift': KMOD_SHIFT,
			'lshift': KMOD_LSHIFT,
			'rshift': KMOD_RSHIFT,
			'ctrl': KMOD_CTRL,
			'lctrl': KMOD_LCTRL,
			'rctrl': KMOD_RCTRL,
			'alt': KMOD_ALT,
			'lalt': KMOD_LALT,
			'ralt': KMOD_RALT,
			'caps': KMOD_CAPS,
			'num': KMOD_NUM,
		}
		return mods[mod] if mod in mods else KMOD_NONE
	
	def __eq__(self, other):
		return other.key == self.key and ((other.mod & self.mod) if self.mod != KMOD_NONE else (other.mod == self.mod))


class Bindings:
	
	def __init__(self, bindings):
		self.SCALE_TILE_UP = Key(*bindings['SCALE-TILE-DOWN'])
		self.SCALE_TILE_DOWN = Key(*bindings['SCALE-TILE-UP'])
		self.TOGGLE_FULLSCREEN = Key(*bindings['TOGGLE-FULLSCREEN'])
		self.EXIT = Key(*bindings['EXIT'])
		self.SAVE = Key(*bindings['SAVE'])
		self.LOAD = Key(*bindings['LOAD'])
		self.TILE_LOOKUP_REMOVAL = Key(*bindings['TILE-LOOKUP-REMOVAL'])
		self.SELECTION_ACCEPT = Key(*bindings['SELECTION-ACCEPT'])
		self.CANCEL_SELECTION = Key(*bindings['CANCEL-SELECTION'])


class Options:
	
	def __init__(self, file):
		with open(file, 'rb') as file:
			self.options = tomllib.load(file)
			"""====[ GUI ]===="""
			self.SHOW_EXIT = self.options['SHOW-EXIT']
			self.HEADER_FONT = self.options['HEADER-FONT']
			self.TEXT_FONT = self.options['TEXT-FONT']
			self.SCROLL_SENSITIVITY = self.options['SCROLL-SENSITIVITY']
			self.MOUSE_SENSITIVITY = self.options['MOUSE-SENSITIVITY']
			self.FPS = self.options['FPS']


class Main:
	
	def __init__(self):
		pg.init()
		tkinter.Tk().withdraw()
		"""====[ WINDOW ]===="""
		self.win = pg.Vector2(pg.display.get_desktop_sizes()[0])
		self.display = pg.display.set_mode(self.win, RESIZABLE)
		self.clock = pg.Clock()
		self.events = ()
		self.Options = Options('options.toml')
		self.Bindings = Bindings(self.Options.options)
		"""====[ PROJECTS ]===="""
		self.path = pg.system.get_pref_path('NotMEE12', 'WorldD')
		if not os.path.exists(self.path + '\\recent.txt'):
			self.recent = []
		else:
			with open(self.path + '\\recent.txt') as recent:
				self.recent = list(recent.read().split('\n'))
		self.projects: list[Project | Welcome] = [Welcome(self)]
		self.popups = []
		self.selected = 0

	def refresh(self):
		self.display.fill(0)
		pg.draw.rect(self.display, (120, 120, 120), pg.Rect(0, 0, self.display.get_width(), 50))
		self.projects[self.selected].render()
		for popup in self.popups:
			popup.render()
		if self.Options.SHOW_EXIT:
			pg.draw.rect(self.display, (180, 180, 180), pg.Rect(self.display.get_width()-25, 0, 25, 25), border_radius=15, width=5)
			pg.draw.line(self.display, (180, 180, 180), (self.display.get_width()-20, 5), (self.display.get_width()-5, 20), 5)
			pg.draw.line(self.display, (180, 180, 180), (self.display.get_width()-20, 20), (self.display.get_width()-5, 5), 5)
		pg.display.flip()
		self.clock.tick(self.Options.FPS)
	
	def exit(self):
		pg.quit()
		with open(self.path + '\\recent.txt', 'a') as recent:
			recent.truncate(0)
			recent.writelines(self.recent)
		sys.exit()
	
	def eventHandler(self):
		self.events = pg.event.get()
		for event in self.events:
			if event.type == QUIT:
				self.exit()
			elif event.type == DROPFILE:
				new_project = Project(self, (32, 32))
				new_project.load(event.file)
				self.projects.append(new_project)
				self.selected = len(self.projects)-1
			elif event.type == MOUSEBUTTONDOWN:
				if event.button == 1:
					if pg.Rect(self.display.get_width()-50, 0, 50, 50).collidepoint(event.pos):
						self.exit()
			elif event.type == KEYDOWN:
				if event == self.Bindings.EXIT:
					self.exit()
				elif event == self.Bindings.TOGGLE_FULLSCREEN:
					pg.display.toggle_fullscreen()
		if not self.popups:
			self.projects[self.selected].eventHandler()
		else:
			for popup in self.popups:
				popup.eventHandler()
		
	def run(self):
		while True:
			self.refresh()
			if self.eventHandler():
				return 1
			pg.display.set_caption("{:.2f}".format(self.clock.get_fps()))


class Project:

	def __init__(self, main: Main, tile_size, load: str | bool = False):
		"""creates new project"""
		
		self.main = main
		
		"""====[ WINDOW ]===="""
		self.win = main.win
		self.display = main.display
		"""====[ GUI ]===="""
		self.offset = pg.Vector2(tile_size[0] * 2, tile_size[1] * 2)
		self.sidebar = pg.Rect(0, 0, self.win[0] / 3, self.win[1])
		self.text = pg.font.SysFont(self.main.Options.TEXT_FONT, 30, False, False)
		self.header = pg.font.SysFont(self.main.Options.HEADER_FONT, 35, True, False)
		self.save_selection = self.header.render("Save selection? (name/ESC)", True, (250, 250, 250))
		self.sprite_sheet = None
		"""====[ CUSTOMIZABLE ]===="""
		self.destination = None
		self.path = None
		self.sprite_sheet_path = None
		self.tiles = {}
		self.grid = {}
		filetypes = [('image', '*.png'), ('image', '*.jpg')]
		if type(load) is bool:
			if load:
				filetypes = [('world', '*.world')]
			file = filedialog.askopenfile(filetypes=filetypes)
			if file is None:
				raise IOError
			if file.name.split('.')[-1].lower() != 'world':
				self.sprite_sheet = pg.image.load(file.name).convert_alpha()
				self.sprite_sheet_path = file.name
			else:
				self.path = file.name
				self.load()
			file.close()
		else:
			file = open(load)
			if file is None:
				raise IOError
			if file.name.split('.')[-1].lower() != 'world':
				self.sprite_sheet = pg.image.load(file.name).convert_alpha()
				self.sprite_sheet_path = file.name
			else:
				self.path = file.name
				self.load()
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
		self.sprite_sheet_zoom = 1
		self.sprite_sheet_offset = pg.Vector2(0, 0)

	def load(self, path=None):
		if path is not None:
			self.path = path
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
		
	def save(self):
		if self.destination is None:
			if self.path is None:
				self.destination = filedialog.asksaveasfile('a+', defaultextension='.world')
				self.path = self.destination.name
			else:
				self.destination = open(self.path, 'a+')
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
		if self.path not in self.main.recent:
			self.main.recent.append(self.path)
	
	def render(self):
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
		for pos, name in self.grid.copy().items():
			try:
				tile = self.tiles[name]
			except KeyError:
				del self.grid[pos]
				continue
			size = self.tile_size * self.zoom
			x = bold_x + size[0] * pos[0]
			y = bold_y + size[1] * pos[1]
			self.display.blit(pg.transform.scale(self.sprite_sheet.subsurface(tile), size), (x, y))
		# ===[ BOLD LINES ]===
		pg.draw.line(self.display, "white", (bold_x, 0), (bold_x, self.display.get_height()), 5)
		pg.draw.line(self.display, "white", (0, bold_y), (self.display.get_width(), bold_y), 5)
		pg.draw.circle(self.display, "white", (bold_x, bold_y), 15)
		"""====[ SIDEBAR ]===="""
		rect = self.sprite_sheet.get_rect(left=self.sidebar.centerx - self.sprite_sheet.get_width() / 2,
		                                  top=self.sidebar.centery)
		pg.draw.rect(self.display, (10, 10, 10), self.sidebar)
		pg.draw.rect(self.display, (32, 32, 32), rect)
		sp_sheet = pg.transform.scale_by(self.sprite_sheet, self.sprite_sheet_zoom)
		draw_rect(sp_sheet, self.selection_color, pg.Rect(
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
	
	def eventHandler(self):
		for event in self.main.events:
			if event.type == KEYDOWN:
				if event == self.main.Bindings.SCALE_TILE_UP:
					self.tile_size *= 2
				elif event == self.main.Bindings.SCALE_TILE_DOWN:
					self.tile_size /= 2
				elif event == self.main.Bindings.SAVE:
					self.save()
				elif event == self.main.Bindings.LOAD:
					self.path = None
					self.destination = None
					self.load()
				elif event == self.main.Bindings.TILE_LOOKUP_REMOVAL:
					if self.selected_tile is not None:
						del self.tiles[self.selected_tile]
						self.selected_tile = None
				elif self.save_selection != (0, 0, 0, 0):
					if event == self.main.Bindings.CANCEL_SELECTION:
						self.selection = pg.Rect(0, 0, 0, 0)
						self.selection_name = ""
					elif event.key == K_BACKSPACE:
						self.selection_name = self.selection_name[:-1]
					elif event == self.main.Bindings.SELECTION_ACCEPT:
						self.tiles[self.selection_name] = tuple(self.selection.copy())
						self.selection = pg.Rect(0, 0, 0, 0)
						self.selection_name = ""
					elif not event.unicode.isascii():
						pass
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
							(event.pos[0] - (
										self.sidebar.centerx - self.sprite_sheet.get_width() / 2 - self.sprite_sheet_offset.x)) / self.sprite_sheet_zoom - self.selection.x + 1,
							self.selection.x - self.sprite_sheet.get_width(),
							self.sprite_sheet.get_width() - self.selection.x
						)
						self.selection.h = pg.math.clamp(
							(event.pos[
								 1] - self.sidebar.centery + self.sprite_sheet_offset.y) / self.sprite_sheet_zoom - self.selection.y + 1,
							self.selection.y - self.sprite_sheet.get_height(),
							self.sprite_sheet.get_height() - self.selection.y
						)
			elif event.type == MOUSEMOTION:
				if event.pos[0] > self.sidebar.right:
					if event.buttons[1]:
						self.offset += pg.Vector2(event.rel) * self.main.Options.MOUSE_SENSITIVITY / self.zoom
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
				                                top=self.sidebar.centery).collidepoint(event.pos):
					if event.buttons[1]:
						self.sprite_sheet_offset -= pg.Vector2(event.rel) * self.main.Options.MOUSE_SENSITIVITY
						self.sprite_sheet_offset.x = pg.math.clamp(self.sprite_sheet_offset.x, 0,
						                                           self.sprite_sheet_zoom *
						                                           self.sprite_sheet.get_width() -
						                                           self.sprite_sheet.get_width())
						self.sprite_sheet_offset.y = pg.math.clamp(self.sprite_sheet_offset.y, 0,
						                                           self.sprite_sheet_zoom *
						                                           self.sprite_sheet.get_height() -
						                                           self.sprite_sheet.get_height())
					if self.sidebar.centerx + self.sprite_sheet.get_width() / 2 \
							>= event.pos[0] >= \
							self.sidebar.centerx - self.sprite_sheet.get_width() / 2 and \
							event.pos[1] >= self.sidebar.centery:
						if event.buttons[0]:
							w = (event.pos[0]-
							     (self.sidebar.centerx-self.sprite_sheet.get_width()/2-self.sprite_sheet_offset.x))\
							    /self.sprite_sheet_zoom-self.selection.x
							if w > 0:
								w += 1
							else:
								w -= 1
							self.selection.w = pg.math.clamp(
									w,
									-self.sprite_sheet.get_width()+self.selection.x,
								self.sprite_sheet.get_width()-self.selection.x
								)
							h = (event.pos[1] - self.sidebar.centery + self.sprite_sheet_offset.y) / self.sprite_sheet_zoom-self.selection.y
							if h > 0:
								h += 1
							else:
								h -= 1
							self.selection.h = pg.math.clamp(
								h,
								-self.sprite_sheet.get_height()+self.selection.y,
								self.sprite_sheet.get_height()-self.selection.y
							)
			elif event.type == MOUSEWHEEL:
				if pg.mouse.get_pos()[0] > self.sidebar.right:
					self.zoom += event.y * self.main.Options.SCROLL_SENSITIVITY
					self.zoom = pg.math.clamp(self.zoom, 0.75, 5)
				else:
					self.sprite_sheet_zoom += event.y * self.main.Options.SCROLL_SENSITIVITY
					if self.sprite_sheet_zoom < 1 or self.sprite_sheet_zoom > 15:
						self.sprite_sheet_zoom = pg.math.clamp(self.sprite_sheet_zoom, 1, 15)


class Welcome:
	
	def __init__(self, main: Main):
		self.main = main
		self.display = main.display
		"""====[ TEXT ]===="""
		self.header = pg.font.SysFont(self.main.Options.HEADER_FONT, 100, True, False)
		self.text = pg.font.SysFont(self.main.Options.TEXT_FONT, 40, False, False)
		self.text_und = pg.font.SysFont(self.main.Options.TEXT_FONT, 40, False, False)
		self.text_und.set_underline(True)
		
		self.texts = {
			'#Welcome': self.header.render('Welcome', True, (200, 200, 200)),
			'New project': self.text.render('New project', True, (200, 200, 200)),
			'Load project': self.text.render('Load project', True, (200, 200, 200)),
			'__New_project__': self.text_und.render('New project', True, (200, 200, 200)),
			'__Load_project__': self.text_und.render('Load project', True, (200, 200, 200))
		}
	
	def render(self):
		""""""  # empty doc string
		"""====[ CONFIG ]===="""
		mouse_pos = pg.mouse.get_pos()
		dis_rect = self.display.get_rect()
		
		"""====[ WELCOME ]===="""
		self.display.fill(0)
		self.display.blit(self.texts['#Welcome'], self.texts['#Welcome'].get_rect(center=(dis_rect.w/4, dis_rect.h/6)))
		
		"""====[ PROJECTS ]===="""
		New = self.texts['New project']
		New_rect = New.get_rect(centerx=dis_rect.w/4, top=dis_rect.h/3)
		Load = self.texts['Load project']
		Load_rect = Load.get_rect(centerx=dis_rect.w/4, top=dis_rect.h/3+New_rect.height*1.5)
		if New_rect.collidepoint(mouse_pos):
			New = self.texts['__New_project__']
		if Load_rect.collidepoint(mouse_pos):
			Load = self.texts['__Load_project__']
		self.display.blit(New, New_rect.topleft)
		self.display.blit(Load, Load_rect.topleft)
		
		"""====[ RECENT ]===="""
		rect = pg.Rect(25, dis_rect.h/2, dis_rect.w/2-25, dis_rect.h/2)
		pg.draw.rect(self.display, (20, 20, 20), rect, border_radius=15)
		for row, text in enumerate(self.main.recent):
			pos = (rect.left + self.text.size('  ')[0], rect.top+row*self.text.get_height())
			txt = self.text.render(text, True, (150, 150, 150))
			if txt.get_rect(topleft=pos).collidepoint(mouse_pos):
				txt = self.text_und.render(text, True, (150, 150, 150))
			self.display.blit(txt, pos)

	def eventHandler(self):
		for event in self.main.events:
			if event.type == MOUSEBUTTONDOWN:
				if event.button == 1:
					dis_rect = self.display.get_rect()
					New_rect = self.texts['New project'].get_rect(centerx=dis_rect.w / 4, top=dis_rect.h / 3)
					Load_rect = self.texts['Load project'].get_rect(
						centerx=dis_rect.w / 4, top=dis_rect.h / 3 + New_rect.height * 1.5
					)
					if New_rect.collidepoint(event.pos):
						# self.main.popups.append(Popup(self.main, self.display, 'select type of world', ('isometric', '2d or 2.5d')))
						try:
							self.main.projects.append(Project(self.main, (32, 32)))
							self.main.selected = len(self.main.projects)-1
						except IOError:
							pass
					elif Load_rect.collidepoint(event.pos):
						try:
							self.main.projects.append(Project(self.main, (32, 32), load=True))
							self.main.selected = len(self.main.projects)-1
						except IOError:
							pass
					else:
						rect = pg.Rect(25, dis_rect.h / 2, dis_rect.w / 2 - 25, dis_rect.h / 2)
						for row, text in enumerate(self.main.recent):
							txt = self.text.render(text, True, (150, 150, 150))
							txt = txt.get_rect(topleft=(rect.left + self.text.size('  ')[0], rect.top+row*self.text.get_height()))
							if txt.collidepoint(event.pos):
								try:
									self.main.projects.append(Project(self.main, (32, 32), load=text))
									self.main.selected = len(self.main.projects)-1
								except IOError:
									pass


class Popup:
	
	def __init__(self, main, display, question, options):
		self.main = main
		self.display = display
		self.header = pg.font.SysFont(self.main.Options.HEADER_FONT, 60, True, False)
		self.text = pg.font.SysFont(self.main.Options.TEXT_FONT, 30, False, False)
		self.text_hover = pg.font.SysFont(self.main.Options.TEXT_FONT, 30, True, False)
		
		self.question = self.header.render(question, True, (200, 200, 200))
		self.options = {option: self.text.render(option, True, (200, 200, 200)) for option in options}
		self.options_hover = {option: self.text_hover.render(option, True, (200, 200, 200)) for option in options}
		self.answer = None
		self.pos = pg.Vector2((self.display.get_width()-self.question.get_width())/2-100, self.display.get_height()/3)
	
	def render(self):
		rect = pg.Rect(self.pos, (self.question.get_width()+200, len(self.options.keys())*150))
		question_rect = self.question.get_rect(centerx=rect.centerx, top=rect.top)
		pg.draw.rect(self.display, (10, 10, 10), rect, border_radius=15)
		pg.draw.rect(self.display, (100, 100, 100), rect, border_radius=15, width=2)
		pg.draw.line(self.display, (100, 100, 100), (rect.x+25, question_rect.bottom+10), (rect.right-25, question_rect.bottom+10))
		self.display.blit(self.question, question_rect)
		for en, (name, texture) in enumerate(self.options.items()):
			rect = pg.Rect((rect.centerx-texture.get_width()/2, rect.top+rect.h/(len(self.options.keys())+1*en)), texture.get_size())
			if rect.collidepoint(pg.mouse.get_pos()):
				self.display.blit(self.options_hover[name], rect)
			else:
				self.display.blit(texture, rect)

	def eventHandler(self):
		pass


if __name__ == '__main__':
	Main().run()
