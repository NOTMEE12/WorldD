import pygame
import WorldD
from dataclasses import dataclass
import typing
import sys

pygame.init()


@dataclass
class Config:
	"""Config class for tile layers"""
	TILE_LAYER = 0
	
	MOVE_UP = pygame.K_w
	MOVE_LEFT = pygame.K_a
	MOVE_RIGHT = pygame.K_d
	MOVE_DOWN = pygame.K_s


class Player:
	
	def __init__(self, main):
		self.main: Main = main
		self.display = main.display
		self.texture = main.sp_sheet.subsurface((16, 64, 16, 16))
		self.texture = pygame.transform.scale(self.texture, main.world.tile_size)
		self.pos = self.texture.get_rect(center=pygame.Vector2(self.display.get_size())/2)
		
		self.hitbox = pygame.Surface(main.world.tile_size)
		self.hitbox.fill('red')

	@property
	def block_pos(self):
		return self.main.world.get_block_pos(self.pos)
	
	def render(self):
		self.display.blit(self.hitbox, self.main.world.block_render_pos(self.block_pos))
		self.display.blit(self.texture, self.pos)


class World:
	
	def __init__(self, main):
		# load the world and export the most important things
		tile_size, _, self.tiles, self.grid, layer_names = WorldD.load('asset-world.world')
		# scale the tile size
		self.tile_size = pygame.Vector2(tile_size) * main.SCALE
		
		# load the sp_sheet (loading from the WorldD.load is not the best option
		# since the path will not be the same on every computer
		self.sp_sheet = main.sp_sheet
		
		# assign the display and main
		self.display = main.display
		self.main = main
		
		self.tile_x, self.tile_y = main.AMOUNT_OF_TILES_IN_ROW, 7
		# setup how many tiles there will be in one row and column
		
		# setup caching for better performance
		self.tile_cache = {
			Config.TILE_LAYER: {}
		}
		self.block_render_pos_cache = {}
	
	def get_block_pos(self, pos, offset: typing.Union[typing.Sequence[int], None] = None):
		if offset is None:
			offset = self.main.offset[0] * self.tile_size[0], self.main.offset[1] * self.tile_size[1]
		return pygame.Vector2(pos[0] - offset[0], pos[1] - offset[1]) // self.tile_size[0]
	
	def block_render_pos(self, grid_pos, cache=True,
						 offset: typing.Union[
							 typing.Sequence[int], None] = None) -> tuple[
		int, int]:
		"""
		:parameter grid_pos: position on the grid
		:parameter offset: offset of Main offset * tile size, if not given then calculated in this function.
		:returns: position where tile should be rendered based on the grid position
		"""
		if cache:
			if tuple(grid_pos) not in self.block_render_pos_cache:
				self.block_render_pos_cache[tuple(grid_pos)] = (
					self.tile_size[0] * grid_pos[0],
					self.tile_size[1] * grid_pos[1])
			if offset is None:
				offset = self.main.offset * self.tile_size[0]
			return self.block_render_pos_cache[tuple(grid_pos)][0] + offset[0], \
				   self.block_render_pos_cache[tuple(grid_pos)][1] + offset[1]
		else:
			if offset is None:
				offset = self.main.offset * self.tile_size[0]
			return \
				self.tile_size[0] * grid_pos[0] + offset[0], \
				self.tile_size[1] * grid_pos[1] + offset[1]
	
	def render(self):
		offset = self.main.offset[0] * self.tile_size[0], self.main.offset[1] * \
				 self.tile_size[1]
		left, top = -int(offset[0] // self.tile_size[0]) - 1, -int(
			offset[1] // self.tile_size[1]) - 1
		right, bottom = int(
			left + self.display.get_width() // self.tile_size[0]) + 2, int(
			top + self.display.get_height() // self.tile_size[1]) + 1
		# for every row visible
		for x in range(left, right):
			
			# for every column visible
			for y in range(top, bottom):
				
				# if tile doesn't exist: next loop
				if (x, y) not in self.grid[Config.TILE_LAYER]:
					continue
				# if tile not cache:
				if (x, y) not in self.tile_cache[Config.TILE_LAYER]:
					# gather the information about tile group and name
					tile_group, tile_name = self.grid[Config.TILE_LAYER][(x, y)]
					# get subsurface pos
					tile_subsurface_pos = self.tiles[tile_group].tiles[
						tile_name]
					# get texture
					tile_texture = self.sp_sheet.subsurface(tile_subsurface_pos)
					# scale texture
					tile_texture = pygame.transform.scale(tile_texture,
														  self.tile_size)
					# cache it
					self.tile_cache[Config.TILE_LAYER][(x, y)] = tile_texture
				else:
					# if tile is in cache: retrieve it
					tile_texture = self.tile_cache[Config.TILE_LAYER][(x, y)]
				
				# render tile
				self.display.blit(tile_texture,
								  self.block_render_pos((x, y), offset=offset))


class Main:
	FPS = 60
	AMOUNT_OF_TILES_IN_ROW = 16
	SCALE = 6
	WINDOW_SIZE: typing.Sequence[float] = pygame.display.get_desktop_sizes()[0]
	sp_sheet = pygame.image.load('asset-img.png')
	
	def __init__(self):
		
		# create display
		self.display = pygame.display.set_mode((16 * 75, 9 * 75))

		self.world = World(self)
		self.player = Player(self)
		self.clock = pygame.time.Clock()
		
		# offset
		self.offset = pygame.Vector2(0, 4)
	
	def render(self):
		# fill the screen black (erase what was previously there)
		self.display.fill('black')
		# render world
		self.world.render()
		# render player
		self.player.render()
		
		# flip the buffers and tick the clock
		pygame.display.flip()
		self.dt = self.clock.tick(self.FPS) / 1000
		pygame.display.set_caption(f'{round(self.clock.get_fps())} fps')
	
	@staticmethod
	def exit():
		"""exit method, will be run on the exit of the game"""
		pygame.quit()
		sys.exit()
	
	def update(self):
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.exit()
		keys = pygame.key.get_pressed()
		speed = self.dt * self.SCALE
		block_pos = self.player.block_pos
		world = self.world.grid[Config.TILE_LAYER]
		pos = (block_pos[0], block_pos[1] - 1)
		tile_up = ('', '')
		if pos in world:
			tile_up = world[pos]
		
		pos = (block_pos[0], block_pos[1] + 1)
		tile_down = ('', '')
		if pos in world:
			tile_down = world[pos]
		
		pos = (block_pos[0] - 1, block_pos[1])
		tile_left = ('', '')
		if pos in world:
			tile_left = world[pos]
		
		pos = (block_pos[0] + 1, block_pos[1])
		tile_right = ('', '')
		if pos in world:
			tile_right = world[pos]
		
		if keys[Config.MOVE_UP] and 'not-mov' not in tile_up[0]:
			self.offset.y += speed
		if keys[Config.MOVE_DOWN] and 'not-mov' not in tile_down[0]:
			self.offset.y -= speed
		if keys[Config.MOVE_LEFT] and 'not-mov' not in tile_left[0]:
			self.offset.x += speed
		if keys[Config.MOVE_RIGHT] and 'not-mov' not in tile_right[0]:
			self.offset.x -= speed
	
	def run(self):
		while True:
			self.render()
			self.update()


if __name__ == '__main__':
	run_build = input('run WorldD (y/n): ') == 'y'
	if run_build:
		WorldD.Main().run()
	else:
		Main().run()
