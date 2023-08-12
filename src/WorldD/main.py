import os
import random
import sys
import json
import tkinter
from tkinter import filedialog
import pygame as pg
from pygame.locals import *
import tomllib
from typing import TypeVar

pg.init()
tkinter.Tk().withdraw()

__version__ = '1.0.0'

PureTileGroup = TypeVar('PureTileGroup')


TILES = dict[str, PureTileGroup]
GRID = list[dict[tuple[int, int], list[str, str]]]


def load(path: str | object) -> tuple[list[int, int], str, TILES, GRID, list]:
	""":returns: tile size, sprite sheet path, tiles, grid"""
	if type(path) is str:
		path = open(path, 'rb')
	
	def load_v0_12():
		sprite_sheet: str = data['img']
		tiles: dict[str, PureTileGroup] = {'all': PureTileGroup('all', {tile: tuple(map(int, pos.lstrip('(').rstrip(')').split(',')))
		                                      for pos, tile in data['data'].items()})}
		grid: GRID = \
			[
				{tuple(map(int, pos.split(','))): list(tile) for pos, tile in data['grid'].items()}
			]
		tile_size: list[int, int] = [32, 32]
		layer_names = [f'layer {layer+1}' for layer in range(len(grid))]
		return tile_size, sprite_sheet, tiles, grid, layer_names
	
	def load_v1_00():
		tile_size: list[int, int] = data['tile-size']
		tiles: dict[str, PureTileGroup] = \
			{
				name: PureTileGroup(name, {tile: pos for tile, pos in tile_group['tiles'].items()}, tile_group['pos'])
				for name, tile_group in data['data'].items()
			}
		grid: GRID = \
			[
				{tuple(map(int, map(float, pos.split(',')))): list(tile) for pos, tile in layer.items()}
				for layer in data['grid']
				]
		sprite_sheet: str = data['img']
		layer_names = [layer for layer in data['layer-names']]
		return tile_size, sprite_sheet, tiles, grid, layer_names
	
	data = json.load(path)
	if "version" not in data:
		version = "? 0.12"
	else:
		version = data['version']
	
	match version:
		case "? 0.12":
			return load_v0_12()
		case "v1.0.0":
			return load_v1_00()
		case _:
			print("VERSION UNKNOWN")


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
		self.AUTOTILE_RECT = Key(*bindings['AUTOTILE-RECT'])
		self.BRUSH = Key(*bindings['BRUSH'])
		self.MATRIX_TOP_RIGHT = Key(*bindings['MATRIX-TOP-RIGHT'])
		self.MATRIX_TOP_MID = Key(*bindings['MATRIX-TOP-MID'])
		self.MATRIX_TOP_LEFT = Key(*bindings['MATRIX-TOP-LEFT'])
		self.MATRIX_MID_RIGHT = Key(*bindings['MATRIX-MID-RIGHT'])
		self.MATRIX_MID_MID = Key(*bindings['MATRIX-MID-MID'])
		self.MATRIX_MID_LEFT = Key(*bindings['MATRIX-MID-LEFT'])
		self.MATRIX_BOT_RIGHT = Key(*bindings['MATRIX-BOT-RIGHT'])
		self.MATRIX_BOT_MID = Key(*bindings['MATRIX-BOT-MID'])
		self.MATRIX_BOT_LEFT = Key(*bindings['MATRIX-BOT-LEFT'])
		self.NEW_LAYER = Key(*bindings['NEW-LAYER'])
		self.PREVIOUS_LAYER = Key(*bindings['PREVIOUS-LAYER'])
		self.DELETE_LAYER = Key(*bindings['DELETE-LAYER'])
		self.RENAME_LAYER = Key(*bindings['RENAME-LAYER'])


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
			if self.FPS == 'AUTO':
				self.FPS = pg.display.get_current_refresh_rate()
			if self.FPS <= 0:
				self.FPS = 120
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
		"""====[ ICONS ]===="""
		icon_sheet = pg.image.load(self.work_path + 'assets/icon-sheet.png').convert_alpha()
		self.hide_ico = pg.transform.scale(icon_sheet.subsurface((0, 0, 16, 16)), (32, 32))
		self.show_ico = pg.transform.scale(icon_sheet.subsurface((16, 0, 16, 16)), (32, 32))
		self.close_ico = pg.transform.scale(icon_sheet.subsurface((32, 0, 16, 16)), (32, 32))
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
		main_project = self.Header.render('< ' + self.projects[self.selected].path.split('/')[-1] + ' > ', True,
		                                  (200, 200, 200))
		main_pos = ((self.display.get_width() - main_project.get_width()) / 2,
		            (self.Options.TOP_OFFSET - main_project.get_height()) / 2)
		self.display.blit(main_project, main_pos)
		if self.selected > 0:
			for en, project in enumerate(self.projects[:self.selected]):
				name = self.SmallerHeader.render(project.path.split('/')[-1], True, (200, 200, 200))
				pos = (main_pos[0] - sum(
					self.SmallerHeader.size(' ' + p.path.split('/')[-1] + ' ')[0] for p in self.projects[:en + 1]),
				       (self.Options.TOP_OFFSET - name.get_height()) / 2)
				self.display.blit(name, pos)
		if self.selected < len(self.projects) - 1:
			for en, project in enumerate(self.projects[self.selected + 1:]):
				name = self.SmallerHeader.render(project.path.split('/')[-1], True, (200, 200, 200))
				pos = (main_pos[0] + main_project.get_width() + sum(
					self.SmallerHeader.size(' ' + p.path.split('/')[-1] + ' ')[0] for p in
					self.projects[self.selected + 1:en - 1]), (self.Options.TOP_OFFSET - name.get_height()) / 2)
				self.display.blit(name, pos)
		
		self.projects[self.selected].render_on_top()
		
		"""====[ POPUPS ]===="""
		for popup in self.popups:
			popup.render()
		"""====[ EXIT ]===="""
		if self.Options.SHOW_EXIT:
			pg.draw.rect(self.display, (180, 180, 180), pg.Rect(self.display.get_width() - 25, 0, 25, 25),
			             border_radius=15, width=5)
			pg.draw.line(self.display, (180, 180, 180), (self.display.get_width() - 20, 5),
			             (self.display.get_width() - 5, 20), 5)
			pg.draw.line(self.display, (180, 180, 180), (self.display.get_width() - 20, 20),
			             (self.display.get_width() - 5, 5), 5)
	
	def exit(self):
		with open(self.path + '\\recent.txt', 'a') as recent:
			recent.truncate(0)
			recent.writelines(self.recent)
		for project in self.projects:
			project.save()
		pg.quit()
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
				self.selected = len(self.projects) - 1
			elif event.type == MOUSEBUTTONDOWN:
				if event.button == 1:
					if pg.Rect(self.display.get_width() - 50, 0, 50, 50).collidepoint(
							event.pos) and self.Options.SHOW_EXIT:
						self.exit()
			elif event.type == KEYDOWN:
				if event == self.Bindings.EXIT:
					self.exit()
				elif event == self.Bindings.TOGGLE_FULLSCREEN:
					pg.display.toggle_fullscreen()
				elif event == self.Bindings.PROJECT_SELECTION_LEFT:
					self.selected -= 1
					self.selected = pg.math.clamp(self.selected, 0, len(self.projects) - 1)
				elif event == self.Bindings.PROJECT_SELECTION_RIGHT:
					self.selected += 1
					self.selected = pg.math.clamp(self.selected, 0, len(self.projects) - 1)
		if not self.popups:
			self.projects[self.selected].eventHandler()
		else:
			for popup in self.popups:
				popup.eventHandler(self.events)
		
	def run(self):
		while True:
			self.refresh()
			pg.display.flip()
			self.clock.tick(self.Options.FPS)
			if self.eventHandler():
				return 1
			project = self.projects[self.selected]
			if project.path != 'Welcome':
				tiles = f'{len(project.grid[project.current_layer].keys())} tiles | '
			else:
				tiles = ''
			path = project.path
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
		self.save_selection = self.header.render("group (name/ESC)", True, (250, 250, 250))
		self.sprite_sheet = None
		
		"""====[ TOOLS ]===="""
		self.tool = 'brush'
		self.rect = [False, pg.Rect(0, 0, 0, 0)]
		
		"""====[ CONFIG ]===="""
		self.renaming = False
		self.tiles: dict[str, TileGroup] = {'all': TileGroup(self, 'all', {})}
		self.grid = [{}]
		self.current_layer = 0
		self.layer_names = ['Layer 0']
		self.layers_vis = Layers(self.display, self)
		self.destination = None
		self.path = None
		new_project = load is False
		load_project = load is True
		recent_project = load is not bool
		if new_project:
			filetypes = [('image', '*.png'), ('image', '*.jpg')]
			file = filedialog.askopenfile(filetypes=filetypes)
			if file is None:
				raise IOError
			self.path = file.name
			self.sprite_sheet = self.SpriteSheet(file.name, self.display, self)
			file.close()
		elif load_project:
			filetypes = [('world', '*.world')]
			file = filedialog.askopenfile(filetypes=filetypes)
			if file is None:
				raise IOError
			else:
				self.load(file.name)
			file.close()
		elif recent_project:
			file = open(load)
			if file is None:
				raise IOError
			if file.name.split('.')[-1].lower() != 'world':
				self.sprite_sheet = self.SpriteSheet(file.name, self.display, self)
			else:
				self.path = file.name
				self.load(file.name)
		self._selected_tile = None
		self.tile_size = pg.Vector2(tile_size)
		self.zoom = 1
		
		"""====[ CUSTOMIZABLE ]===="""
		self.grid_color = (255, 255, 255)
		self.selected_tile_color = (255, 255, 255)
		self.selected_matrix_selection_color = (255, 100, 100)
		self.matrix_full_color = (50, 255, 50)
		self.window_outline_color = (128, 128, 128)
		self.selected_window_outline_color = (255, 255, 255)
		
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
		tile_size, sp_sheet, pure_tile_groups, self.grid, self.layer_names = load(self.destination)
		self.tile_size = pg.Vector2(tuple(tile_size))
		self.sprite_sheet = self.SpriteSheet(sp_sheet, self.display, self)
		self.tiles = {name: TileGroup(self, name, tile_group.tiles, tile_group.pos) for name, tile_group in pure_tile_groups.items()}
		self.destination.close()
		self.destination = None
	
	def save(self):
		if self.destination is None:
			if self.path is None or self.path[-4:] == '.png':
				self.destination = filedialog.asksaveasfile('a+', defaultextension='.world')
				if self.destination is not None:
					self.path = self.destination.name
			else:
				self.destination = open(self.path, 'a+')
		else:
			print(self.destination)
		if self.path is not None and self.path[-4:] != '.png':
			save_data = json.dumps(
				{
					'grid':  [{f"{pos[0]},{pos[1]}": tile for pos, tile in layer.items()} for layer in self.grid],
					'current-layer': self.current_layer,
					'layer-names': self.layer_names,
					'data': {name: tile_group.data for name, tile_group in self.tiles.items()},
					'img': self.sprite_sheet.path,
					'tile-size': list(self.tile_size),
					'version': __version__
				},
			)
			self.destination.seek(0)
			self.destination.truncate(0)
			self.destination.write(save_data)
			self.destination.close()
			self.destination = None
			if self.path not in self.main.recent:
				self.main.recent.append(self.path)
    
	def display_hover_tile(self, pos=None, tile=None):
		if self.selected_tile is not None or tile is not None:
			dis_rect = self.display.get_rect()
			pos = self.current_block(pos)
			size = (self.tile_size.x * self.zoom, self.tile_size.y * self.zoom)
			x = self.bold.x + size[0] * pos[0]
			y = self.bold.y + size[1] * pos[1]
			if pg.Rect(0, self.main.Options.TOP_OFFSET, dis_rect.w, dis_rect.h - self.main.Options.TOP_OFFSET) \
					.colliderect(pg.Rect((x, y), size)):
				if tile is None:
					tile = self.sprite_sheet.img.subsurface(self.selected_tile)
				if pos is None:
					pos = pg.mouse.get_pos()
				self.display.blit(pg.transform.scale(tile, size), (x, y))
	
	@property
	def selected_tile(self):
		if self._selected_tile is not None:
			return self.tiles[self._selected_tile[0]][self._selected_tile[1]]
		else:
			return None
	
	@selected_tile.setter
	def selected_tile(self, value):
		self._selected_tile = value
	
	@property
	def raw_selected_tile(self):
		return self._selected_tile
	
	def draw_hover_rect(self):
		if not (self.selected_tile is not None and self.rect[0]):
			return
		dis_rect = self.display.get_rect()
		size = (self.tile_size.x * self.zoom, self.tile_size.y * self.zoom)
		
		rect: pg.Rect = self.rect[1]
		
		left = rect.left if rect.w > 0 else rect.right - 1
		right = rect.right if rect.w > 0 else rect.left + 1
		top = rect.top if rect.h > 0 else rect.bottom - 1
		bottom = rect.bottom if rect.h > 0 else rect.top + 1
		
		for x_ in range(left, right):
			for y_ in range(top, bottom):
				x = self.bold.x + size[0] * x_
				y = self.bold.y + size[1] * y_
				if pg.Rect(0, self.main.Options.TOP_OFFSET, dis_rect.w, dis_rect.h - self.main.Options.TOP_OFFSET) \
						.colliderect(pg.Rect((x, y), size)):
					self.display.blit(
						pg.transform.scale(self.sprite_sheet.img.subsurface(self.selected_tile), size),
						(x, y))
		w = 5
		left = self.bold.x + size[0] * left - w
		top = self.bold.y + size[1] * top - w
		width = self.bold.x + size[0] * right - left + w
		height = self.bold.y + size[1] * bottom - top + w
		pg.draw.rect(self.display, (200, 200, 200), pg.Rect((left, top), (width, height)), w)
	
	def draw_hover_autotiling_rect(self):
		if not (self.selected_tile is not None and self.rect[0]) or not self.tiles[
			self.raw_selected_tile[0]].matrix_is_full():
			return
		group = self.tiles[self.raw_selected_tile[0]]
		matrix = group.matrix
		
		size = (self.tile_size.x * self.zoom, self.tile_size.y * self.zoom)
		rect: pg.Rect = self.rect[1]
		
		left = rect.left if rect.w > 0 else rect.right - 1
		right = rect.right if rect.w > 0 else rect.left + 1
		top = rect.top if rect.h > 0 else rect.bottom - 1
		bottom = rect.bottom if rect.h > 0 else rect.top + 1
		
		txt = {
			key: pg.transform.scale(self.sprite_sheet.img.subsurface(group[value]), size) for key, value in
			matrix.items()
		}
		# DRAW TOP
		width = right - left
		height = bottom - top
		
		if width == 1 and height == 1:
			self.display_hover_tile((self.bold.x + size[0] * left, self.bold.y + size[1] * top), txt[(0, 0)])
		if width > 1:
			self.display_hover_tile((self.bold.x + size[0] * left, self.bold.y + size[1] * top), txt[(-1, -1)])
			self.display_hover_tile((self.bold.x + size[0] * right - size[0], self.bold.y + size[1] * top),
			                        txt[(1, -1)])
		if height > 1:
			self.display_hover_tile((self.bold.x + size[0] * left, self.bold.y + size[1] * bottom - size[1]),
			                        txt[(-1, 1)])
			self.display_hover_tile((self.bold.x + size[0] * right - size[0], self.bold.y + size[1] * bottom - size[1]),
			                        txt[(1, 1)])
		if width > 3 and height > 3:
			for x in range(left + 1, right - 1):
				for y in range(top + 1, bottom - 1):
					self.display_hover_tile((self.bold.x + size[0] * x, self.bold.y + size[1] * y), txt[(0, 0)])
		if height > 2:
			x = self.bold.x + size[0] * left
			x2 = self.bold.x + size[0] * right - size[0]
			for y in range(top + 1, bottom - 1):
				y = self.bold.y + size[1] * y
				self.display_hover_tile((x, y), txt[(-1, 0)])
				self.display_hover_tile((x2, y), txt[(1, 0)])
		if width > 2:
			y = self.bold.y + size[1] * top
			y2 = self.bold.y + size[1] * bottom - size[1]
			for x in range(left + 1, right - 1):
				x = self.bold.x + size[0] * x
				self.display_hover_tile((x, y), txt[(0, -1)])
				self.display_hover_tile((x, y2), txt[(0, 1)])
		w = 5
		left = self.bold.x + size[0] * left - w
		top = self.bold.y + size[1] * top - w
		width = self.bold.x + size[0] * right - left + w
		height = self.bold.y + size[1] * bottom - top + w
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
		vis_rect = pg.Rect(self.sidebar.right - size[0] + 1, self.main.Options.TOP_OFFSET - size[1],
		                   self.display.get_width() - self.sidebar.w + size[0] * 2, self.sidebar.h + size[1])
		grid = []
		left, top = self.current_block(vis_rect.topleft)
		right, bottom = self.current_block(vis_rect.bottomright)
		for x_ in range(left, right):
			for y_ in range(top, bottom):
				pos = (x_, y_)
				tiles = []
				x, y = None, None
				for layer in reversed(self.grid):
					if pos in layer:
						data = layer[pos]
						if data[0] in self.tiles:
							tile_group = self.tiles[data[0]]
							name = data[1]
							if name in tile_group:
								tile_name = tuple(tile_group[name])
								x = self.bold.x + size[0] * pos[0]
								y = self.bold.y + size[1] * pos[1]
								if vis_rect.collidepoint(x, y):
									if tile_name not in self.tile_cache:
										self.tile_cache[tile_name] = pg.transform.scale(self.sprite_sheet.img.subsurface(tile_name), size).convert_alpha()
									tiles.append(self.tile_cache[tile_name])
							else:
								del layer[pos]
						else:
							del layer[pos]
				if tiles:
					for tile in tiles:
						grid.append((tile, (x, y)))
				
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
		elif self.tool == 'autotile-rect':
			self.draw_hover_autotiling_rect()
		# ===[ BOLD LINES ]===
		pg.draw.line(self.display, "white", (self.bold.x, self.main.Options.TOP_OFFSET), (self.bold.x, dis_rect.h), 5)
		if self.bold.y > self.main.Options.TOP_OFFSET:
			pg.draw.line(self.display, "white", (0, self.bold.y), (dis_rect.w, self.bold.y), 5)
			pg.draw.circle(self.display, "white", (self.bold.x, self.bold.y), 15)
		"""====[ SIDEBAR ]===="""
		pg.draw.rect(self.display, (10, 10, 10), self.sidebar)
		self.sprite_sheet.render(self.tile_size)
		self.layers_vis.visualize()
		for tile_group in self.tiles.values():
			tile_group.draw()
	
	def render_on_top(self):
		tile_size = self.header.render(f'{self.tile_size[0]}x{self.tile_size[1]}', True,
		                               (200, 200, 200))
		self.display.blit(tile_size, (self.sidebar.centerx - tile_size.get_width() / 2, 0))
	
	def current_block(self, pos=None) -> tuple[int, int]:
		""":return: block position at specified pos / mouse pos"""
		if pos is None:
			pos = pg.mouse.get_pos()
		pos = (
			int((pos[0] - self.bold.x) // (self.tile_size[0] * self.zoom)),
			int((pos[1] - self.bold.y) // (self.tile_size[1] * self.zoom))
		)
		return pos
	
	def set_block(self, pos, group=None, name=None):
		if self.selected_tile is not None:
			if group is None or name is None:
				group, name = self._selected_tile
			self.grid[self.current_layer][pos] = [group, name]
		else:
			pass
	
	def upload_rect_to_grid(self, width, height):
		for x in range(width[0], width[1]):
			for y in range(height[0], height[1]):
				self.set_block((x, y))
	
	def upload_autotile_rect_to_grid(self, width, height):
		if not (self.selected_tile is not None and self.rect[0]) or not self.tiles[
			self.raw_selected_tile[0]].matrix_is_full():
			return
		group = self.tiles[self.raw_selected_tile[0]]
		matrix = group.matrix
		
		left, right = width
		top, bottom = height
		
		# DRAW TOP
		width = right - left
		height = bottom - top
		
		if width == 1 and height == 1:
			self.set_block((left, top), group.name, matrix[(0, 0)])
		if width > 1:
			self.set_block((left, top), group.name, matrix[(-1, -1)])
			self.set_block((right - 1, top), group.name, matrix[(1, -1)])
		if height > 1:
			self.set_block((left, bottom - 1), group.name, matrix[(-1, 1)])
			self.set_block((right - 1, bottom - 1), group.name, matrix[(1, 1)])
		if width > 3 and height > 3:
			for x in range(left + 1, right - 1):
				for y in range(top + 1, bottom - 1):
					self.set_block((x, y), group.name, matrix[(0, 0)])
		if height > 2:
			x = left
			x2 = right - 1
			for y in range(top + 1, bottom - 1):
				self.set_block((x, y), group.name, matrix[(-1, 0)])
				self.set_block((x2, y), group.name, matrix[(1, 0)])
		if width > 2:
			y = top
			y2 = bottom - 1
			for x in range(left + 1, right - 1):
				self.set_block((x, y), group.name, matrix[(0, -1)])
				self.set_block((x, y2), group.name, matrix[(0, 1)])
	
	def eventHandler(self):
		for event in self.main.events:
			if event.type == KEYDOWN:
				if self.renaming:
					if event == self.main.Bindings.CANCEL_SELECTION or event == self.main.Bindings.SELECTION_ACCEPT:
						self.renaming = False
					elif event.key == K_BACKSPACE:
						self.layer_names[self.current_layer] = self.layer_names[self.current_layer][0:-1]
					elif event.unicode.isascii():
						self.layer_names[self.current_layer] += event.unicode
						print(self.layer_names[self.current_layer], event.unicode)
				else:
					if event == self.main.Bindings.RECT:
						self.tool = 'rect'
						self.rect[0] = False
						self.rect[1].topleft = (0, 0)
						self.rect[1].size = (0, 0)
					if event == self.main.Bindings.AUTOTILE_RECT:
						self.tool = 'autotile-rect'
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
							del self.tiles[self.raw_selected_tile[0]][self.raw_selected_tile[1]]
							self.selected_tile = None
					elif event == self.main.Bindings.NEW_LAYER:
						print("new layer")
						self.current_layer += 1
						if len(self.grid) <= self.current_layer:
							print(len(self.grid), self.current_layer)
							self.grid.append({})
							self.layer_names.append(f"layer {len(self.grid)}")
					elif event == self.main.Bindings.PREVIOUS_LAYER:
						print("previous layer")
						if self.current_layer > 0:
							self.current_layer -= 1
					elif event == self.main.Bindings.DELETE_LAYER:
						self.grid.pop(self.current_layer)
						self.layer_names.pop(self.current_layer)
						self.current_layer -= 1
					elif event == self.main.Bindings.RENAME_LAYER:
						self.renaming = True
			elif event.type == KEYUP:
				if event == self.main.Bindings.RECT:
					if self.rect[0]:
						pos = self.current_block()
						self.rect[1].w = pos[0] - self.rect[1].x + 1
						self.rect[1].h = pos[1] - self.rect[1].y + 1
						self.rect[0] = False
			elif event.type == MOUSEBUTTONDOWN:
				if event.button == 1:
					if not event.pos[0] < self.sidebar.right:
						if self.selected_tile is not None:
							if self.tool == 'brush':
								if not any(group.collidepoint(event.pos) for group in self.tiles.values()):
									self.set_block(self.current_block(event.pos))
							elif self.tool == 'rect' or self.tool == 'autotile-rect':
								if not any(group.collidepoint(event.pos) for group in self.tiles.values()):
									self.rect[0] = True
									self.rect[1] = pg.Rect(self.current_block(), (1, 1))
			elif event.type == MOUSEBUTTONUP:
				if self.selected_tile is not None:
					if self.tool == 'rect' or self.tool == 'autotile-rect':
						if self.rect[0]:
							rect: pg.Rect = self.rect[1]
							
							width = (
							rect.left if rect.w > 0 else rect.right - 1, rect.right if rect.w > 0 else rect.left + 1)
							height = (
							rect.top if rect.h > 0 else rect.bottom - 1, rect.bottom if rect.h > 0 else rect.top + 1)
							if self.tool == 'rect':
								self.upload_rect_to_grid(width, height)
							else:
								self.upload_autotile_rect_to_grid(width, height)
							
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
								if not any(group.collidepoint(event.pos) for group in self.tiles.values()):
									self.set_block(self.current_block(event.pos))
							elif self.tool == 'rect' or self.tool == 'autotile-rect':
								if self.rect[0]:
									if not any(group.collidepoint(event.pos) for group in self.tiles.values()):
										pos = self.current_block(pg.mouse.get_pos())
										self.rect[1].w = pos[0] - self.rect[1].x + 1
										self.rect[1].h = pos[1] - self.rect[1].y + 1
			elif event.type == MOUSEWHEEL:
				if not self.sidebar.collidepoint(pg.mouse.get_pos()):
					self.zoom += event.y * self.main.Options.SCROLL_SENSITIVITY
					self.zoom = pg.math.clamp(self.zoom, 0.25, 15)
					self.tile_cache = {}
					self.bold = pg.Vector2(self.offset[0] * self.zoom - self.tile_size[0] + self.sidebar.right,
					                       self.offset[1] * self.zoom - self.tile_size[1])
		self.layers_vis.event_handler(self.main.events)
		for tile_group in self.tiles.copy().values():
			tile_group.eventHandler(self.main.events)
		self.sprite_sheet.eventHandler(self.main.events)
	
	class SpriteSheet:
		
		def __init__(self, path, display, project):
			"""sprite sheet object"""
			
			"""====[ PARAMETERS & INHERITANCE ]===="""
			self.path = path
			self.grid_color = "white"
			self.project: Project = project
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
			pg.draw.line(img, self.grid_color, (img.get_width() - 1, 0), (img.get_width() - 1, img.get_height()))
			pg.draw.line(img, self.grid_color, (0, img.get_height() - 1), (img.get_width(), img.get_height() - 1))
		
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
					if self.area.collidepoint(*pg.mouse.get_pos()):
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
						if self.area.collidepoint(event.pos) and not any(
								tile_group.collidepoint(event.pos) for tile_group in self.project.tiles.values()):
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
							if self.selection_name not in self.project.tiles:
								self.project.tiles[self.selection_name]: TileGroup = TileGroup(self.project,
								                                                               self.selection_name, {})
							id_ = random.random()
							while id_ in self.project.tiles[self.selection_name].tiles:
								id_ = str(random.random())
							self.project.tiles[self.selection_name][id_] = tuple(self.selection.copy())
							self.selection = pg.Rect(0, 0, 0, 0)
							self.selection_name = ""
						elif not event.unicode.isascii():
							pass
						else:
							self.selection_name += event.unicode


class PureTileGroup:
	
	def __init__(self, name, tiles, pos=None):
		self.name = name
		self.tiles = tiles
		self.pos = pg.Vector2(pos)
		self.tiles: dict = tiles
		self._matrix = {}
	
	def items(self):
		return self.tiles.items()
	
	@property
	def matrix(self) -> dict[tuple[int, int], None | str]:
		"""position from -1x-1 to 1x1"""
		map_matrix = self.mapping_matrix
		matrix = {
			(-1, -1): self._matrix[(-1, -1)] if map_matrix[(-1, -1)] else (
				self._matrix[(-1, 0)] if map_matrix[(-1, 0)] else None),
			(-1, 0): self._matrix[(-1, 0)] if map_matrix[(-1, 0)] else None,
			(-1, 1): self._matrix[(-1, 1)] if map_matrix[(-1, 1)] else (
				self._matrix[(-1, 0)] if map_matrix[(-1, 0)] else None),
			(0, -1): self._matrix[(0, -1)] if map_matrix[(0, -1)] else None,
			(0, 0): self._matrix[(0, 0)] if map_matrix[(0, 0)] else None,
			(0, 1): self._matrix[(0, 1)] if map_matrix[(0, 1)] else None,
			(1, -1): self._matrix[(1, -1)] if map_matrix[(1, -1)] else (
				self._matrix[(1, 0)] if map_matrix[(1, 0)] else None),
			(1, 0): self._matrix[(1, 0)] if map_matrix[(1, 0)] else None,
			(1, 1): self._matrix[(1, 1)] if map_matrix[(1, 1)] else (
				self._matrix[(1, 0)] if map_matrix[(1, 0)] else None)
		}
		return matrix
	
	@matrix.setter
	def matrix(self, value):
		value = tuple(value)
		self._matrix[value[0]] = value[1]
	
	@property
	def mapping_matrix(self):
		mapping_matrix = {
			(-1, -1): (-1, -1) in self._matrix,
			(-1, 0): (-1, 0) in self._matrix,
			(-1, 1): (-1, 1) in self._matrix,
			(0, -1): (0, -1) in self._matrix,
			(0, 0): (0, 0) in self._matrix,
			(0, 1): (0, 1) in self._matrix,
			(1, -1): (1, -1) in self._matrix,
			(1, 0): (1, 0) in self._matrix,
			(1, 1): (1, 1) in self._matrix
		}
		return mapping_matrix
	
	def matrix_is_full(self):
		matrix = self.matrix
		cross = (matrix[(-1, 0)] and matrix[(0, 0)] and matrix[(1, 0)] and matrix[(0, -1)] and matrix[(0, 1)])
		return cross

	def __repr__(self):
		return f'<PureTileGroup name:\"{self.name}\" tiles:{self.tiles}>'
		

class TileGroup(PureTileGroup):
	
	def __init__(self, project: Project, name, tiles, pos=None, _draw_matrix=False):
		self.project = project
		self.display = project.display
		self.header, self.text = self.project.header, self.project.text
		self.name = name
		if type(pos) is not tuple and type(pos) is not list and type(pos) is not pg.Vector2:
			self.pos = pg.Vector2(project.sidebar.centerx, project.main.Options.TOP_OFFSET + 50)
		else:
			self.pos = pg.Vector2(pos)
		self.selected_edit = None
		self._draw_matrix = _draw_matrix
		super().__init__(name, tiles, self.pos)
	
	def items(self):
		return self.tiles.items()
	
	@property
	def size(self):
		tile_size = (max(64, int(self.project.tile_size[0])), max(64, int(self.project.tile_size[0])))
		width = max(256, min(len(self.tiles), 5) * tile_size[0] + tile_size[0] // 2)
		tiles_in_row = width // tile_size[0]
		height = int((len(self.tiles) // tiles_in_row) * tile_size[1] + tile_size[1] * 1.5) + 64
		return tile_size, width, height, tiles_in_row
	
	def draw(self):
		tile_size, width, height, tiles_in_row = self.size
		tiles = pg.Surface((width, height))
		
		if self.project.selected_tile is not None and self.name == self.project.raw_selected_tile[0]:
			color = self.project.selected_window_outline_color
		else:
			color = self.project.window_outline_color
		
		name = self.header.render(self.name, True, color)
		tiles.blit(name, ((tiles.get_width() - name.get_width()) / 2, 0))
		for idx, (name, tile) in enumerate(self.tiles.items()):
			pos = pg.Vector2(idx % tiles_in_row * 69 + 5, idx // tiles_in_row * 69 + 5 + 64)
			# text = self.text.render(name, False, (120, 120, 120), wraplength=55)
			if (self.name, name) == self.project.raw_selected_tile:
				pg.draw.rect(tiles, self.project.selected_tile_color,
				             pg.Rect(pos.x - 4, pos.y - 4, tile_size[0] + 8, tile_size[1] + 8))
			tiles.blit(pg.transform.scale(self.project.sprite_sheet.img.subsurface(tile), tile_size), pos)
		# tiles.blit(text, (pos[0] + tile_size[0]/2 - text.get_width() / 2, pos[1] + tile_size[1]))
		
		pg.draw.rect(self.display, color,
		             pg.Rect(self.pos[0] - 2, self.pos[1] - 2, tiles.get_width() + 4, tiles.get_height() + 4),
		             border_radius=15)
		x = tiles.get_width() - 64
		y = 20
		if not self._draw_matrix:
			tiles.blit(self.project.main.hide_ico, (x, y))
		else:
			tiles.blit(self.project.main.show_ico, (x, y))
		tiles.blit(self.project.main.close_ico, (x + 32, y))
		self.display.blit(tiles, self.pos)
		self.draw_matrix()
	
	def draw_matrix(self):
		if not self._draw_matrix:
			return
		matrix_complete = super().matrix_is_full()
		matrix = super().matrix
		
		tile_size = (max(64, int(self.project.tile_size[0])), max(64, int(self.project.tile_size[0])))
		width = max(256, 3 * tile_size[0])
		height = max(256, 3 * tile_size[1]) + 64
		matrix_canvas = pg.Surface((width, height))
		
		if self.project.selected_tile is not None and self.name == self.project.raw_selected_tile[0]:
			color = self.project.selected_window_outline_color
		else:
			color = self.project.window_outline_color
		
		color = color if not matrix_complete else self.project.matrix_full_color
		
		for en_x, x in zip((-1, 0, 1), [15 * (x_ + 1) + tile_size[0] * x_ for x_ in range(3)]):
			for en_y, y in zip((-1, 0, 1), [64 + 15 * y_ + tile_size[1] * y_ for y_ in range(3)]):
				if matrix[(en_x, en_y)] is None:
					pg.draw.rect(matrix_canvas, self.project.window_outline_color, pg.Rect((x, y), tile_size))
				else:
					cl = self.project.selected_window_outline_color if not matrix_complete else self.project.matrix_full_color
					pg.draw.rect(matrix_canvas, cl, pg.Rect(x - 3, y - 3, tile_size[0] + 6, tile_size[1] + 6))
					tile = pg.transform.scale(
						self.project.sprite_sheet.img.subsurface(self.tiles[matrix[(en_x, en_y)]]), tile_size)
					matrix_canvas.blit(tile, pg.Rect((x, y), tile_size))
		w = max(256, min(len(self.tiles), 5) * tile_size[0] + tile_size[0] // 2)
		pos = (self.pos.x + w, self.pos.y)
		pg.draw.rect(self.display, color,
		             (pos[0] - 2, pos[1] - 2, matrix_canvas.get_width() + 4, matrix_canvas.get_height() + 4))
		self.display.blit(matrix_canvas, pos)
	
	def collidepoint(self, *pos):
		tile_size, width, height, tiles_in_row = self.size
		tiles = pg.Rect(self.pos, (width, height))
		matrix = pg.Rect((self.pos.x + width, self.pos.y),
		                 (max(256, 3 * tile_size[0]), max(256, 3 * tile_size[1]) + 64))
		return tiles.collidepoint(pos) or (matrix.collidepoint(pos) if self._draw_matrix else False)
	
	def eventHandler(self, events):
		for event in events:
			if event.type == MOUSEMOTION:
				if event.buttons[0]:
					if self.collidepoint(event.pos):
						self.pos += event.rel
			elif event.type == MOUSEBUTTONDOWN:
				if event.button == 1 or event.button == 3 and self.collidepoint(event.pos):
					tile_size, width, height, tiles_in_row = self.size
					if pg.Rect(self.pos[0] + width - 64, self.pos[1] + 20, 32, 32).collidepoint(event.pos):
						self._draw_matrix = not self._draw_matrix
					elif pg.Rect(self.pos[0] + width - 32, self.pos[1] + 20, 32, 32).collidepoint(event.pos):
						del self.project.tiles[self.name]
					else:
						for idx, (name, tile) in enumerate(self.tiles.items()):
							pos = pg.Vector2(idx % tiles_in_row * 69 + 5, idx // tiles_in_row * 69 + 5 + 64) + self.pos
							if pg.Rect(pos, tile_size).collidepoint(event.pos):
								self.project.selected_tile = (self.name, name)
								self.selected_edit = name
								break
			elif event.type == KEYDOWN:
				if self.selected_edit is not None:
					match event:
						case self.project.main.Bindings.MATRIX_TOP_RIGHT:
							self.matrix = [(1, -1), self.selected_edit]
						case self.project.main.Bindings.MATRIX_TOP_MID:
							self.matrix = [(0, -1), self.selected_edit]
						case self.project.main.Bindings.MATRIX_TOP_LEFT:
							self.matrix = [(-1, -1), self.selected_edit]
						case self.project.main.Bindings.MATRIX_MID_RIGHT:
							self.matrix = [(1, -0), self.selected_edit]
						case self.project.main.Bindings.MATRIX_MID_MID:
							self.matrix = [(0, 0), self.selected_edit]
						case self.project.main.Bindings.MATRIX_MID_LEFT:
							self.matrix = [(-1, 0), self.selected_edit]
						case self.project.main.Bindings.MATRIX_BOT_RIGHT:
							self.matrix = [(1, 1), self.selected_edit]
						case self.project.main.Bindings.MATRIX_BOT_MID:
							self.matrix = [(0, 1), self.selected_edit]
						case self.project.main.Bindings.MATRIX_BOT_LEFT:
							self.matrix = [(-1, 1), self.selected_edit]
	
	def __setitem__(self, key, value):
		self.tiles[key] = value
	
	def __getitem__(self, item):
		return self.tiles[item]
	
	def __delitem__(self, key):
		del self.tiles[key]
	
	def __contains__(self, item):
		if item in self.tiles:
			return True
		else:
			return False
	
	@property
	def data(self):
		return {'tiles': {name: tile for name, tile in self.tiles.items()}, 'pos': list(self.pos),
		        '_draw_matrix': self._draw_matrix, '_matrix': {}}

	def __repr__(self):
		return f'<TileGroup name:\"{self.name}\" tiles:{self.tiles}>'


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
		self.display.blit(self.texts['#Welcome'],
		                  self.texts['#Welcome'].get_rect(center=(dis_rect.w / 4, dis_rect.h / 6)))
		
		"""====[ PROJECTS ]===="""
		New = self.texts['New project']
		New_rect = New.get_rect(centerx=dis_rect.w / 4, top=dis_rect.h / 3)
		Load = self.texts['Load project']
		Load_rect = Load.get_rect(centerx=dis_rect.w/4, top=dis_rect.h/3+New_rect.height*1.5)
		if len(self.main.popups) == 0:
			if New_rect.collidepoint(mouse_pos):
				New = self.texts['__New_project__']
			if Load_rect.collidepoint(mouse_pos):
				Load = self.texts['__Load_project__']
		self.display.blit(New, New_rect.topleft)
		self.display.blit(Load, Load_rect.topleft)
		
		"""====[ RECENT ]===="""
		rect = pg.Rect(25, dis_rect.h / 2, dis_rect.w / 2 - 25, dis_rect.h / 2)
		pg.draw.rect(self.display, (20, 20, 20), rect, border_radius=15)
		for row, text in enumerate(self.main.recent):
			pos = (rect.left + self.text.size('  ')[0], rect.top + row * self.text.get_height())
			txt = self.text.render(text, True, (150, 150, 150))
			if txt.get_rect(topleft=pos).collidepoint(mouse_pos) and len(self.main.popups) == 0:
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
						self.main.popups.append(Popup(self.main, self.display))
					elif Load_rect.collidepoint(event.pos):
						try:
							self.main.projects.append(Project(self.main, (32, 32), load=True))
							self.main.selected = len(self.main.projects) - 1
						except IOError:
							pass
					else:
						rect = pg.Rect(25, dis_rect.h / 2, dis_rect.w / 2 - 25, dis_rect.h / 2)
						for row, text in enumerate(self.main.recent):
							txt = self.text.render(text, True, (150, 150, 150))
							txt = txt.get_rect(
								topleft=(rect.left + self.text.size('  ')[0], rect.top + row * self.text.get_height()))
							if txt.collidepoint(event.pos):
								try:
									self.main.projects.append(Project(self.main, (32, 32), load=text))
									self.main.selected = len(self.main.projects) - 1
								except IOError:
									pass


class Popup:
	
	def __init__(self, main, display):
		self.main = main
		self.display = display
		self.header = pg.font.SysFont(self.main.Options.HEADER_FONT, 60, True, False)
		self.small_header = pg.font.SysFont(self.main.Options.HEADER_FONT, 40, True, False)
		self.text = pg.font.SysFont(self.main.Options.TEXT_FONT, 30, False, False)
		self.text_hover = pg.font.SysFont(self.main.Options.TEXT_FONT, 31, True, False)
		
		self.question = self.header.render("New world", True, (200, 200, 200))
		self.DATA = [
			{
				'question': "Type",
				'options': ['! isometric (no support for now) !', '2(.5)D']
			},
			{
				'question': "Tile Size",
				'options': ['8x8', '16x16', '24x24', '32x32', '48x48', '64x64']
			 }
		]
		self.option_groups = \
			[
				{
					'question': self.small_header.render(option_group['question'], True, (200, 200, 200)),
					'options':
						{
							option: self.text.render(option, True, (200, 200, 200)) for option in option_group['options']
						}
				} for option_group in self.DATA
			]
		self.option_groups_hover = \
			[
				{
					'question': self.text_hover.render(option_group['question'], True, (200, 200, 200)),
					'options':
						{
							option: self.text_hover.render(option, True, (200, 200, 200)) for option in option_group['options']
						}
				} for option_group in self.DATA
			]
		self.answer = {option_group['question']: None for option_group in self.DATA}
		self.pos = pg.Vector2((self.display.get_width()-self.question.get_width())/2-100, self.display.get_height()/3)
	
	def render(self):
		h = self.question.get_height() + sum(70 + 50 * len(option_group['options'].values()) for option_group in self.option_groups)
		rect = pg.Rect((self.pos.x, self.pos.y - h/4), (self.question.get_width() + 200, h))
		question_rect = self.question.get_rect(centerx=rect.centerx, top=rect.top)
		question_rect.bottom += 10
		top = question_rect.bottom
		pg.draw.rect(self.display, (10, 10, 10), rect, border_radius=15)
		pg.draw.rect(self.display, (100, 100, 100), rect, border_radius=15, width=2)
		self.display.blit(self.question, question_rect)
		for enum, option_group in enumerate(self.option_groups):
			options = option_group['options']
			
			pg.draw.line(self.display, (100, 100, 100), (rect.x+25, top), (rect.right-25, top))
			question = option_group['question']
			self.display.blit(question, (rect.centerx-question.get_width()/2, top))
			top += question.get_height()
			for en, (name, texture) in enumerate(options.items()):
				pos = pg.Rect((rect.centerx-texture.get_width()/2, top), texture.get_size())
				if pos.collidepoint(pg.mouse.get_pos()) or self.answer[self.DATA[enum]['question']] == name:
					self.display.blit(self.option_groups_hover[enum]['options'][name], pos)
				else:
					self.display.blit(texture, pos)
				top = top+10+texture.get_height()
		if any(self.answer[key] is None for key in self.answer.keys()):
			pg.draw.rect(self.display, (30,) * 3, pg.Rect(rect.x + 25, rect.bottom - 55, rect.w - 50, 50))
			pg.draw.rect(self.display, (40,) * 3, pg.Rect(rect.x + 25, rect.bottom - 55, rect.w - 50, 5))
			pg.draw.rect(self.display, (40,) * 3, pg.Rect(rect.x + 25, rect.bottom - 55, 5, 50))
			text = self.small_header.render('OK', True, (60,)*3)
		else:
			pg.draw.rect(self.display, (60,) * 3, pg.Rect(rect.x + 25, rect.bottom - 55, rect.w - 50, 50))
			pg.draw.rect(self.display, (80,) * 3, pg.Rect(rect.x + 25, rect.bottom - 55, rect.w - 50, 5))
			pg.draw.rect(self.display, (80,) * 3, pg.Rect(rect.x + 25, rect.bottom - 55, 5, 50))
			text = self.small_header.render('OK', True, (120,)*3)
		self.display.blit(text, (rect.x + 25 + (rect.w - 50 - text.get_width())/2, rect.bottom - 50))

	def eventHandler(self, events):
		for event in events:
			if event.type == MOUSEBUTTONUP:
				if event.button == 1:
					h = self.question.get_height() + sum(
						70 + 50 * len(option_group['options'].values()) for option_group in self.option_groups)
					rect = pg.Rect((self.pos.x, self.pos.y - h / 4), (self.question.get_width() + 200, h))
					question_rect = self.question.get_rect(centerx=rect.centerx, top=rect.top)
					question_rect.bottom += 10
					top = question_rect.bottom
					for enum, option_group in enumerate(self.option_groups):
						options = option_group['options']
						
						top += option_group['question'].get_height()
						for en, (name, texture) in enumerate(options.items()):
							pos = pg.Rect((rect.centerx - texture.get_width() / 2, top), texture.get_size())
							if pos.collidepoint(event.pos):
								self.answer[self.DATA[enum]['question']] = name
								break
							top = top + 10 + texture.get_height()
					if pg.Rect(rect.x + 25, rect.bottom - 55, rect.w - 50, 50).collidepoint(event.pos) and \
							all(self.answer[key] is not None for key in self.answer.keys()):
						try:
							self.main.projects.append(Project(self.main, list(map(int, self.answer['Tile Size'].split('x')))))
							self.main.selected = len(self.main.projects) - 1
							del self.main.popups[-1]
						except IOError:
							pass
			elif event.type == KEYDOWN:
				if event.key == K_ESCAPE:
					del self.main.popups[-1]


class Layers:
	
	def __init__(self, display: pg.Surface, project: Project, pos: tuple[int, int] = None):
		if pos is None:
			pos = display.get_width()//15, display.get_height()//1.25
		self.display: pg.Surface = display
		self.project: Project = project
		self.header: pg.Font = project.header
		self.text: pg.Font = project.text
		self.pos: pg.Vector2 = pg.Vector2(pos)
		self.scroll: int = 0
		self.selected: bool = False
		
	def visualize(self) -> None:
		cl = self.project.window_outline_color if not self.selected else self.project.selected_window_outline_color
		
		layers: int = len(self.project.grid)
		height: int = min(layers, 5) * 50 + 50
		texture: pg.Surface = pg.Surface((350, height))
		text: pg.Surface = self.header.render("Layers", True, cl)
		texture.blit(text, ((texture.get_width() - text.get_width())/2, 10))
		pg.draw.line(texture, cl, (10, 10 + text.get_height()), (texture.get_width()-10, 10 + text.get_height()))
		
		y = 20 + text.get_height()
		for layer in range(max(0, self.project.current_layer), layers):
			layer_cl = (0, 0, 0)
			text_cl = (200, 200, 200)
			if layer == self.project.current_layer:
				layer_cl, text_cl = text_cl, layer_cl
				prefix = '_' if self.project.renaming else ''
			else:
				prefix = ''
			text: pg.Surface = self.text.render(self.project.layer_names[layer] + prefix, True, text_cl, layer_cl)
			pg.draw.rect(texture, layer_cl, (10, y, texture.get_width() - 10, 40))
			texture.blit(text, (10, y + 5))
			y += 40
		
		pg.draw.rect(self.display, cl, (self.pos-(2, 2), (350+4, height+4)), border_radius=15)
		self.display.blit(texture, self.pos)
	
	def event_handler(self, events):
		for event in events:
			if event.type == MOUSEMOTION:
				if event.buttons[0]:
					layers: int = len(self.project.grid)
					height: int = layers * 50 + 150
					if pg.Rect(self.pos, (350, height)).collidepoint(event.pos):
						self.pos += event.rel
						self.selected = True
			if event.type == MOUSEBUTTONUP:
				self.selected = False
	

if __name__ == '__main__':
	Main().run()
