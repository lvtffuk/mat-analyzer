from src.analyzers.base import BaseAnalyzer
import gensim
from gensim.utils import simple_preprocess
import nltk
from nltk.corpus import stopwords
import gensim.corpora as corpora

class LDA(BaseAnalyzer):

	def get_name(self) -> str:
		return "LDA"

	def get_default_config(self) -> dict:
		return {
			"num_topics": 10
		}

	def _analyze(self) -> None:
		# nltk.download("stopwords")
		# stop_words = stopwords.words("czech")
		df = self.read_csv(self.get_udpipe_data_file_path())
		df = df.loc[(df[3] != "PUNCT") & (df[3] != "SYM") & (~df[2].isin(self.stop_words))]
		df[2] = df[2].map(lambda x: x.lower())
		data = df[2].values.tolist()
		id2word = corpora.Dictionary([data])
		texts = [data]
		corpus = [id2word.doc2bow(text) for text in texts]
		lda_model = gensim.models.LdaMulticore(
			corpus=corpus,
			id2word=id2word,
			num_topics=self.config["num_topics"]
		)
		lda_model.save(self.get_output_file_path("lda.model"))