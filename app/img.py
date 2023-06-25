import pygame as pg

pg.init()


def load(image: str) -> pg.Surface:
	return pg.image.load(image)


def partition(image: pg.Surface, pos: list[int, int] | tuple[int, int], size: list[int, int] | tuple[int, int]) -> pg.Surface:
	return image.subsurface(pg.Rect(pos, size))


def scale(image: pg.Surface, size: list[int|float, int|float] | tuple[int|float, int|float]) -> pg.Surface:
	return pg.transform.scale(image, size)


class DefColor:

	background = pg.Color(222, 225, 189)
	tab_background = pg.Color(90, 105, 136)
	background_line = pg.Color(139, 155, 180)
	text_header = pg.Color(255,255,255)
	

class DefImgs:

	button = scale(load('.\\app\\GUI\\images\\button.png'), (256, 128))
	textbox = load('.\\app\\GUI\\images\\textbox.png')
	