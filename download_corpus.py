from cltk.data.fetch import FetchCorpus

corpus_downloader = FetchCorpus(language="grc")
corpus_downloader.import_corpus("grc_models_cltk")