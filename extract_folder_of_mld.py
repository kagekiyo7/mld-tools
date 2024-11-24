# -*- coding: utf-8 -*-

import os
import sys
import get_mld_metadata
import re
import argparse
import hashlib
from typing import List, Dict

def extract_mld(binary: bytes) -> List[Dict]:
    ret = []
    file_i = 0
    magic = b"melo"
    while True:
        mld_dict = {}
        file_i = binary.find(magic, file_i)
        if file_i == -1:
            break
        print(f"magic: {hex(file_i)}")
        size = int.from_bytes(binary[file_i+4:file_i+8]) + 8
        if size > (3 * 1000 * 1000):
            file_i += 1
            continue
        mld_binary = binary[file_i:file_i+size]
        if not get_mld_metadata.is_valid_mld(mld_binary):
            file_i += 1
            continue
        mld_dict["binary"] = mld_binary
        mld_dict["title"] = get_mld_metadata.get_metadata(mld_binary).get("title", "")
        file_i += 1
        ret.append(mld_dict)
    return ret

def get_file_hash(file_path: str) -> str:
    with open(file_path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

def process_file(file_path: str, output_dir: str, delete: bool, existing_files: Dict[str, str]) -> None:
    file_name = os.path.splitext(os.path.basename(file_path))[0]
    with open(file_path, "rb") as f:
        target_binary = f.read()
    mlds = extract_mld(target_binary)
    if not mlds:
        print(f"{os.path.basename(file_path)}: There is no mld.")
        return

    def output(files, ext):
        dig = len(str(len(files)))
        for i, file_dict in enumerate(files):
            num = str(i + 1)
            num = num.zfill(dig) if dig > 2 else num.zfill(2)
            filename = re.sub(r'[\\/:*?"<>|]+', "", file_dict['title'])
            output_path = os.path.join(output_dir, f"{num} {filename}.{ext}")
            
            # Check for duplicates
            file_hash = hashlib.md5(file_dict["binary"]).hexdigest()
            if file_hash in existing_files:
                print(f"Duplicate file found: {output_path}")
                print(f"Matches existing file: {existing_files[file_hash]}")
                continue
            
            if os.path.isfile(output_path):
                output_path = os.path.join(output_dir, f"{num} {filename}_.{ext}")
            
            with open(output_path, "wb") as f:
                f.write(file_dict["binary"])
                print(f"{os.path.basename(output_path)}: done!")
            
            existing_files[file_hash] = output_path

    output(mlds, ext="mld")

    if delete:
        os.remove(file_path)
        print(f"Deleted original file: {file_path}")

def main():
    parser = argparse.ArgumentParser(description="Extract MLD files from a directory.")
    parser.add_argument("input_dir", help="Directory containing MLD files")
    parser.add_argument("-d", "--delete", action="store_true", help="Delete original files after processing")
    args = parser.parse_args()

    input_dir = args.input_dir
    output_dir = input_dir
    delete = args.delete

    if not os.path.isdir(input_dir):
        print(f"Error: {input_dir} is not a valid directory.")
        sys.exit(1)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    existing_files = {}

    for root, _, files in os.walk(input_dir):
        for file in files:
            file_path = os.path.join(root, file)
            process_file(file_path, output_dir, delete, existing_files)   

if __name__ == "__main__":
    main()