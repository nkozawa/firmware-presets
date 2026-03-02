import sys
import json
import hashlib
from pathlib import Path

from .presets_folder import PresetsFolder
from .settings import Settings
from .index_content import IndexContent

errors = []
sys.exitcode = 100 # Default exit code for failure

write_index_file = True

if len(sys.argv) == 2:
    if sys.argv[1] == "nosave":
        write_index_file = False

preset_files_array = []
settings = Settings()

# Ensure the presets directory exists before trying to scan it
presets_dir_path = Path(settings.presetsDir)
if not presets_dir_path.is_dir():
    errors.append(f"Presets directory '{settings.presetsDir}' not found.")
else:
    presets_folder = PresetsFolder(settings.presetsDir, settings, preset_files_array, errors)
    PresetsFolder.check_for_include_loops(preset_files_array, errors)

def settings_to_dict(settings_class):
    # Helper to convert class attributes to dict
    def class_to_dict(cls):
        return {k: v for k, v in cls.__dict__.items() if not k.startswith('__')}

    return {
        "MetapropertyDirective": settings_class.MetapropertyDirective,
        "PresetCategories": class_to_dict(settings_class.PresetCategories),
        "PresetCategoriesPriorities": class_to_dict(settings_class.PresetCategoriesPriorities),
        "MetadataTypes": class_to_dict(settings_class.MetadataTypes),
        "OptionsDirectives": class_to_dict(settings_class.OptionsDirectives),
        "PresetStatusEnum": settings_class.PresetStatusEnum,
        "ParserEnum": settings_class.ParserEnum,
        "presetsDir": settings_class.presetsDir,
        "presetsFileEncoding": settings_class.presetsFileEncoding,
        "presetsFileMetadata": settings_class.presetsFileMetadata
    }

def json_default(o):
    if isinstance(o, Settings):
        return settings_to_dict(o.__class__)
    if isinstance(o, Path):
        return str(o)
    return o.__dict__

if not errors:
    print("OK")

    if write_index_file:
        index_content = IndexContent(preset_files_array, settings)
        json_index_content = json.dumps(index_content, default=json_default, indent=2)
        
        # Ensure the output directory exists
        output_dir = Path("./") # Assuming index.json is written to the current directory
        output_dir.mkdir(parents=True, exist_ok=True)

        index_json_path = output_dir / "index.json"
        index_json_path.write_text(json_index_content, encoding="utf-8")
        print("index.json created")

        sum_hash = hashlib.sha256()
        sum_hash.update(json_index_content.encode("utf-8"))
        index_hash = sum_hash.hexdigest()
        
        index_hash_path = output_dir / "index_hash.txt"
        index_hash_path.write_text(index_hash, encoding="utf-8")
        print("index_hash.txt created")

    sys.exitcode = 0
else:
    print("Failed with errors")
    for error in errors:
        print(error)
    sys.exitcode = 1
