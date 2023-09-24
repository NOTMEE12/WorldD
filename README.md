# WorldD - level designer for pygame
[![Upload Python Package](https://github.com/NOTMEE12/WorldD/actions/workflows/python-publish.yml/badge.svg)](https://github.com/NOTMEE12/WorldD/actions/workflows/python-publish.yml)

---
### Shortcuts:

------------------------
##### window related
- `SHIFT + ESCAPE` - quit the application,
- `F11` - toggling fullscreen,
##### tile related
- `W` - brush tool (default)
- `X` - rect fill tool
- `E` - reset tile to nothing (eraser)
- `SHIFT + X` - rect autotile fill tool
- `Up and Down arrows` - scaling size of the tile,
- `CTRL + DELETE` - delete tile from lookup (all occurrences of tile will be deleted),
  > by renaming the tiles in the lookup, every tile in the grid will be replaced.
- `CTRL + T` - toggle tile mode
  > tile mode is when you want to add new tiles or delete them
- `ALT + E` - export tiles
  > classically you have two inputs, one for the tile group name and one for the tile name. 
  > 
  > export feature will make so it will generate tiles from starting point to the end selection
  > with each tiles having the selected tile size.
  >
  > for example, you will start at 0x0 and end at 0x64 with the tile size being (32, 32) 
  > and name of the tile being "tiles":
  > 
  > you will have tiles: 
  > 
  > (0, 0, 32, 32) - "tiles - 0x0", 
  > 
  > (0, 32, 32, 32) - "tiles - 1x0", 
  > 
  > (0, 64, 32,32) - "tiles - 2x0"
- `CTRL + E` - edit tile
  > when editing tiles they aren't replaced, they make a new copy.
    making it replace could break the entire map, since the map is "indexed",
    that means each tile is a reference for a tile group and a tile in it.
- `<` or `>` - toggle between editting group name and tile name
##### saving / loading
- `CTRL + S` - save output,
- `CTRL + SHIFT + s` - save as,
- `CTRL + O` - load world,
##### Project related
- `Q` - move project selection to left
- `E` - move project selection to right
##### Layers
- `right arrow` - new layer / change selection to the layer above
- `left arrow` - change selection to the layer below, you can't select layers below 0.
- `CTRL + R` - rename layer
- `SHIFT + DELETE` - deletes current layer

---
### Important Info

1. > path of the image is absolute. If you want to use WorldD you have to change the path to be relative, 
   > otherwise there is a very high probability it will not work.