from src.analyzers.base import BaseAnalyzer

class Gensim(BaseAnalyzer):

	def get_name(self) -> str:
		return "gensim"