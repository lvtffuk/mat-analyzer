from src.analyzers.base import BaseAnalyzer
from io import BytesIO
from zipfile import ZipFile
from urllib.request import urlopen
import os
import gensim

corpus_url = "https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11858/00-097C-0000-0023-1B22-8/Czech_Named_Entity_Corpus_2.0.zip"

class LSI(BaseAnalyzer):

	def get_name(self) -> str:
		return "LSI"

	def get_default_config(self) -> dict:
		return {
			"num_topics": 200
		}

	def _analyze(self) -> None:
		# TODO deprecated?
		self._download_corpus()
		texts = self.get_texts()
		dictionary = gensim.corpora.Dictionary(texts)
		corpus = [dictionary.doc2bow(text) for text in texts]
		model = gensim.models.LsiModel(corpus, id2word=dictionary, num_topics=self.config["num_topics"])
		model.save(self.get_output_file_path("lsi.model"))

	def _download_corpus(self) -> None:
		if os.path.exists(self._get_corpus_path()):
			print("Corpus already downloaded")
			return
		print("Downloading corpus")
		resp = urlopen(corpus_url)
		with ZipFile(BytesIO(resp.read()), "r") as zip:
			zip.extractall(self._get_corpus_path())

	def _get_corpus_path(self) -> str:
		return self.get_output_file_path("corpus")