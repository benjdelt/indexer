from indexer import Indexer

index = Indexer("../TMP/")
index.create_index()
duplicates = index.filter_duplicates()
index.write_to_file(duplicates, "duplicates")
