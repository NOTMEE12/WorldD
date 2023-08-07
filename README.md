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
- `SHIFT + X` - rect autotile fill tool
- `Up and Down arrows` - scaling size of the tile,
- `CTRL + DELETE` - delete tile from lookup (all occurrences of tile will be deleted),
  > by renaming the tiles in the lookup, every tile in the grid will be replaced.
##### saving / loading
- `CTRL + S` - save output,
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