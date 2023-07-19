import os
import sys
import json
import tkinter
from tkinter import filedialog
import pygame as pg
from pygame.locals import *
import tomllib

pg.init()
tkinter.Tk().withdraw()


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
		return other.key == self.key and ((other.mod & self.mod) if self.mod != KMOD_NONE else True)


class Bindings:
	
	def __init__(self, bindings):
		self.SCALE_TILE_UP = Key(*bindings['SCALE-TILE-UP'])
		self.SCALE_TILE_DOWN = Key(*bindings['SCALE-TILE-DOWN'])
		self.TOGGLE_FULLSCREEN = Key(*bindings['TOGGLE-FULLSCREEN'])
		self.EXIT = Key(*bindings['EXIT'])
		self.SAVE = Key(*bindings['SAVE'])
		self.LOAD = Key(*bindings['LOAD'])
		self.TILE_LOOKUP_REMOVAL = Key(*bindings['TILE-LOOKUP-REMOVAL'])
		self.SELECTION_ACCEPT = Key(*bindings['SELECTION-ACCEPT'])
		self.CANCEL_SELECTION = Key(*bindings['CANCEL-SELECTION'])
		self.PROJECT_SELECTION_LEFT = Key(*bindings['PROJECT-SELECTION-LEFT'])
		self.PROJECT_SELECTION_RIGHT = Key(*bindings['PROJECT-SELECTION-RIGHT'])
		self.RECT = Key(*bindings['RECT'])
		self.BRUSH = Key(*bindings['BRUSH'])


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
			self.TOP_OFFSET = self.options['TOP-OFFSET']


