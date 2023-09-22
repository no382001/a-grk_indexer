hacked together bad python code to index digital ancient-greek dictionaries (i hate digital dictionaries, but you cant have everything)

### install
(this will take a while)

    pip install cltk pytesseract pdf2image

    apt install tesseract-ocr-grc

after, run this to get the CLTK ancient greek model (or just run `download_corpus.py`)

```python
from cltk.data.fetch import FetchCorpus

corpus_downloader = FetchCorpus(language="grc")
corpus_downloader.import_corpus("grc_models_cltk")
```

### use
- run `indexer.py`
- select a pdf
- select an area (or two) with L or RMouse (this is the only part of all the pages thats going to be OCR'd and tokenized by CLTK)
- press Tokenize
- ...