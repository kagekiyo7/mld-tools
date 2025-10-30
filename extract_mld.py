# -*- coding: utf-8 -*-
import os
import sys
from utils.mld import parse_mld
import re
import argparse
import hashlib

def main(inputs, out_dir, enable_rename=True, enable_sequential=False, check_mld_structure=True, remove_duplicates=True):
    extracting_mld_dicts = []

    if os.path.isdir(inputs[0]):
        for root, dirs, files in os.walk(inputs[0]):
            for file in files:
                extracting_mld_dicts += detect_mld(os.path.join(root, file), check_mld_structure)
    else:
        for file_path in inputs:
            extracting_mld_dicts += detect_mld(file_path, check_mld_structure)

    if len(extracting_mld_dicts) == 0:
        print(f"No MLD was detected.")
        return
    
    if remove_duplicates:
        extracting_mld_dicts = remove_duplicates_mld(extracting_mld_dicts)

    save_mld_files(extracting_mld_dicts, out_dir, enable_rename, enable_sequential)
    print(f"\n=> {out_dir}")


def remove_duplicates_mld(extracting_mld_dicts):
    ret = []
    hash_set = set()
    for extracting_mld_dict in extracting_mld_dicts:
        if extracting_mld_dict["sha256"] not in hash_set:
            ret.append(extracting_mld_dict)
            hash_set.add(extracting_mld_dict["sha256"])

    return ret


def get_file_hash(target_data, algo="sha256"): 
    hash_func = hashlib.new(algo)
    hash_func.update(target_data)
    return hash_func.hexdigest()


def detect_mld(file_path, check_mld_structure):
    print(f"\n[{os.path.basename(file_path)}]")

    with open(file_path, "rb") as f:
        target = f.read()
    
    ret = []
    offset = -1

    while (offset := target.find(b"melo", offset + 1)) != -1:
        extracting_dict = {}
        print(f"\nFound: {hex(offset)}") 
        size = int.from_bytes(target[offset + 4 : offset + 8], "big") + 8
        end = min(offset+size, len(target))

        candidate_mld_data = target[offset : end]
        if check_mld_structure:
            try:
                mld_info = parse_mld(candidate_mld_data)
                temp = "" if mld_info["titl"] is None else mld_info["titl"].decode("cp932", errors="ignore")
                extracting_dict["title"] = "NO NAME" if temp in ["", " "] else temp
            except Exception as e:
                print("Skiped because MLD parsing failed.", f"({e})")
                continue
        else:
            try:
                if (title_off := candidate_mld_data.find(b"titl")) == -1:
                    raise Exception()
                else:
                    namesize = int.from_bytes(candidate_mld_data[title_off + 4 : title_off + 6], "big")
                    extracting_dict["title"] = candidate_mld_data[title_off + 6 : title_off + 6 + namesize].decode("cp932")
            except:
                extracting_dict["title"] = "NO NAME"

        extracting_dict["binary"] = candidate_mld_data
        extracting_dict["sha256"] = get_file_hash(candidate_mld_data)
        extracting_dict["file_name"] = os.path.splitext(os.path.basename(file_path))[0]
        ret.append(extracting_dict)
        print(f"""Succeeded: '{extracting_dict['title']}'""")
    return ret


def save_mld_files(extracting_mld_dicts, out_dir, enable_rename, enable_sequential):
    digits_num = len(str(len(extracting_mld_dicts)))

    for i, extracting_mld_dict in enumerate(extracting_mld_dicts):
        file_num = str(i + 1)
        file_num = file_num.zfill(digits_num)

        if enable_rename:
            # Remove characters that cannot be used in songnames.
            songname = re.sub(r'[\\/:*?"<>|\t\r\n]+', "", extracting_mld_dict['title'])
        else:
            songname = extracting_mld_dict["file_name"]

        filename = f"{file_num} {songname}.mld" if enable_sequential else f"{songname}.mld"
        output_path = os.path.join(out_dir, filename)

        j = 1
        while True:
            if not os.path.isfile(output_path):
                break
            filename = f"{file_num} {songname}.mld" if enable_sequential else f"{songname}.mld"
            output_path = os.path.join(out_dir, f"{songname} ({j}).mld")
            j += 1

        with open(output_path, "wb") as f:
            f.write(extracting_mld_dict["binary"])

    
if __name__ == "__main__":
    parser = argparse.ArgumentParser("MLD extractor")
    parser.add_argument("inputs", nargs="+", help="Files (multiple possible) or a folder (one)")
    parser.add_argument(
        "-o",
        "--out_dir",
        default=None,
        help="When omitted, the output folder is created in the same folder as the first input file.",
    )
    parser.add_argument(
        "-r",
        "--rename",
        default=True,
        help="Overwrite the filename with the song title information found within the MLD. (Default: True)",
        action=argparse.BooleanOptionalAction,
    )
    parser.add_argument(
        "-s",
        "--sequential",
        help="Assign sequential numbers to filenames. (Default: False)",
        action=argparse.BooleanOptionalAction,
    )
    parser.add_argument(
        "-c",
        "--check-mld-structure",
        default=True,
        help="Not only does it carve the file size written in the header, but it also checks whether the MLD structure is valid. (Default: True)",
        action=argparse.BooleanOptionalAction,
    )
    parser.add_argument(
        "-d",
        "--remove-duplicates",
        default=True,
        help="Use a hash (SHA-256) to remove duplicate files from the output. (Default: True)",
        action=argparse.BooleanOptionalAction,
    )
    args = parser.parse_args()

    out_dir = args.out_dir or os.path.join(
        os.path.dirname(args.inputs[0]),
        "MLD_files",
    )
    os.makedirs(out_dir, exist_ok=True)

    main(args.inputs, out_dir, args.rename, args.sequential, args.check_mld_structure, args.remove_duplicates)
