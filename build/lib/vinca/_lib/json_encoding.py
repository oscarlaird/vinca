import json
import datetime

class CustomJSONEncoder(json.JSONEncoder):

	def default(obj):
		if type(obj) is datetime.date:
			return str(obj)  # use iso format
		elif hasattr(obj, '__dataclass_fields__'):
			return vars(obj)  # used for serializing dataclasses
		else:
			raise TypeError
