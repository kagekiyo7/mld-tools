# -*- coding: utf-8 -*-

import os
import sys
from utils.mld import parse_mld
import argparse

def replace_ver_to_mfi3(mld_data: bytearray):
    vers_i = mld_data.find(b"vers")
    if (vers_i == -1):
        raise Exception("no vers")
    mld_data[vers_i+6:vers_i+6+4] = "0300".encode("ascii")
    return mld_data

def main(file_path):
    in_dir = os.path.dirname(file_path)
    out_dir = os.path.join(in_dir, "MFi3")
    os.makedirs(out_dir, exist_ok=True)
    with open(file_path, "rb") as file:
        mld_data = bytearray(file.read())
    try:
        parse_mld(mld_data)
    except:
        print("It's not a mld.")
        return
    out_data = replace_ver_to_mfi3(mld_data)
    with open(os.path.join(out_dir, os.path.basename(file_path)), "wb") as file:
        file.write(out_data)

if __name__ == "__main__":
    parser = argparse.ArgumentParser("replace_ver_to_MFi3")
    parser.add_argument("inputs", nargs="+")
    args = parser.parse_args()
    for file_path in args.inputs:
        main(file_path)