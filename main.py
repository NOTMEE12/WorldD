from app.PygameBase import *
from app.img import DefImgs, DefColor, scale
import app
import sys


class Main(app.SceneHandler, PgBase):
	
	def __init__(self):
		app.SceneHandler.__init__(self)
		PgBase.__init__(self, pg.Vector2(pg.display.get_desktop_sizes()[0]), flags=FULLSCREEN)
		self.tabs = [sys.argv[1] if len(sys.argv) > 1 else "choose project"]
		self.scene = sys.argv[1] if len(sys.argv) > 1 else 'choose project'
		self.resize()
		
	def resize(self):
		self.add_scene_data('choose project',
		                    {
			                    'tab-height': 12,
		                    }
		                    )
		
	def refresh(self):
		self.display.fill(DefColor.background)
		data = self.data()
		if self.scene == 'choose project':
			for i, tab in enumerate(self.tabs):
				pos = (i * DefImgs.button.get_width(), data['tab-height'])
				text_size = self.headers.size(tab)
				self.display.blit(DefImgs.button, pos)
				self.display.blit(self.headers.render(tab, True, DefColor.text_header),
				                  (
					                  pos[0]+(DefImgs.button.get_width()-text_size[0])/2,
					                  pos[1]+(DefImgs.button.get_height()-text_size[1])/2.5
				                  ))
			size = pg.Rect(0, data['tab-height']+DefImgs.button.get_height(),
			               self.display.get_width(), self.display.get_height())
			pg.draw.rect(self.display, DefColor.tab_background, size)
			pg.draw.line(self.display, DefColor.background_line,
			                 (len(self.tabs)*DefImgs.button.get_width(), data['tab-height']+DefImgs.button.get_height()),
			                 (self.display.get_width(), data['tab-height']+DefImgs.button.get_height()),4)
			self.display.blit(scale(DefImgs.textbox, (size.w/2-20,size.h/2-20)), (size.x+10,size.y+10))
			
	def EventHandler(self):
		self.events = pg.event.get()
		for event in self.events:
			if event.type == QUIT:
				self.exit()
			if event.type == WINDOWRESIZED:
				self.resize()
			if self.scene == 'choose project': pass
			if event.type == KEYDOWN:
				if event.key == K_ESCAPE:
					return True
	
	def run(self):
		while True:
			self.refresh()
			if self.EventHandler():
				return True
			PgBase.refresh(self)
		
		
if __name__ == '__main__':
	app = Main()
	app.run()
			