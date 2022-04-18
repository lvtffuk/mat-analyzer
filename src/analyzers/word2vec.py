from src.analyzers.base import BaseAnalyzer
import gensim

class Word2Vec(BaseAnalyzer):

	def get_name(self) -> str:
		return "Word2Vec"

	def get_default_config(self) -> dict:
		return {
			"vector_size": 100,
			"window": 5,
			"min_count": 1,
			"workers": 4
		}

	def _analyze(self) -> None:
		model = gensim.models.Word2Vec(
			sentences=self._get_texts(), 
			vector_size=self.config["vector_size"],
			window=self.config["window"],
			min_count=self.config["min_count"],
			workers=self.config["workers"]
		)
		model.save(self.get_output_file_path("word2vec.model"))
		sims = model.wv.most_similar("fotbal", topn=10)  # get other similar words

		print(sims)

	# Gets the list of separated words from the sentences.
	# The words are lowercased and stripped.
	def _get_texts(self) -> list[list[str]]:
		return list(map(lambda s: list(map(lambda s: s.lower().strip(".,?!\n"), s.split(" "))), self.get_sentences()))