from typing import Optional


class SceneHandler:
	
	def __init__(self):
		self.scene: Optional[str] = None
		self.scene_data: dict[str, dict] = {}
	
	def add_scene_data(self, scene: str, data: dict) -> None:
		self.scene_data[scene] = data
	
	def data(self) -> dict:
		return self.scene_data[self.scene] if self.scene in self.scene_data else {}