from indexer import Indexer

# Instantiate Indexer wit path

index = Indexer("../TMP/")

# Create Index

# index.create_index()

# Create Index with filters

index.create_index(duplicates=True, max_size="315 KB")

# Filter By Duplicates

# duplicates = index.filter_duplicates()

# Write to file

index.write_to_file()
