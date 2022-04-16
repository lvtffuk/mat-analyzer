import importlib
import os
from dotenv import load_dotenv
from src.analyzers.base import BaseAnalyzer
load_dotenv()

analyzerName: str = os.getenv("ANALYZER")

AnalyzerClass = getattr(importlib.import_module(f".{analyzerName.lower()}", "src.analyzers"), analyzerName)

analyzer: BaseAnalyzer = AnalyzerClass(
	os.getenv("INPUT_FILE"), 
	os.getenv("DATA_KEY"),
	os.getenv("DOC_ID_KEY"),
	os.getenv("OUTPUT_DIR"),
	os.getenv("CONFIG_FILE")
)

analyzer.analyze()
