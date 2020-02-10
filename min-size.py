from indexer import Indexer

index = Indexer("../TMP/")
index.create_index()
min_size_files = index.filter_by_min_size("200 KB")
index.write_to_file(min_size_files, "min-size")
