class IndexContent:
    def __init__(self, preset_files_array, settings_obj):
        self.majorVersion = 1
        self.minorVersion = 0
        self.settings = settings_obj
        self.uniqueValues = {}
        self.presets = preset_files_array

        self.uniqueValues["firmware_version"] = self._get_unique_values(preset_files_array, "firmware_version")
        self.uniqueValues["category"] = self._get_unique_values(preset_files_array, "category")
        self.uniqueValues["author"] = self._get_unique_values(preset_files_array, "author")
        self.uniqueValues["keywords"] = self._get_unique_values(preset_files_array, "keywords")

    def _get_unique_values(self, preset_files_array, property_name):
        result = []
        result_lower_case = set()

        def add_value(value):
            value_lower_case = value.lower()
            if value_lower_case not in result_lower_case:
                result.append(value)
                result_lower_case.add(value_lower_case)

        for preset in preset_files_array:
            if hasattr(preset, property_name):
                prop_value = getattr(preset, property_name)
                if isinstance(prop_value, list):
                    for value in prop_value:
                        add_value(value)
                else:
                    add_value(prop_value)

        result.sort(key=lambda x: x.lower())
        return result
