import collections

class MetadataTypes:
    STRING = "STRING"
    STRING_ARRAY = "STRING_ARRAY"
    PRESET_CATEGORY = "PRESET_CATEGORY"
    FILE_PATH = "FILE_PATH"
    BOOLEAN = "BOOLEAN"
    WORDS_ARRAY = "WORDS_ARRAY"
    FILE_PATH_ARRAY = "FILE_PATH_ARRAY"
    PRESET_STATUS = "PRESET_STATUS"
    PRIORITY = "PRIORITY"
    PARSER = "PARSER"

class PresetStatusEnum:
    OFFICIAL = "OFFICIAL"
    COMMUNITY = "COMMUNITY"
    EXPERIMENTAL = "EXPERIMENTAL"
    ALL = [OFFICIAL, COMMUNITY, EXPERIMENTAL]

class ParserEnum:
    TEXT = "TEXT"
    MARKED = "MARKED"
    ALL = [TEXT, MARKED]

class PresetCategories:
    TUNE = "TUNE"
    RATES = "RATES"
    OSD = "OSD"
    VTX = "VTX"
    LEDS = "LEDS"
    MODES = "MODES"
    FILTERS = "FILTERS"
    RC_LINK = "RC_LINK"
    BNF = "BNF"
    OTHER = "OTHER"

class PresetCategoriesPriorities:
    TUNE = 10**12
    RATES = 10**4
    OSD = 0
    VTX = 10**6
    LEDS = 0
    MODES = 0
    RC_SMOOTHING = 10**8
    FILTERS = 10**2
    RC_LINK = 10**10
    BNF = 0
    OTHER = 0

class OptionsDirectives:
    OPTION_DIRECTIVE = "option"
    BEGIN_OPTION_DIRECTIVE = "option begin"
    END_OPTION_DIRECTIVE = "option end"
    OPTION_CHECKED = "(checked)"
    OPTION_UNCHECKED = "(unchecked)"
    BEGIN_OPTION_GROUP_DIRECTIVE = "option_group begin"
    END_OPTION_GROUP_DIRECTIVE = "option_group end"
    EXCLUSIVE_OPTION_GROUP = "(exclusive)"

class Settings:
    MetapropertyDirective = "#$"

    PresetCategories = PresetCategories
    PresetCategoriesPriorities = PresetCategoriesPriorities

    MetadataTypes = MetadataTypes

    OptionsDirectives = OptionsDirectives

    PresetStatusEnum = PresetStatusEnum.ALL
    ParserEnum = ParserEnum.ALL

    presetsDir = "presets"
    presetsFileEncoding = "utf-8"

    presetsFileMetadata = collections.OrderedDict([
        ("title",                {"type": MetadataTypes.STRING,           "optional": False}),
        ("firmware_version",     {"type": MetadataTypes.STRING_ARRAY,     "optional": False}),
        ("category",             {"type": MetadataTypes.PRESET_CATEGORY,  "optional": False}),
        ("status",               {"type": MetadataTypes.PRESET_STATUS,    "optional": False}),
        ("author",               {"type": MetadataTypes.STRING,           "optional": True}),
        ("description",          {"type": MetadataTypes.STRING_ARRAY,     "optional": True}),
        ("include",              {"type": MetadataTypes.FILE_PATH_ARRAY,  "optional": True}),
        ("keywords",             {"type": MetadataTypes.WORDS_ARRAY,      "optional": True}),
        ("hidden",               {"type": MetadataTypes.BOOLEAN,          "optional": True}),
        ("discussion",           {"type": MetadataTypes.STRING,           "optional": True}),
        ("warning",              {"type": MetadataTypes.STRING,           "optional": True}),
        ("disclaimer",           {"type": MetadataTypes.STRING,           "optional": True}),
        ("include_warning",      {"type": MetadataTypes.FILE_PATH_ARRAY,  "optional": True}),
        ("include_disclaimer",   {"type": MetadataTypes.FILE_PATH_ARRAY,  "optional": True}),
        ("priority",             {"type": MetadataTypes.PRIORITY,         "optional": True}),
        ("force_options_review", {"type": MetadataTypes.BOOLEAN,          "optional": True}),
        ("parser",               {"type": MetadataTypes.PARSER,           "optional": True}),
    ])

settings = Settings()
