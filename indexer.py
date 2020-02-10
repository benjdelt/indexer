""" Creates an index of all the files contained in the path's folder and subfolders.

The module creates an list of dicts representing all the files in the folder and subfolders
of the path provided. That index can then be filtered and dumped in a csv file.

Typical usage:

index = Indexer("../")
index.create_index()
duplicates = index.filter_duplicates()
index.write_to_file(duplicates, "duplicates")
"""

import os
import json
import re
import csv
from time import ctime

class Indexer:
    """ Creates an index of all the files contained in the provided path's folder and subfolders.

    Attributes:
        path (str): represents the absolute or relative path of the folder to index.
        files (list): list of dicts representing the indexed files. Filled by the create_index method.
        types (dict): represents the type of files according to their extension. Loaded from a json file by default.

    Public Methods:
        create_index: Creates dict for each file contained in the path attribute's folder and subfolders.
        filter_duplicates: Filters a list of dicts representing files to only keep files that have the same name and 
            size.
        filter_by_min_size: Filters a list of dict representing files to keep files that are at least as big as the 
            provided argument.
        write_to_file: Creates or overwrite a csv file representing all the files.
    """


    def __init__(self, path):
        """Inits the Indexer class with path, files and types atrtibutes."""
        self.path = path
        self.files = []

        with open("./types.json", "r") as types_file:
            self.types = json.loads(types_file.read())

    def __is_exception(self, path_function, file_path, dirpath):
        """Returns True if the os.path function passed raises an exception."""
        try:
            path_function(dirpath, file_path) if dirpath else path_function(file_path)
            return False
        except Exception as exception:
            print("Parsing File Error:", exception)
            return True

    def __get_file_info_str(self, path_function, file_path, dirpath=""):
        """Returns a default value if the path function raised an exception or the value returned 
           by that function"""
        if self.__is_exception(path_function, file_path, dirpath):
            return "Parsing Error"
        return path_function(dirpath, file_path) if dirpath else path_function(file_path) 

    def __get_file_info_int(self, path_function, file_path, dirpath=""):
        """Returns a default value if the path function raised an exception or the value returned 
           by that function"""
        if self.__is_exception(path_function, file_path, dirpath):
            return 0
        return path_function(dirpath, file_path) if dirpath else path_function(file_path) 

    def __get_type(self, file_extension, types=None):
        """Returns a string representing the type of a file based on its extension."""
        if types is None:
            types = self.types
        file_type = "other"
        for key in types:
            if file_extension in types[key]:
                file_type = key
        return file_type

    def create_index(self):
        """Creates dict for each file contained in the path attribute's folder and subfolders.

        Returns:
            list: a list of dicts representing each file.             
        """
        print("Creating index...")
        for dirpath, _, filenames in os.walk(self.path):
            for filename in filenames:
                file_path = self.__get_file_info_str(os.path.join, filename, dirpath)
                self.files.append({
                    "Absolute Path": self.__get_file_info_str(os.path.abspath, file_path),
                    "File Name": self.__get_file_info_str(os.path.basename, file_path),
                    "File Size": self.__get_file_info_int(os.path.getsize, file_path),
                    "Last Access":  self.__get_file_info_int(os.path.getatime, file_path),
                    "Creation": self.__get_file_info_int(os.path.getctime, file_path),
                    "File Extension": self.__get_file_info_str(os.path.splitext, file_path)[1].lower(),
                    "File Type": self.__get_type(self.__get_file_info_str(os.path.splitext, file_path)[1].lower())
                })
        print("Index created.")
        return self.files

    def filter_duplicates(self, files=None):
        """Filters a list of dicts representing files to only keep files that have the same name and size.
        
        Args:
            files (list): optional, a list of fict representing files, defaults to the files attribute.
        Returns:
            list: a list of dicts representing the filtered files.
        """
        if files is None:
            files = self.files
        print("Filtering duplicates...")
        duplicates = {}
        for file_name in files:
            if file_name["File Name"] in duplicates:
                if duplicates[file_name["File Name"]]["File Size"] == file_name["File Size"]:
                    duplicates[file_name["File Name"]]["count"] += 1
            else:
                duplicates[file_name["File Name"]] = {
                    "count": 1,
                    "File Size": file_name["File Size"]
                }
        filtered_file_names = [f for f in duplicates if duplicates[f]["count"] > 1]
        filtered_files = [f for f in self.files if f["File Name"] in filtered_file_names]
        print("Duplicates filtered.")
        return filtered_files

    def __parse_size(self, size):
        """Turns a string representing the size of a file into an integer of the size of the file.
           The function assumes that each size is 1024 times bigger than the previous one. 
        
        Args:
            size (str): a string representing a size in B, KB, MB, GB or TB (e.g.: 123 KB).
        Returns:
            int: the size of the file in Bytes
        Raises:
            ValueError: Invalid argument string for the size.
        """
        valid = re.search(r"^\d+\.*\d*\s*[KMGT]*B$", size.upper())
        if valid is None:
            raise ValueError("Invalid argument string")
        valid_str = valid.group(0)
        value = float(re.search(r"^\d+\.*\d*", valid_str).group(0))
        unit = re.search(r"[KMGT]*B$", valid_str).group(0)
        exponent = {"B": 0, "KB": 10, "MB": 20, "GB": 30, "TB": 40}
        return value * 2** exponent[unit]

    def filter_by_min_size(self, min_size, files=None):
        """Filters a list of dict representing files to keep files that are at least as big as the 
           provided argument.

        Args:
            min_size (str): represents the minimum size of files to keep in B, KB, MB, GB, or TB 
                (e.g.: 123 KB).
            files (list): optional, a list of fict representing files, defaults to the files attribute.
        Returns:
            list: a list of dicts representing the filtered files.
        """
        value = self.__parse_size(min_size)
        if files is None:
            files = self.files
        print("Filtering by minimum size...")
        filtered_files = [f for f in files if f["File Size"] >= value]
        print("Filtering by minimum size complete.")
        return filtered_files

    def write_to_file(self, files=None, file_name=None):
        """ Creates or overwrite a csv file representing all the files.

        Args:
            files (list): optional, a list of fict representing files, defaults to the files attribute.
            file_name (str): optional, the name of the output file, defaults to 'index'. 
        """
        if files is None:
            files = self.files
        if file_name is None:
            file_name = "index"
        with open(f"{file_name}.csv", "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = ["Absolute Path", "File Name", "File Size", "Last Access", "Creation", "File Extension", "File Type"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for file_name in files:
                print("Writing:", file_name["File Name"])
                writer.writerow(file_name)
        print("Done writing.")
