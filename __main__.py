import importlib
from inspect import getmembers, isclass
import os
from types import ModuleType
from dotenv import load_dotenv
from src.analyzers.base import BaseAnalyzer

load_dotenv()

if os.getenv("CLEAR", False) == "1": 
	out_dir = os.getenv("OUTPUT_DIR")
	for filename in os.listdir(out_dir):
		os.unlink(os.path.join(out_dir, filename))

analyzerName: str = os.getenv("ANALYZER")

analyzerModule: ModuleType = importlib.import_module(f".{analyzerName.lower()}", "src.analyzers")

analyzerClassName: str
for name, cls in getmembers(analyzerModule, isclass):
	if name.lower() == analyzerName.lower():
		analyzerClassName = name 
	
if not analyzerName:
	raise ValueError(f"Invalid analyzer '{analyzerName}'")

AnalyzerClass = getattr(analyzerModule, analyzerClassName)

analyzer: BaseAnalyzer = AnalyzerClass(
	os.getenv("INPUT_FILE"), 
	os.getenv("DATA_KEY"),
	os.getenv("DOC_ID_KEY"),
	os.getenv("OUTPUT_DIR"),
	os.getenv("CONFIG_FILE")
)

analyzer.analyze()
