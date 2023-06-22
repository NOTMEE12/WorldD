from app.PygameBase import *
import app


class Main(app.SceneHandler, PgBase):
	def __init__(self):
		app.SceneHandler.__init__(self)
		PgBase.__init__(self, (500, 500))
		self.scene = 'choose project'
		self.add_scene_data('choose project',
		                    {
			                    'new': pg.Rect((self.win.x / 2, self.win.y / 2 - 64), (64, 32)),
			                    'load': pg.Rect((self.win.x / 2, self.win.y / 2 + 64), (64, 32)),
			                    'img': {'new': app.load()}
		                    }
		                    )
		
	def refresh(self):
		self.screen.fill("black")
		if self.scene == 'choose project':
		
		
	def EventHandler(self):
		self.events = pg.event.get()
		for event in self.events:
			if self.scene == 'choose project':
				if event.type == MOUSEBUTTONDOWN:
					if self.data()['new'].collidepoint(event.pos):
						self.scene = 'new project'
					elif self.data()['load'].collidepoint(event.pos):
						self.scene = 'load project'
	
	def run(self):
		while True:
			self.refresh()
			self.EventHandler()
			PgBase.refresh(self)
		
if __name__ == '__main__':
	app = Main()
	app.run()
			