# -*- coding: utf-8 -*-

import os
import sys
import get_mld_metadata

def replace_ver_to_mfi3(mld: bytearray):
    vers_i = mld.find("vers".encode())
    if (vers_i == -1):
        raise Exception("no vers")
    mld[vers_i+6:vers_i+6+4] = "0300".encode()
    return mld

def main(file_path):
    in_dir = os.path.dirname(file_path)
    out_dir = os.path.join(in_dir, "MFi3")
    os.makedirs(out_dir, exist_ok=True)
    with open(file_path, "rb") as file:
        mld_binary = bytearray(file.read())
    if not get_mld_metadata.is_valid_mld(mld_binary):
        print("It's not a mld.")
        return
    out_binary = replace_ver_to_mfi3(mld_binary)
    with open(os.path.join(out_dir, os.path.basename(file_path)), "wb") as file:
        file.write(out_binary)


if __name__ == "__main__":
    for file_path in sys.argv[1:]:
        main(file_path)