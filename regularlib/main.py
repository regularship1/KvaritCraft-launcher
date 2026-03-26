import os
from importlib.resources import files
from PIL import Image
from PIL.ImageTk import PhotoImage

class icons:
	def __init__(self, width, height):
		print("regularlib icons made by icons8.com")
		iconspath = files(__package__).joinpath("Assets", "Icons")
		for photo in os.listdir(iconspath):
			if os.path.splitext(photo)[1] == ".png":
				setattr(self, str(os.path.splitext(photo)[0]), PhotoImage(image=Image.open(os.path.join(iconspath, photo)).resize((width, height))))
