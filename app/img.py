import pygame as pg

pg.init()


def load(image: str) -> pg.Surface:
	return pg.image.load(image)


def partition(image: pg.Surface, pos, size):
	return image.subsurface(pg.Rect(pos, size))


class DefaultImages:

	button = load('')