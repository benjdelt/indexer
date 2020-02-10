# Indexer

Creates an index of all the files contained in the path's folder and subfolders.

---

The module creates an list of dicts representing all the files in the folder and subfolders
of the path provided. That index can then be filtered and dumped in a csv file.

## Typical usage:

index = Indexer("../")
index.create_index()
duplicates = index.filter_duplicates()
index.write_to_file(duplicates, "duplicates")
