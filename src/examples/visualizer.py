import pygame
import src.WorldD as WorldD
from dataclasses import dataclass
import typing

pygame.init()


@dataclass
class Config:
	"""Config class for tile layers"""
	TILE_LAYER = 0


class World:
	
	def __init__(self, main):
		tile_size, _, self.tiles, self.grid, layer_names = WorldD.load(
			'asset-world.world')
		# load the world and export the most important things
		self.tile_size = pygame.Vector2(tile_size) * main.SCALE
		# scale the tile size
		self.sp_sheet = pygame.image.load('asset-img.png')
		# load the sp_sheet (loading from the WorldD.load is not the best option
		# since the path will not be the same on every computer
		self.display = main.display
		# assign the display
		self.tile_x, self.tile_y = main.AMOUNT_OF_TILES_IN_ROW, 6
		# setup how many tiles there will be in one row and column
		
		self.tile_cache = {
			Config.TILE_LAYER: {}
		}
		# setup caching for better performance
	
	def render(self):
		# for every row visible
		for x in range(0, self.tile_x):
			# for every column visible
			for y in range(0, self.tile_y):
				
				# if tile doesn't exist: next loop
				if (x, y) not in self.grid[Config.TILE_LAYER]:
					continue

				if (x, y) not in self.tile_cache[Config.TILE_LAYER]:
					# if tile not cache:

					# gather the information about tile group and name
					tile_group, tile_name = self.grid[Config.TILE_LAYER][(x, y)]
					# get subsurface pos
					tile_subsurface_pos = self.tiles[tile_group].tiles[tile_name]
					# get texture
					tile_texture = self.sp_sheet.subsurface(tile_subsurface_pos)
					# scale texture
					tile_texture = pygame.transform.scale(tile_texture, self.tile_size)
					# cache it
					self.tile_cache[Config.TILE_LAYER][(x, y)] = tile_texture
				else:
					# if tile is in cache: retrieve it
					tile_texture = self.tile_cache[Config.TILE_LAYER][(x, y)]
				
				# render tile
				self.display.blit(tile_texture,
								  (
									  x * self.tile_size[0],
									  y * self.tile_size[1]
								  ))


class Main:

	FPS = 60
	AMOUNT_OF_TILES_IN_ROW = 16
	SCALE = pygame.display.get_desktop_sizes()[0][0] // (
		16 * AMOUNT_OF_TILES_IN_ROW
	)
	WINDOW_SIZE: typing.Sequence[float] = pygame.display.get_desktop_sizes()[0]
	
	def __init__(self):
		
		self.display = pygame.display.set_mode(self.WINDOW_SIZE)
		# create display
		self.world = World(self)
		self.clock = pygame.time.Clock()
	
	def render(self):
		# fill the screen black (erase what was previously there)
		self.display.fill('black')
		# render world
		self.world.render()
		# flip the buffers and tick the clock
		pygame.display.flip()
		self.clock.tick(self.FPS)
		pygame.display.set_caption(f'{round(self.clock.get_fps())} fps')
	
	@staticmethod
	def exit():
		"""exit method, will be run on the exit of the game"""
		pygame.quit()
		exit()
	
	def update(self):
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.exit()
	
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
