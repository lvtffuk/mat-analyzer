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
	stop_words: list[str] = []

	config: dict = {}

	nlp = None

	def __init__(
		self, 
		input_file: str, 
		data_key: str, 
		doc_id_key: str, 
		output_dir: str, 
		config_file: str, 
		**options # TODO typings
	) -> None:
		self.input_file = input_file
		self.data_key = data_key
		self.doc_id_key = doc_id_key
		self.output_dir = output_dir
		self.config = self.get_default_config()
		if config_file:
			with open(config_file, "rb") as config:
				self.config = self.config | yaml.safe_load(config)
		self.lang = options.get("language") or "cs"
		self.csv_separator = options.get("csv_separator") or ";"
		if options.get("stop_words"):
			self.stop_words = self.read_csv(options.get("stop_words"))[0].values.tolist()

	@abstractmethod
	def get_name(self) -> str:
		pass

	def analyze(self) -> None:
		print(f"Running analyzer '{self.get_name()}' {self.config}")
		self.check()
		self.prepare()
		print("Analyzing")
		self._analyze()

	def check(self) -> None:
		if not os.path.exists(self.output_dir):
			raise ValueError(f"Out dir '{self.output_dir}' doesn't exist")
		if not os.path.exists(self.input_file):
			raise ValueError(f"Input file '{self.input_file}' doesn't exist")
		if not self.doc_id_key:
			raise ValueError("No Document ID key defined")
		if not self.data_key:
			raise ValueError("No Data key defined")

	def prepare(self):
		spacy_udpipe.download(self.lang)
		self.nlp = spacy_udpipe.load(self.lang)
		with open(self.input_file, mode="r", encoding="utf8") as input_file:
			if self.udpipe_exists(input_file):
				print("Udpipe file for input exists.")
				return
			print("Generating udpipe file")
			input_file.seek(0)
			# TODO read with pandas?
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

	# Gets the list of separated words from the sentences.
	# The words are lowercased and stripped.
	def get_texts(self) -> list[list[str]]:
		return list(map(lambda s: list(map(lambda s: s.lower().strip(".,?!\n"), s.split(" "))), self.get_sentences()))

	def get_sentences(self) -> list[str]:
		df = self.read_csv(self.get_udpipe_file_path())
		return df[1].str.strip().tolist()

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

	def get_udpipe_data_file_path(self) -> str:
		return self.get_output_file_path("udpipe-data.csv")

	def get_output_file_path(self, filename: str) -> str:
		return f"{self.output_dir}/{filename}"

	def read_csv(self, filename: str, header: bool = False) -> pd.DataFrame:
		"""
		Reads the CSV file.

		:param filename: The path to the file.
		:param header: Indicates if the file contains header and the header data are skipped.
		:return: Data frame.
		""" 
		data = pd.read_csv(filename, header=None, sep=f'"\s*[|{self.csv_separator}]\s*"', encoding="utf8", engine="python")
		data = data.transform(lambda s: s.str.strip("\""))
		if header:
			return data.iloc[1:]
		return data

	@abstractmethod
	def _analyze(self) -> None:
		pass