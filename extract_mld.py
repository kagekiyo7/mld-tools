# -*- coding: utf-8 -*-

import os
import sys
import get_mld_metadata

def extract_mld(binary: bytes):
    ret = []
    file_i = 0
    magic = "melo".encode()
    while True:
        mld_dict = {}
        file_i = binary.find(magic, file_i)
        if (file_i == -1):
            break
        size = int.from_bytes(binary[file_i+4:file_i+8]) + 8
        mld_binary = binary[file_i:file_i+size]
        mld_dict["binary"] = mld_binary
        mld_dict["title"] = get_mld_metadata.get_metadata(mld_binary).get("title", None)
        file_i += 1
        ret.append(mld_dict)
    return ret

def main(file_path):
    file_name = os.path.splitext(os.path.basename(file_path))[0]
    dir_name = os.path.dirname(file_path)
    with open(file_path, "rb") as f:
        target_binary = f.read()
    mlds = extract_mld(target_binary)

    def output(files, ext):
        i = 0
        for file_dict in files:
            if title := file_dict.get("title", False):
                output_path = os.path.join(dir_name, f"{str(i).zfill(2)} {title}.{ext}")
                with open(output_path, "wb") as f:
                    f.write(file_dict["binary"])
                    print(f"{os.path.basename(output_path)}: done!")
            else:
                output_path = os.path.join(dir_name, f"{file_name}_{i}.{ext}")
                with open(output_path, "wb") as f:
                    f.write(file_dict["binary"])
                    print(f"{os.path.basename(output_path)}: done!")
            i += 1
    output(mlds, ext="mld")

if __name__ == "__main__":
    for file_path in sys.argv[1:]:
        main(file_path)