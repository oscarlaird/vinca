''' cache card tags for use in tab completions '''
from pathlib import Path
from vinca._config import config

vinca_path = Path(__file__).parent
tags_path = vinca_path / 'tags'
if not tags_path.exists():
	tags_path.touch()

class TagsCache(list):
	def __init__(self):
		tags = tags_path.read_text().splitlines()
		super().__init__(tags)

	def update(self, new_tag_list):
		self[:] = new_tag_list
		self._save()

	def save(self):
		tags_path.write_text('\n'.join(self))
	
	def add_tag(self, tag):
		if tag not in self:
			self.append(tag)
			self.save()

	def add_tags(self, tags):
		for tag in tags:
			self.add_tag(tag)

tags_cache = TagsCache()

	
		
