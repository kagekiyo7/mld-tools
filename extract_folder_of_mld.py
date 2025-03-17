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
    magic = b"melo"
    file_i = -1
    
    while True:
        mld_dict = {}
        file_i = binary.find(magic, file_i+1)
        if file_i == -1:
            break

        size = int.from_bytes(binary[file_i+4:file_i+8]) + 8
            
        mld_binary = binary[file_i:file_i+size]
        
        if not get_mld_metadata.is_valid_mld(mld_binary):
            continue
        
        mld_dict["binary"] = mld_binary
        mld_dict["title"] = get_mld_metadata.get_metadata(mld_binary).get("title", "")
        mld_dict["offset"] = file_i
        
        ret.append(mld_dict)
    return ret

def get_file_hash(file_path: str) -> str:
    with open(file_path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

def process_file(file_path: str, output_dir: str, delete: bool, existing_files: Dict[str, str]) -> None:
    file_name = os.path.splitext(os.path.basename(file_path))[0]
    
    with open(file_path, "rb") as f:
        target_binary = f.read()
    
    print(f"\nInput: {file_path}")
    mld_dicts = extract_mld(target_binary)
    
    if not mld_dicts:
        print(f"Failed: There is no MLD.")
        return

    def output(mld_dicts, ext):
        for mld_dict in mld_dicts:
            filename = re.sub(r'[\\/:*?"<>|\t]+', "", mld_dict['title'])
            output_path = os.path.join(output_dir, f"{filename}.{ext}")
            
            i = 1
            while os.path.isfile(output_path):
                output_path = os.path.join(output_dir, f"{filename} ({i}).{ext}")
                i += 1
            
            # Check for duplicates
            file_hash = hashlib.md5(mld_dict["binary"]).hexdigest()
            if file_hash in existing_files:
                print(f"""Failed: The md5 matches that of file '{os.path.basename(existing_files[file_hash])}' (offset: {hex(mld_dict['offset'])})""")
                continue
            
            with open(output_path, "wb") as f:
                f.write(mld_dict["binary"])
                print(f"""Succeed: {os.path.basename(output_path)} (songname: '{mld_dict['title']}', offset: {hex(mld_dict['offset'])})""")
            
            existing_files[file_hash] = output_path

    output(mld_dicts, ext="mld")

    if delete:
        os.remove(file_path)
        print(f"Deleted original file: {file_path}")
    

def main():
    parser = argparse.ArgumentParser(description="Extract MLD files from a directory.")
    parser.add_argument("input_dir", help="Directory containing MLD files")
    parser.add_argument("-d", "--delete", action="store_true", help="Delete original files after processing")
    args = parser.parse_args()

    input_dir = args.input_dir
    output_dir = os.path.join(os.path.dirname(input_dir), "output_mld")
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
    
    print(f"\noutput => {output_dir}")

if __name__ == "__main__":
    main()
