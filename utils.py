from pathlib import Path

def get_files_with_extensions(source, extensions):
    return [f for f in Path(source).iterdir() if f.suffix.lower() in extensions]