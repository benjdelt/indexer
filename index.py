from indexer import Indexer

index = Indexer("../TMP/")
index.create_index()
index.write_to_file()
