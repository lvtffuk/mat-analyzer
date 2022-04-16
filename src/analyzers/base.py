from abc import abstractmethod
import csv
import hashlib
from io import TextIOWrapper
import os
from langdetect import detect
import spacy_udpipe
import yaml
import pandas as pd

class BaseAnalyzer:

	input_file: str
	data_key: str
	doc_id_key: str
	output_dir: str
	lang: str = "cs"
	csv_separator: str = ";"

	config: dict = {}

	nlp = None

	def __init__(self, input_file: str, data_key: str, doc_id_key: str, output_dir: str, config_file: str) -> None:
		self.input_file = input_file
		self.data_key = data_key
		self.doc_id_key = doc_id_key
		self.output_dir = output_dir
		if config_file:
			with open(config_file, "rb") as config:
				self.config = self.get_default_config() | yaml.safe_load(config)

	@abstractmethod
	def get_name(self) -> str:
		pass

	def analyze(self) -> None:
		self.check()
		self.prepare()
		self._analyze()

	def check(self) -> None:
		if not os.path.exists(self.output_dir):
			raise ValueError(f"Out dir '{self.output_dir}' doesn't exist")
		spacy_udpipe.download(self.lang)
		self.nlp = spacy_udpipe.load(self.lang)

	def prepare(self):
		with open(self.input_file, mode="r", encoding="utf8") as input_file:
			if self.udpipe_exists(input_file):
				print("Udpipe file for input exists.")
				return
			print("Generating udpipe file")
			input_file.seek(0)
			reader = csv.reader(input_file, delimiter=self.csv_separator)
			header = next(reader)
			try:
				data_index = header.index(self.data_key)
			except:
				data_index = -1
			try:
				doc_id_index = header.index(self.doc_id_key)
			except:
				doc_id_index = -1
			if (data_index < 0):
				raise ValueError(f"Data key '{self.data_key}' missing in the input file.") 
			if (doc_id_index < 0):
				raise ValueError(f"Doc ID key '{self.doc_id_key}' missing in the in put file.")	
			with open(self.get_udpipe_file_path(), mode="w", encoding="utf8") as udpipe_file:
				with open(self.get_output_file_path("udpipe-data.csv"), mode="w", encoding="utf8") as udpipe_data_file:
					for row in reader:
						key = row[doc_id_index]
						value = row[data_index]
						if self.check_lang(value):
							doc = self.nlp(value)
							if doc == None:
								continue
							for token in doc:
								row_data = [key, token.text, token.lemma_, token.pos_, token.dep_]
								udpipe_data_file.write(f"{self.create_csv_row(row_data)}\n")
							updated = value
							for token in reversed(doc): #reversed to not modify the offsets of other entities when substituting
								start = token.idx
								end = start + len(token.text)
								updated = updated[:start] + token.lemma_ + updated[end:]
							udpipe_file.write(f"{self.create_csv_row([key, updated])}\n")
					with open(f"{self.output_dir}/udpipe.md5", "w") as file:
						file.write(self.get_file_md5(input_file))

	def check_lang(self, text: str) -> bool:
		try:
			return detect(text) == self.lang
		except:
			return False

	def create_csv_row(self, data: list[str]) -> str:
		return self.csv_separator.join(list(map(lambda item: f"\"{item}\"", data)))

	def udpipe_exists(self, file: TextIOWrapper) -> bool:
		path = f"{self.output_dir}/udpipe.md5"
		hash = self.get_file_md5(file)
		if not os.path.exists(path):
			return False
		with open(path, "r") as file:
			saved_hash = file.read().strip()
			return hash == saved_hash

	def get_default_config(self) -> dict:
		return {}

	def get_file_md5(self, file: TextIOWrapper) -> str:
		file.seek(0)
		hash = hashlib.md5()
		while chunk := file.read(8192):
			hash.update(chunk.encode("utf8"))
		return hash.hexdigest()

	def get_udpipe_file_path(self) -> str:
		return self.get_output_file_path("udpipe.csv")

	def get_output_file_path(self, filename: str) -> str:
		return f"{self.output_dir}/{filename}"

	def read_csv(self, filename: str, header: bool = False) -> str:
		data = pd.read_csv(filename, header=None, sep=f'"\s*[|{self.csv_separator}]\s*"', encoding="utf8")
		data = data.transform(lambda s: s.str.strip("\""))
		if header:
			return data.iloc[1:]
		return data

	@abstractmethod
	def _analyze(self) -> None:
		pass