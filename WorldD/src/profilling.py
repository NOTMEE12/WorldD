import cProfile
from .main import Main

cProfile.run("Main().run()", sort='tottime')