class Main:
	
	def __init__(self):
		""""""
		"""====[ WINDOW ]===="""
		self.win = pg.Vector2(pg.display.get_desktop_sizes()[0])
		self.display = pg.display.set_mode(self.win, RESIZABLE)
		self.clock = pg.Clock()
		self.events = ()
		self.work_path = os.path.dirname(os.path.abspath(__file__)) + '\\'
		self.Options = Options(self.work_path + 'options.toml')
		self.Bindings = Bindings(self.Options.options)
		"""====[ PROJECTS ]===="""
		self.Header = pg.font.SysFont(self.Options.HEADER_FONT, 50, True, False)
		self.SmallerHeader = pg.font.SysFont(self.Options.HEADER_FONT, 30, False, False)
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
		
		self.projects[self.selected].render()
		"""====[ PROJECT NAME ]===="""
		pg.draw.rect(self.display, (5, 5, 5), (0, 0, self.display.get_width(), self.Options.TOP_OFFSET))
		main_project = self.Header.render('< ' + self.projects[self.selected].path.split('/')[-1] + ' > ', True, (200, 200, 200))
		main_pos = ((self.display.get_width()-main_project.get_width())/2, (self.Options.TOP_OFFSET-main_project.get_height())/2)
		self.display.blit(main_project, main_pos)
		if self.selected > 0:
			for en, project in enumerate(self.projects[:self.selected]):
				name = self.SmallerHeader.render(project.path.split('/')[-1], True, (200, 200, 200))
				pos = (main_pos[0] - sum(self.SmallerHeader.size(' '+p.path.split('/')[-1]+' ')[0] for p in self.projects[:en+1]), (self.Options.TOP_OFFSET-name.get_height())/2 )
				self.display.blit(name, pos)
		if self.selected < len(self.projects)-1:
			for en, project in enumerate(self.projects[self.selected+1:]):
				name = self.SmallerHeader.render(project.path.split('/')[-1], True, (200, 200, 200))
				pos = (main_pos[0] + main_project.get_width() + sum(self.SmallerHeader.size(' '+p.path.split('/')[-1]+' ')[0] for p in self.projects[self.selected+1:en-1]), (self.Options.TOP_OFFSET-name.get_height())/2 )
				self.display.blit(name, pos)
		
		self.projects[self.selected].render_on_top()
		
		"""====[ POPUPS ]===="""
		# for popup in self.popups:
		# 	popup.render()
		"""====[ EXIT ]===="""
		if self.Options.SHOW_EXIT:
			pg.draw.rect(self.display, (180, 180, 180), pg.Rect(self.display.get_width()-25, 0, 25, 25), border_radius=15, width=5)
			pg.draw.line(self.display, (180, 180, 180), (self.display.get_width()-20, 5), (self.display.get_width()-5, 20), 5)
			pg.draw.line(self.display, (180, 180, 180), (self.display.get_width()-20, 20), (self.display.get_width()-5, 5), 5)
	
	def exit(self):
		pg.quit()
		with open(self.path + '\\recent.txt', 'a') as recent:
			recent.truncate(0)
			recent.writelines(self.recent)
		for project in self.projects:
			project.save()
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
					if pg.Rect(self.display.get_width()-50, 0, 50, 50).collidepoint(event.pos) and self.Options.SHOW_EXIT:
						self.exit()
			elif event.type == KEYDOWN:
				if event == self.Bindings.EXIT:
					self.exit()
				elif event == self.Bindings.TOGGLE_FULLSCREEN:
					pg.display.toggle_fullscreen()
				elif event == self.Bindings.PROJECT_SELECTION_LEFT:
					self.selected -= 1
					self.selected = pg.math.clamp(self.selected, 0, len(self.projects)-1)
				elif event == self.Bindings.PROJECT_SELECTION_RIGHT:
					self.selected += 1
					self.selected = pg.math.clamp(self.selected, 0, len(self.projects)-1)
		if not self.popups:
			self.projects[self.selected].eventHandler()
		else:
			for popup in self.popups:
				popup.eventHandler()
		
	def run(self):
		while True:
			self.refresh()
			pg.display.flip()
			self.clock.tick(self.Options.FPS)
			if self.eventHandler():
				return 1
			if self.projects[self.selected].path != 'Welcome':
				tiles = f'{len(self.projects[self.selected].grid.keys())} tiles | '
			else:
				tiles = ''
			path = self.projects[self.selected].path
			pg.display.set_caption(f'{path} - WorldD | {tiles}{self.clock.get_fps():.2f} FPS')


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
		
		"""====[ TOOLS ]===="""
		self.tool = 'brush'
		self.rect = [False, pg.Rect(0, 0, 0, 0)]
		
		"""====[ CONFIG ]===="""
		
		"""====[ CUSTOMIZABLE ]===="""
		self.destination = None
		self.path = None
		self.tiles = {}
		self.grid = {}
		if load is False:
			filetypes = [('image', '*.png'), ('image', '*.jpg')]
			file = filedialog.askopenfile(filetypes=filetypes)
			if file is None:
				raise IOError
			self.path = file.name
			self.sprite_sheet = self.SpriteSheet(file.name, self.display, self)
		elif load is True:
			filetypes = [('world', '*.world')]
			file = filedialog.askopenfile(filetypes=filetypes)
			if file is None:
				raise IOError
			else:
				self.load(file.name)
			file.close()
		else:
			file = open(load)
			if file is None:
				raise IOError
			if file.name.split('.')[-1].lower() != 'world':
				self.sprite_sheet = self.SpriteSheet(file.name, self.display, self)
			else:
				self.path = file.name
				self.load(file.name)
		self.selected_tile = None
		self.scroll = 0
		self.grid_color = (255, 255, 255)
		self.selected_tile_color = (255, 255, 255)
		self.tile_size = pg.Vector2(tile_size)
		self.zoom = 1
		
		"""====[ CACHED ]===="""
		self.bold = pg.Vector2(self.offset[0] * self.zoom - self.tile_size[0] + self.sidebar.right,
		                       self.offset[1] * self.zoom - self.tile_size[1])
		self.tile_cache = {}
	
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
		self.sprite_sheet = self.SpriteSheet(data['img'], self.display, self)
		self.tiles = {tile: tuple(map(int, pos.lstrip('(').rstrip(')').split(','))) for pos, tile in data['data'].items()}
		self.grid = {tuple(map(int, pos.split(','))): tile for pos, tile in data['grid'].items()}
		self.destination.close()
		self.destination = None
		print(self.path, self.sprite_sheet.path)
	
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
					'img': self.sprite_sheet.path
				}
			)
		)
		self.destination.close()
		self.destination = None
		if self.path not in self.main.recent:
			self.main.recent.append(self.path)
		
	def display_hover_tile(self):
		if self.selected_tile is not None:
			dis_rect = self.display.get_rect()
			pos = self.current_block(pg.mouse.get_pos())
			size = (self.tile_size.x * self.zoom, self.tile_size.y * self.zoom)
			x = self.bold.x + size[0] * pos[0]
			y = self.bold.y + size[1] * pos[1]
			if pg.Rect(0, self.main.Options.TOP_OFFSET, dis_rect.w, dis_rect.h - self.main.Options.TOP_OFFSET) \
					.colliderect(pg.Rect((x, y), size)):
				self.display.blit(pg.transform.scale(self.sprite_sheet.img.subsurface(self.tiles[self.selected_tile]), size), (x, y))
	
	def draw_hover_rect(self):
		if self.selected_tile is not None and self.rect[0]:
			dis_rect = self.display.get_rect()
			size = (self.tile_size.x * self.zoom, self.tile_size.y * self.zoom)
			
			rect: pg.Rect = self.rect[1]
			
			left = rect.left if rect.w > 0 else rect.right-1
			right = rect.right if rect.w > 0 else rect.left+1
			top = rect.top if rect.h > 0 else rect.bottom-1
			bottom = rect.bottom if rect.h > 0 else rect.top+1

			for x_ in range(left, right):
				for y_ in range(top, bottom):
					x = self.bold.x + size[0] * x_
					y = self.bold.y + size[1] * y_
					if pg.Rect(0, self.main.Options.TOP_OFFSET, dis_rect.w, dis_rect.h - self.main.Options.TOP_OFFSET) \
							.colliderect(pg.Rect((x, y), size)):
						self.display.blit(
							pg.transform.scale(self.sprite_sheet.img.subsurface(self.tiles[self.selected_tile]), size),
							(x, y))
			w = 5
			left = self.bold.x + size[0] * left-w
			top = self.bold.y + size[1] * top-w
			width = self.bold.x + size[0] * right - left+w
			height = self.bold.y + size[1] * bottom - top+w
			pg.draw.rect(self.display, (200, 200, 200), pg.Rect((left, top), (width, height)), w)
	
	def draw_grid_lines(self):
		dis_rect = self.display.get_rect()
		v_line = pg.Surface((dis_rect.w, 1))
		h_line = pg.Surface((1, dis_rect.h))
		v_line.fill(self.grid_color)
		h_line.fill(self.grid_color)
		tile_w, tile_h = self.tile_size
		lines = []
		for idx in range(int(max(dis_rect.w / self.tile_size[0], dis_rect.h / self.tile_size[1]) / self.zoom)):
			x = idx * tile_w * self.zoom + self.offset[0] % tile_w * self.zoom - tile_w + self.sidebar.right
			if 0 < x < dis_rect.w:
				lines.append((h_line, (x, self.main.Options.TOP_OFFSET)))
			x2 = self.sidebar.right - self.offset[0] % tile_w - tile_w
			y = idx * tile_h * self.zoom + self.offset[1] % tile_h * self.zoom - tile_w
			if y >= self.main.Options.TOP_OFFSET:
				lines.append((v_line, (x2, y)))
		self.display.fblits(lines)
		
	def draw_grid_tiles(self):
		size = (self.tile_size.x * self.zoom, self.tile_size.y * self.zoom)
		vis_rect = pg.Rect(self.sidebar.right-size[0]+1, self.main.Options.TOP_OFFSET-size[1], self.display.get_width()-self.sidebar.w+size[0], self.display.get_height())
		grid = []
		left, top = self.current_block(vis_rect.topleft)
		right, bottom = self.current_block(vis_rect.bottomright)
		for x_ in range(left, right):
			for y_ in range(top, bottom):
				pos = (x_, y_)
				if pos in self.grid:
					name = self.grid[pos]
					if name in self.tiles:
						tile = self.tiles[name]
						x = self.bold.x + size[0] * pos[0]
						y = self.bold.y + size[1] * pos[1]
						if vis_rect.collidepoint(x, y):
							if tile not in self.tile_cache:
								self.tile_cache[tile] = pg.transform.scale(self.sprite_sheet.img.subsurface(tile), size).convert_alpha()
							grid.append((self.tile_cache[tile], (x, y)))
					else:
						del self.grid[pos]
		self.display.fblits(grid)
	
	def render(self):
		dis_rect = self.display.get_rect()
		self.draw_grid_lines()
		# ===[ GRID ]===
		self.draw_grid_tiles()
		if self.tool == 'brush':
			self.display_hover_tile()
		elif self.tool == 'rect':
			self.draw_hover_rect()
		# ===[ BOLD LINES ]===
		pg.draw.line(self.display, "white", (self.bold.x, self.main.Options.TOP_OFFSET), (self.bold.x, dis_rect.h), 5)
		if self.bold.y > self.main.Options.TOP_OFFSET:
			pg.draw.line(self.display, "white", (0, self.bold.y), (dis_rect.w, self.bold.y), 5)
			pg.draw.circle(self.display, "white", (self.bold.x, self.bold.y), 15)
		"""====[ SIDEBAR ]===="""
		pg.draw.rect(self.display, (10, 10, 10), self.sidebar)
		self.sprite_sheet.render(self.tile_size)
		tiles = pg.Surface((self.sidebar.w, self.sidebar.centery))
		for idx, (name, tile) in enumerate(self.tiles.items()):
			pos = pg.Vector2(idx % 7 * 69 + 5, idx // 7 * 109 + 5 + self.scroll + self.main.Options.TOP_OFFSET)
			text = self.text.render(name, False, (120, 120, 120), wraplength=55)
			if name == self.selected_tile:
				pg.draw.rect(tiles, self.selected_tile_color, pg.Rect(pos.x - 4, pos.y - 4, 72, 72))
			tiles.blit(pg.transform.scale(self.sprite_sheet.img.subsurface(tile), (64, 64)), pos)
			tiles.blit(text, (pos[0] + 32 - text.get_width() / 2, pos[1] + 64))
		self.display.blit(tiles, (0, 0))

	def render_on_top(self):
		tile_size = self.header.render(f'{self.tile_size[0]}x{self.tile_size[1]}', True,
		                               (200, 200, 200))
		self.display.blit(tile_size, (self.sidebar.centerx - tile_size.get_width() / 2, 0))
	
	def current_block(self, pos) -> tuple[int, int]:
		""":return: block position at specified mouse pos"""
		pos = (
			int((pos[0] - self.bold.x) // (self.tile_size[0] * self.zoom)),
			int((pos[1] - self.bold.y) // (self.tile_size[1] * self.zoom))
		)
		return pos
	
	def eventHandler(self):
		for event in self.main.events:
			if event.type == KEYDOWN:
				if event == self.main.Bindings.RECT:
					self.tool = 'rect'
					self.rect[0] = False
					self.rect[1].topleft = (0, 0)
					self.rect[1].size = (0, 0)
				if event == self.main.Bindings.BRUSH:
					self.tool = 'brush'
					self.rect = [False, pg.Rect(0, 0, 0, 0)]
				if event == self.main.Bindings.SCALE_TILE_UP:
					self.tile_size *= 2
					self.bold = pg.Vector2(self.offset[0] * self.zoom - self.tile_size[0] + self.sidebar.right,
					                       self.offset[1] * self.zoom - self.tile_size[1])
				elif event == self.main.Bindings.SCALE_TILE_DOWN:
					self.tile_size /= 2
					self.tile_size[0] = max(1.0, self.tile_size[0])
					self.tile_size[1] = max(1.0, self.tile_size[1])
					self.bold = pg.Vector2(self.offset[0] * self.zoom - self.tile_size[0] + self.sidebar.right,
					                       self.offset[1] * self.zoom - self.tile_size[1])
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
			elif event.type == KEYUP:
				if event == self.main.Bindings.RECT:
					if self.rect[0]:
						pos = self.current_block(pg.mouse.get_pos())
						self.rect[1].w = pos[0] - self.rect[1].x + 1
						self.rect[1].h = pos[1] - self.rect[1].y + 1
						self.rect[0] = False
			elif event.type == MOUSEBUTTONDOWN:
				if event.button == 1:
					if event.pos[0] < self.sidebar.right:
						if (not self.sprite_sheet.area.collidepoint(event.pos)) and self.sidebar.collidepoint(event.pos):
							for idx, (name, tile) in enumerate(zip(self.tiles.keys(), self.tiles.values())):
								if pg.Rect(pg.Vector2(idx % 7 * 69+5, idx//7*109+5+self.scroll+self.main.Options.TOP_OFFSET), (64, 64)).collidepoint(event.pos):
									self.selected_tile = name
									break
					else:
						if self.selected_tile is not None:
							if self.tool == 'brush':
								self.grid[self.current_block(event.pos)] = self.selected_tile
							elif self.tool == 'rect':
								self.rect[0] = True
								self.rect[1] = pg.Rect(self.current_block(pg.mouse.get_pos()), (0, 0))
			elif event.type == MOUSEBUTTONUP:
				if self.selected_tile is not None:
					if self.tool == 'rect':
						if self.rect[0]:
							rect: pg.Rect = self.rect[1]
							
							left = rect.left if rect.w > 0 else rect.right - 1
							right = rect.right if rect.w > 0 else rect.left + 1
							top = rect.top if rect.h > 0 else rect.bottom - 1
							bottom = rect.bottom if rect.h > 0 else rect.top + 1
							for x in range(left, right):
								for y in range(top, bottom):
									self.grid[(x, y)] = self.selected_tile
							self.rect[0] = False
							pos = self.current_block(event.pos)
							self.rect[1].w = pos[0] - self.rect[1].x + 1
							self.rect[1].h = pos[1] - self.rect[1].y + 1
			elif event.type == MOUSEMOTION:
				if event.pos[0] > self.sidebar.right:
					if event.buttons[1]:
						self.offset += pg.Vector2(event.rel) * self.main.Options.MOUSE_SENSITIVITY / self.zoom
						self.bold = pg.Vector2(self.offset[0] * self.zoom - self.tile_size[0] + self.sidebar.right,
						                       self.offset[1] * self.zoom - self.tile_size[1])
					elif event.buttons[0]:
						if self.selected_tile is not None:
							if self.tool == 'brush':
								self.grid[self.current_block(event.pos)] = self.selected_tile
							elif self.tool == 'rect':
								if self.rect[0]:
									pos = self.current_block(pg.mouse.get_pos())
									self.rect[1].w = pos[0] - self.rect[1].x + 1
									self.rect[1].h = pos[1] - self.rect[1].y + 1
			elif event.type == MOUSEWHEEL:
				if not self.sidebar.collidepoint(pg.mouse.get_pos()):
					self.zoom += event.y * self.main.Options.SCROLL_SENSITIVITY
					self.zoom = pg.math.clamp(self.zoom, 0.25, 15)
					self.bold = pg.Vector2(self.offset[0] * self.zoom - self.tile_size[0] + self.sidebar.right,
					                       self.offset[1] * self.zoom - self.tile_size[1])
		self.sprite_sheet.eventHandler(self.main.events)
			
	class SpriteSheet:
		
		def __init__(self, path, display, project):
			"""sprite sheet object"""
			
			"""====[ PARAMETERS & INHERITANCE ]===="""
			self.path = path
			self.grid_color = "white"
			self.project = project
			self.main = self.project.main
			self.display = display
			self.sidebar = self.project.sidebar

			"""====[ IMAGE ]===="""
			self.img = pg.image.load(path).convert_alpha()
			self.w, self.h = self.img.get_size()

			"""====[ TEXT ]===="""
			self.save_selection = self.project.save_selection
			self.text = self.project.text
			self.header = self.project.header

			"""====[ CUSTOMIZABLE ]===="""
			self.zoom = 1
			self.offset = pg.Vector2(0, 0)
			self.selection_name = ""
			self.selection_color = "red"
			self.selection = pg.Rect(0, 0, 0, 0)
		
		def draw_selection(self, img):
			if self.selection != (0, 0, 0, 0):
				draw_rect(img, self.selection_color,
				          pg.Rect(
					          self.selection.x * self.zoom, self.selection.y * self.zoom,
					          self.selection.w * self.zoom, self.selection.h * self.zoom
				          ), width=3
				          )
		
		@property
		def area(self):
			return self.img.get_rect(centerx=self.sidebar.centerx, top=self.sidebar.centery)
		
		def draw_lines(self, img, tile_size):
			if img.get_width() > img.get_height():
				r = img.get_width() / tile_size[0]
			else:
				r = img.get_height() / tile_size[1]
			
			for idx in range(int(r)):
				x = idx * tile_size[0] * self.zoom
				pg.draw.line(img, self.grid_color, (x, 0), (x, img.get_height()), 1)
				y = idx * tile_size[1] * self.zoom
				pg.draw.line(img, self.grid_color, (0, y), (img.get_width(), y), 1)
			pg.draw.line(img, self.grid_color, (img.get_width()-1, 0), (img.get_width()-1, img.get_height()))
			pg.draw.line(img, self.grid_color, (0, img.get_height()-1), (img.get_width(), img.get_height()-1))
		
		def draw_data(self):
			rect = self.area
			if self.selection != (0, 0, 0, 0):
				self.display.blit(self.save_selection,
				                  (rect.centerx - self.save_selection.get_width() / 2, rect.bottom + 20))
				text = self.text.render(self.selection_name, False, (120, 120, 120))
				self.display.blit(text, (rect.centerx - text.get_width() / 2, rect.bottom + 50))
		
		def render(self, tile_size):
			sp_sheet = pg.transform.scale_by(self.img, self.zoom)
			rect = self.area
			pg.draw.rect(self.display, (32, 32, 32), rect)
			self.draw_lines(sp_sheet, tile_size)
			# sp sheet
			dest = rect.topleft
			area = self.img.get_rect(
				topleft=(
					rect.w / 2 * (self.zoom - 1) + self.offset.x,
					rect.h / 2 * (self.zoom - 1) + self.offset.y
				)
			)
			self.draw_selection(sp_sheet)
			self.display.blit(sp_sheet, dest, area)
			self.draw_data()
			return rect
		
		def get_rect(self, **kwargs):
			return self.img.get_rect(**kwargs)

		def get_point(self, x, y):
			rect = self.area
			area = self.img.get_rect(
				topleft=(self.w / 2 * (self.zoom - 1) + self.offset.x, self.h / 2 * (self.zoom - 1) + self.offset.y)
			)
			vis = pg.Rect(rect.left - area[0], rect.top - area[1], self.w * self.zoom, self.h * self.zoom)
			x = pg.math.clamp((x - vis.left) / self.zoom, 0, self.w)
			y = pg.math.clamp((y - vis.top) / self.zoom, 0, self.h)
			return x, y

		def eventHandler(self, events):
			for event in events:
				if event.type == MOUSEWHEEL:
					if pg.mouse.get_pos()[0] < self.sidebar.right:
						self.zoom += event.y * self.main.Options.SCROLL_SENSITIVITY
						if self.zoom < 1 or self.zoom > 15:
							self.zoom = pg.math.clamp(self.zoom, 1, 15)
				elif event.type == MOUSEMOTION:
					if self.area.collidepoint(pg.mouse.get_pos()):
						if event.buttons[0]:
							point = self.get_point(*event.pos)
							self.selection.size = (point[0] - self.selection.x, point[1] - self.selection.y)
						elif event.buttons[1]:
							self.offset -= pg.Vector2(event.rel) * self.main.Options.MOUSE_SENSITIVITY
				elif event.type == MOUSEBUTTONDOWN:
					if event.button == 1:
						if self.area.collidepoint(event.pos):
							self.selection.topleft = pg.Vector2(self.get_point(*event.pos))
							self.selection.size = (0, 0)
				elif event.type == MOUSEBUTTONUP:
					if event.button == 1:
						if self.area.collidepoint(event.pos):
							self.selection = pg.Rect(
								self.selection.x + (self.selection.w if self.selection.w < 0 else 0),
								self.selection.y + (self.selection.h if self.selection.h < 0 else 0),
								self.selection.w - ((self.selection.w * 2) if self.selection.w < 0 else 0),
								self.selection.h - ((self.selection.h * 2) if self.selection.h < 0 else 0)
							)
				elif event.type == KEYDOWN:
					if self.save_selection != (0, 0, 0, 0):
						if event == self.main.Bindings.CANCEL_SELECTION:
							self.selection = pg.Rect(0, 0, 0, 0)
							self.selection_name = ""
						elif event.key == K_BACKSPACE:
							self.selection_name = self.selection_name[:-1]
						elif event == self.main.Bindings.SELECTION_ACCEPT:
							self.project.tiles[self.selection_name] = tuple(self.selection.copy())
							self.selection = pg.Rect(0, 0, 0, 0)
							self.selection_name = ""
						elif not event.unicode.isascii():
							pass
						else:
							self.selection_name += event.unicode


class Welcome:
	
	def __init__(self, main: Main):
		self.main = main
		self.display = main.display
		self.path = 'Welcome'
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
	
	def save(self):
		"""it's just to prevent errors"""
		pass
	
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

	def render_on_top(self):
		pass

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
