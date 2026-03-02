import os
from pathlib import Path
from .presets_file import PresetsFile

class PresetsFolder:
    def __init__(self, full_path, settings_obj, preset_files_array, errors):
        self.sub_folders = []
        self.files = []
        self.fullPath = Path(full_path)
        self.name = ""

        try:
            list_dir = os.listdir(self.fullPath)
        except FileNotFoundError:
            # This can happen if the presetsDir in settings is not found
            # The error will be caught by the main indexer.py
            return

        for file_name in list_dir:
            full_file_name = self.fullPath / file_name
            if not file_name.startswith("."):
                if full_file_name.is_dir():
                    subdir = PresetsFolder(full_file_name, settings_obj, preset_files_array, errors)
                    subdir.name = file_name
                    self.sub_folders.append(subdir)
                elif full_file_name.is_file() and file_name.lower().endswith(".txt"):
                    presets_file = PresetsFile(full_file_name, settings_obj, errors)
                    preset_files_array.append(presets_file)
                    self.files.append(presets_file)

    @staticmethod
    def check_for_include_loops(preset_files_array, errors):
        files_db = PresetsFolder._create_files_dictionary(preset_files_array)
        file_name_errors = {}

        for file in preset_files_array:
            parents = []
            PresetsFolder._check_file_for_include_loops(file, files_db, parents, file_name_errors)

        for file_name_error in file_name_errors:
            error_text = f"File {file_name_error}, takes part in the #$ INCLUDE loop'"
            errors.append(error_text)
            print(error_text)

    @staticmethod
    def _check_file_for_include_loops(file, files_db, parents, file_name_errors):
        if file.fullPath in parents:
            file_name_errors[file.fullPath] = True
        else:
            parents.append(file.fullPath)
            if hasattr(file, "include") and file.include:
                for included_file_name in file.include:
                    cloned_parents = list(parents) # Create a shallow copy
                    if included_file_name in files_db:
                        PresetsFolder._check_file_for_include_loops(files_db[included_file_name], files_db, cloned_parents, file_name_errors)
                    else:
                        # This error should ideally be caught during PresetsFile parsing
                        # but adding a safeguard here.
                        file._add_error(f"Included file '{included_file_name}' not found in the index.")


    @staticmethod
    def _create_files_dictionary(preset_files_array):
        result = {}
        for file in preset_files_array:
            result[file.fullPath] = file
        return result
