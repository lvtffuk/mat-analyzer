from src.analyzers.base import BaseAnalyzer
import csv
from dicttoxml import dicttoxml

class VT(BaseAnalyzer):

	def get_name(self) -> str:
		return "Voyant Tools"

	def get_default_config(self) -> dict:
		return {}

	def check(self) -> None:
		super().check()
		if not "author_key" in self.config:
			raise ValueError("author_key missing in config.")
		if not "published_key" in self.config:
			raise ValueError("published_key missing in config.")

	def prepare(self):
		pass	

	def _analyze(self) -> None:
		with open(self.input_file, mode="r", encoding="utf8") as input_file:
			input_file.seek(0)
			reader = csv.reader(input_file, delimiter=self.csv_separator, quotechar="\"", quoting=csv.QUOTE_ALL, skipinitialspace=True)
			header = next(reader)
			try:
				data_index = header.index(self.data_key)
			except:
				data_index = -1
			try:
				doc_id_index = header.index(self.doc_id_key)
			except:
				doc_id_index = -1
			try:
				author_index = header.index(self.config["author_key"])
			except:
				author_index = -1
			try:
				published_index = header.index(self.config["published_key"])
			except:
				published_index = -1
			if (data_index < 0):
				raise ValueError(f"Data key '{self.data_key}' missing in the input file.") 
			if (doc_id_index < 0):
				raise ValueError(f"Doc ID key '{self.doc_id_key}' missing in the in put file.")	
			if (author_index < 0):
				raise ValueError(f"Author key '{self.config['author_key']}' missing in the input file.") 
			if (published_index < 0):
				raise ValueError(f"Published key '{self.config['published_key']}' missing in the in put file.")
			data = []
			for row in reader:
				data.append({
					"id": row[doc_id_index],
					"content": row[data_index],
					"author": row[author_index],
					"published": row[published_index]
				})
			with open(self.get_output_file_path("voyant-tools.xml"), mode="wb") as xml:
				xml.write(dicttoxml(data, custom_root="items", attr_type=False))
