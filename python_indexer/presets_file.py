import os
import hashlib
from pathlib import Path
from .settings import Settings, MetadataTypes, PresetCategories, PresetStatusEnum, ParserEnum, OptionsDirectives

class PresetsFile:
    def __init__(self, full_path, settings_obj, errors):
        self.fullPath = Path(full_path)
        self.hash = ""
        self._presets_file_metadata = settings_obj.presetsFileMetadata
        self._errors = errors
        self._settings = settings_obj
        self.options = []
        self.option_groups = []
        self._current_option = None
        self._current_option_group = None

        try:
            binary_file_content = self.fullPath.read_bytes()
            self.hash = hashlib.sha256(binary_file_content).hexdigest()
        except FileNotFoundError:
            self._add_error(f"File not found: {self.fullPath}")
            return
        except Exception as e:
            self._add_error(f"Error reading file {self.fullPath}: {e}")
            return

        self._process_lines(binary_file_content, self._settings.presetsFileEncoding)
        self._check_properties()

        if not hasattr(self, 'priority') or self.priority is None:
            self.priority = getattr(self._settings.PresetCategoriesPriorities, self.category, 0)

        self._clear_properties()

    def _clear_properties(self):
        del self._presets_file_metadata
        del self._errors
        del self._settings
        del self._current_option
        del self._current_option_group

        properties_to_delete = [
            "options", "option_groups", "description", "include",
            "discussion", "warning", "disclaimer", "include_warning",
            "include_disclaimer", "parser"
        ]

        for prop in properties_to_delete:
            if hasattr(self, prop):
                # Only delete if the property is empty (or false for booleans)
                if not getattr(self, prop):
                    delattr(self, prop)

    def _check_properties(self):
        for property_name, value_meta in self._presets_file_metadata.items():
            if not value_meta["optional"]:
                if self._is_empty_property(getattr(self, property_name, None)):
                    self._add_error(f"missing or empty property '{property_name}'")

        if self._current_option is not None:
            self._add_error(f"Missing {self._settings.OptionsDirectives.END_OPTION_DIRECTIVE} for {self._current_option['name']}")

        if self._current_option_group is not None:
            self._add_error(f"Missing {self._settings.OptionsDirectives.END_OPTION_GROUP_DIRECTIVE} for {self._current_option_group['name']}")

    def _is_empty_property(self, property_value):
        return property_value is None or (isinstance(property_value, (str, list)) and len(property_value) == 0)

    def _process_lines(self, binary_file_content, presets_file_encoding):
        file_content = binary_file_content.decode(presets_file_encoding)
        lines = file_content.split('\n')

        self._current_line = 1

        for line in lines:
            line = line.strip()
            if line.startswith(self._settings.MetapropertyDirective):
                self._process_metaproperty_line(line)
            self._current_line += 1

        del self._current_line

    def _process_metaproperty_line(self, line):
        line = line[len(self._settings.MetapropertyDirective):].strip()
        low_case_line = line.lower()
        is_property = False
        is_property_missing_colon = False
        is_option_directive = False

        for property_name, value_meta in self._presets_file_metadata.items():
            line_beginning = f"{property_name.lower()}:"
            wrong_line_beginning = f"{property_name.lower()}"

            if low_case_line.startswith(line_beginning):
                line_value = line[len(line_beginning):].strip()
                self._process_property(property_name, line_value)
                is_property = True
                break
            elif low_case_line.startswith(wrong_line_beginning):
                is_property_missing_colon = True

        if not is_property and low_case_line.startswith(self._settings.OptionsDirectives.OPTION_DIRECTIVE):
            self._process_option_directive(line)
            is_option_directive = True

        if not is_property and not is_option_directive:
            if is_property_missing_colon:
                self._add_error(f"line {self._current_line}, property missing ':'")
            else:
                self._add_error(f"line {self._current_line}, unknown preset directive: '{line}'")

    def _process_option_directive(self, line):
        low_case_line = line.lower()

        if low_case_line.startswith(self._settings.OptionsDirectives.BEGIN_OPTION_DIRECTIVE):
            self._process_option_begin_directive(line, low_case_line)
        elif low_case_line.startswith(self._settings.OptionsDirectives.END_OPTION_DIRECTIVE):
            self._process_option_end_directive(line, low_case_line)
        elif low_case_line.startswith(self._settings.OptionsDirectives.BEGIN_OPTION_GROUP_DIRECTIVE):
            self._process_option_group_begin_directive(line, low_case_line)
        elif low_case_line.startswith(self._settings.OptionsDirectives.END_OPTION_GROUP_DIRECTIVE):
            self._process_option_group_end_directive(line, low_case_line)

    def _process_option_group_begin_directive(self, line, low_case_line):
        option_group = self._get_option_group(line)

        if not option_group["name"]:
            self._add_error(f"line {self._current_line}, empty optionGroup name")
        elif self._current_option_group is not None:
            self._add_error(f"line {self._current_line}, nested #$ option groups are not allowed")
        else:
            self._current_option_group = option_group

    def _process_option_group_end_directive(self, line, low_case_line):
        if self._current_option_group is None:
            self._add_error(f"line {self._current_line}, end Option Group directive found but no Option Group to close")
        else:
            low_case_option_group_name = self._current_option_group["name"].lower()

            found = False
            for item in self.option_groups:
                if low_case_option_group_name == item["name"].lower():
                    found = True
                    break

            if not found:
                self.option_groups.append(self._current_option_group)

            self._current_option_group = None

    def _process_option_begin_directive(self, line, low_case_line):
        option = self._get_option(line)

        if not option["name"]:
            self._add_error(f"line {self._current_line}, empty Option name")
        elif self._current_option is not None:
            self._add_error(f"line {self._current_line}, nested #$ options are not allowed")
        else:
            self._current_option = option

    def _process_option_end_directive(self, line, low_case_line):
        if self._current_option is None:
            self._add_error(f"line {self._current_line}, end Option directive found but no Option to close")
        else:
            low_case_option_name = self._current_option["name"].lower()

            found = False
            for item in self.options:
                if low_case_option_name == item["name"].lower():
                    found = True
                    break

            if not found:
                self.options.append(self._current_option)

            self._current_option = None

    def _escape_regex(self, string):
        import re
        return re.escape(string)

    def _get_option_group(self, line):
        directive_removed = line[len(self._settings.OptionsDirectives.BEGIN_OPTION_GROUP_DIRECTIVE):].strip()
        is_exclusive_group = self._is_exclusive_group(directive_removed.lower())

        import re
        exclusive_option_group_regex = re.compile(self._escape_regex(self._settings.OptionsDirectives.EXCLUSIVE_OPTION_GROUP), re.IGNORECASE)

        option_group_name = exclusive_option_group_regex.sub("", directive_removed).strip()

        if not option_group_name or option_group_name[0] != ":":
            self._add_error(f'line {self._current_line}, OPTION_GROUP BEGIN directive should be followed by ":". Example: #$ OPTION_GROUP BEGIN: My Group Name or if its exclusive: #$ OPTION_GROUP BEGIN: (EXCLUSIVE) My Exclusive Group')

        option_group = {
            "name": option_group_name[1:].strip(),
            "exclusive": is_exclusive_group,
        }

        return option_group

    def _is_exclusive_group(self, lowercase_line):
        return self._settings.OptionsDirectives.EXCLUSIVE_OPTION_GROUP.lower() in lowercase_line

    def _get_option(self, line):
        directive_removed = line[len(self._settings.OptionsDirectives.BEGIN_OPTION_DIRECTIVE):].strip()
        directive_removed_low_case = directive_removed.lower()
        option_checked = self._is_option_checked(directive_removed_low_case)

        import re
        reg_exp_remove_checked = re.compile(self._escape_regex(self._settings.OptionsDirectives.OPTION_CHECKED), re.IGNORECASE)
        reg_exp_remove_unchecked = re.compile(self._escape_regex(self._settings.OptionsDirectives.OPTION_UNCHECKED), re.IGNORECASE)

        option_name = reg_exp_remove_checked.sub("", directive_removed)
        option_name = reg_exp_remove_unchecked.sub("", option_name).strip()

        if not option_name or option_name[0] != ":":
            self._add_error(f'line {self._current_line}, OPTION BEGIN directive should be followed by ":". Example: #$ OPTION BEGIN (UNCHECKED): My Option Name')

        option = {
            "name": option_name[1:].strip(),
            "checked": option_checked
        }

        return option

    def _is_option_checked(self, low_case_line):
        option_checked = False
        option_unchecked = False

        if self._settings.OptionsDirectives.OPTION_CHECKED.lower() in low_case_line:
            option_checked = True
        if self._settings.OptionsDirectives.OPTION_UNCHECKED.lower() in low_case_line:
            option_unchecked = True

        if option_checked and option_unchecked:
            self._add_error(f"line {self._current_line}, Option can't be checked and unchecked at the same time")
        elif not option_checked and not option_unchecked:
            self._add_error(f"line {self._current_line}, Every option must specify whether it is {self._settings.OptionsDirectives.OPTION_CHECKED.upper()} or {self._settings.OptionsDirectives.OPTION_UNCHECKED.upper()}")
        else:
            return option_checked # Return the actual boolean value

        return option_checked

    def _process_property(self, property_name, line):
        property_type = self._presets_file_metadata[property_name]["type"]
        if property_type == MetadataTypes.STRING_ARRAY:
            self._process_array_property(property_name, line)
        elif property_type == MetadataTypes.STRING:
            self._process_string_property(property_name, line)
        elif property_type == MetadataTypes.PRESET_CATEGORY:
            self._process_preset_category_property(property_name, line)
        elif property_type == MetadataTypes.FILE_PATH:
            self._process_file_path_property(property_name, line)
        elif property_type == MetadataTypes.FILE_PATH_ARRAY:
            self._process_file_path_array_property(property_name, line)
        elif property_type == MetadataTypes.BOOLEAN:
            self._process_boolean_property(property_name, line)
        elif property_type == MetadataTypes.WORDS_ARRAY:
            self._process_words_array_property(property_name, line)
        elif property_type == MetadataTypes.PRESET_STATUS:
            self._process_preset_status_property(property_name, line)
        elif property_type == MetadataTypes.PRIORITY:
            self._process_priority_property(property_name, line)
        elif property_type == MetadataTypes.PARSER:
            self._process_parser_property(property_name, line)
        else:
            self._add_error(f"line {self._current_line}, unknown property type '{property_type}' for the property '{property_name}'")

    def _process_preset_status_property(self, property_name, line):
        self._check_property_duplicated(property_name)

        if line in self._settings.PresetStatusEnum:
            setattr(self, property_name, line)
        else:
            self._add_error(f"line {self._current_line}, unknown {property_name} value: '{line}'; available values: {', '.join(self._settings.PresetStatusEnum)}")

    def _process_parser_property(self, property_name, line):
        self._check_property_duplicated(property_name)

        if line in self._settings.ParserEnum:
            setattr(self, property_name, line)
        else:
            self._add_error(f"line {self._current_line}, unknown {property_name} value: '{line}'; available values: {', '.join(self._settings.ParserEnum)}")

    def _process_words_array_property(self, property_name, line):
        self._check_property_duplicated(property_name)

        words = [word.strip() for word in line.split(",") if word.strip()]
        setattr(self, property_name, words)

    def _process_boolean_property(self, property_name, line):
        self._check_property_duplicated(property_name)

        true_values = ["true", "yes"]
        false_values = ["false", "no"]

        line_low_case = line.lower()

        result = False

        if line_low_case in true_values:
            result = True
        elif line_low_case in false_values:
            result = False
        else:
            self._add_error(f"line {self._current_line}, boolean property '{property_name}' has a wrong value: '{line}'")

        setattr(self, property_name, result)

    def _check_property_duplicated(self, property_name):
        if hasattr(self, property_name) and getattr(self, property_name) is not None:
            self._add_error(f"line {self._current_line}, duplicated property '{property_name}'")

    def _process_file_path_property(self, property_name, line):
        self._check_property_duplicated(property_name)
        file_path = Path(line)
        if not file_path.is_file():
            self._add_error(f"line {self._current_line}, can't find file '{line}'")
        else:
            setattr(self, property_name, line)

    def _process_file_path_array_property(self, property_name, line):
        if not hasattr(self, property_name) or getattr(self, property_name) is None:
            setattr(self, property_name, [])

        file_path = Path(line)
        if file_path.is_file():
            getattr(self, property_name).append(line)
        else:
            self._add_error(f"line {self._current_line}, can't find file '{line}' or it's a directory")

    def _process_preset_category_property(self, property_name, line):
        self._check_property_duplicated(property_name)
        line_low_case = line.lower()
        preset_type_valid = False

        for key in PresetCategories.__dict__:
            if not key.startswith('__') and key.lower() == line_low_case:
                preset_type_valid = True
                setattr(self, property_name, getattr(PresetCategories, key))
                break

        if not preset_type_valid:
            self._add_error(f"line {self._current_line}, unknown preset category: '{line}'")

    def _process_array_property(self, property_name, line):
        if not hasattr(self, property_name) or getattr(self, property_name) is None:
            setattr(self, property_name, [])
        getattr(self, property_name).append(line)

    def _process_string_property(self, property_name, line):
        self._check_property_duplicated(property_name)
        setattr(self, property_name, line)

    def _process_priority_property(self, property_name, line):
        self._check_property_duplicated(property_name)
        try:
            value = int(line)
            setattr(self, property_name, value)
        except ValueError:
            self._add_error(f"line {self._current_line}, PRIORITY value must be an integer. Instead it is: '{line}'")

    def _add_error(self, error):
        full_error = f"{self.fullPath}: {error}"
        self._errors.append(full_error)
        print(full_error)