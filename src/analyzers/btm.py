from src.analyzers.base import BaseAnalyzer
import bitermplus as btm
import pandas as pd
import numpy as np
import pickle

class Btm(BaseAnalyzer):

	def get_name(self) -> str:
		return "btm"

	def get_default_config(self) -> dict:
		return {
			"iterations": 20,
			"seed": 12321,
			"T": 8,
			"M": 20,
			"alpha": 50 / 8,
			"beta": 0.01
		}

	def _analyze(self) -> None:	
		texts = self._prepare_texts()
		# PREPROCESSING
		# Obtaining terms frequency in a sparse matrix and corpus vocabulary
		X, vocabulary, vocab_dict = btm.get_words_freqs(texts)
		tf = np.array(X.sum(axis=0)).ravel()
		# Vectorizing documents
		docs_vec = btm.get_vectorized_docs(texts, vocabulary)
		docs_lens = list(map(len, docs_vec))
		# Generating biterms
		biterms = btm.get_biterms(docs_vec)
		
		# INITIALIZING AND RUNNING MODEL
		model = btm.BTM(
			X, 
			vocabulary, 
			seed=self.config["seed"], 
			T=self.config["T"], 
			M=self.config["M"], 
			alpha=self.config["alpha"], 
			beta=self.config["beta"]
		)
		model.fit(biterms, iterations=self.config["iterations"])
		with open(self.get_output_file_path("btm-model.pkl"), "wb") as file:
			pickle.dump(model, file)


		# Testing data
		p_zd = model.transform(docs_vec)

		# METRICS
		perplexity = btm.perplexity(model.matrix_topics_words_, p_zd, X, 8)
		coherence = btm.coherence(model.matrix_topics_words_, X, M=20)

		print(btm.get_docs_top_topic(texts, model.matrix_docs_topics_))
		print(perplexity)
		print(coherence)
		print(model.labels_)

	def _prepare_texts(self) -> list[str]:
		df = self.read_csv(self.get_udpipe_file_path())
		return df[1].str.strip().tolist()
