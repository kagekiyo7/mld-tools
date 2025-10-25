# mld-tools
MFi format (.mld) tools
- extract_mld.py: Extract mld files accurately based on metadata of file size and filename from binary data.
- get_mld_metadata.py: Print metadata of mld file.

## extract_mld.py
```usage: MLD extractor [-h] [-o OUT_DIR] [-r | --rename | --no-rename] [-s | --sequential | --no-sequential]
                     [-c | --check-mld-structure | --no-check-mld-structure]
                     [-d | --remove-duplicates | --no-remove-duplicates]
                     inputs [inputs ...]

positional arguments:
  inputs                Files (multiple possible) or a folder (one)

options:
  -h, --help            show this help message and exit
  -o, --out_dir OUT_DIR
                        When omitted, the output folder is created in the same folder as the first input file.
  -r, --rename, --no-rename
                        Overwrite the filename with the song title information found within the MLD. (Default: True)
  -s, --sequential, --no-sequential
                        Assign sequential numbers to filenames. (Default: False)
  -c, --check-mld-structure, --no-check-mld-structure
                        Not only does it carve the file size written in the header, but it also checks whether the MLD
                        structure is valid. (Default: True)
  -d, --remove-duplicates, --no-remove-duplicates
                        Use a hash (SHA-256) to remove duplicate files from the output. (Default: True)```