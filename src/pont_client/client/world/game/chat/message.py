import datetime

class Message:
	def __init__(self, text: str):
		self.text = text
		self.time = datetime.time()