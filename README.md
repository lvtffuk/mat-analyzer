# mat-analyzer
Text analyzer for data for Media Analytics Tool project.

## Development
### Requirements
- Python 3
- `gcc` and `g++` libraries
### Installation & test run
```bash
git clone git@github.com:zabkwak/mat-analyzer.git
cd mat-analyzer
pip install -r requirements.txt
python ./
```
### Creating new analyzer
New analyzer is created when the module is defined in `src/analyzers`. The class must extend `BaseAnalyzer` and at least define `get_name` and `_analyze` methods.
```python
# test.py
from src.analyzers.base import BaseAnalyzer

class Test(BaseAnalyzer):

	def get_name(self) -> str:
		return "Test"

	def _analyze(self) -> None:
		# Do some stuff
```
Analyzers are loaded as modules by the name defined in the env vars.

## Settings
The settings are set with environment variables. 
Variable | Description | Required | Default value
:------------ | :------------- | :-------------| :-------------
`ANALYZER` | The analyzer to use. The app can be run with different analyzers on same input data. | :heavy_check_mark: | 
`INPUT_FILE` | The filepath of the `csv` file with input file texts. | :heavy_check_mark: | 
`OUTPUT_DIR` | The directory where the output is stored. | :heavy_check_mark: | 
`DATA_KEY` | The column in the input `csv` file where are the texts. | :heavy_check_mark: | 
`DOC_ID_KEY` | The column in the input `csv` file where the document ID is. | :heavy_check_mark: | 
`CSV_SEPARATOR` | The separator of the input `csv` files. | :x: | `;`
`CONFIG_FILE` | The path to the config `yml` file of the analyzer. | :x: | `None`
`LANGUAGE` | The language for the udpipe analysis. | :x: | `cs`
`CLEAR` | Indicates if the output dir should be cleared before the run. All downloads are starting again. | :x: | `0`

## Input file
The input `csv` file must contain at least two columns. One with document ids and one with the texts to analyze.
### Example
#### Example
```csv
"doc_id";"text";"additional_field"
"1";"Some text";"foo"
"2";"Some other text";"bar"
```
First line must be a header.

## Analyzers
### BTM
Creates [Biterm Topic Model](https://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.402.4032&rep=rep1&type=pdf) from lemmatized texts. The model is stored as `btm-model.pkl` in the output directory.
#### Configuration
```yaml
iterations: 20
seed: 12321
T: 8
M: 20
alpha: 6.25
beta: 0.01
```
### LSI
Creates [LSI](https://radimrehurek.com/gensim/models/lsimodel.html) model from lemmatized texts. The model is stored as `lsi.model` and `lsi.model.projection` in the output directory.
### Word2Vec
Creates [Word2Vec](https://en.wikipedia.org/wiki/Word2vec) model from lemmatized texts. The model is stored as `word2vec.model` file in the output directory.
#### Configuration
```yaml
vector_size: 100
window: 5
min_count: 1
workers: 4
```
### VT
Creates XML file for [Voyant tools](https://voyant-tools.org/). The file is stored as `voyant-tools.xml` in the output directory.
#### Configuration
```yaml
author_key: 'author'
published_key: 'published'
```
##### author_key
The column in the input file representing the author. The field is required.
##### published_key
The column in the input file representing the publication time of the text. The field is required.
#### Import
The file should be uploaded in the [Voyant tools](https://voyant-tools.org/) but before that the xpath of the fields must be specified:
Field | Xpath
:------------ | :------------- |
`Documents` | `//items/` 
`Content` | `//item/content` 
`Author` | `//item/author` 
`Publication Date` | `//item/published`

For more information check the [docs](https://voyant-tools.org/docs/#!/guide/corpuscreator-section-xml).

## Output
The output directory contains models mentioned above and additional files.
File | Description
:------------ | :-------------
`corpus` | The directory containing NER corpus (It will be deleted in the future).
`udpipe-data.csv` | All of the lemmatized tokens data.
`udpipe.csv` | The original texts with lemmatized words.
`udpipe.md5` | MD5 checksum of the input file. If the checksum matches the lemmatization is not done again.

## Docker
The [image](https://github.com/zabkwak/mat-analyzer/pkgs/container/mat-analyzer) is stored in GitHub packages registry and the app can be run in the docker environment.
```bash
docker pull ghcr.io/zabkwak/mat-analyzer:latest
```

```bash
docker run \
--name=mat-analyzer \
-e 'ANALYZER=BTM|LSI|Word2Vec|VT' \
-e 'INPUT_FILE=./input/tweets.csv' \
-e 'OUTPUT_DIR=./output' \
-e 'DATA_KEY=tweet_id' \
-e 'DOC_ID_KEY=tweet' \
-v '/absolute/path/to/output/dir:/usr/src/app/output' \
-v '/absolute/path/to/input/dir:/usr/src/app/input' \
ghcr.io/zabkwak/mat-analyzer:latest  
```
The volumes must be set for accessing input and output data.