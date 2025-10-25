# -*- coding: utf-8 -*-

import os
import sys
import datetime
from utils.mld import parse_mld

def to_bin(bytes) -> str:
    bin_list = list()
    for byte in bytes:
        bin_list.append(format(byte, '08b'))

    return ''.join(map(str, bin_list))


def main(file_path):
    with open(file_path, "rb") as file:
        mld_data = file.read()

    mld_chunks = parse_mld(mld_data)
    
    # format document
    # https://www.awm.jp/~yoya/cache/homepage2.nifty.com/cstation/mfi_1.html

    if mld_chunks.get("titl"):
        print("title:", mld_chunks["titl"].decode("cp932", "ignore"))

    match mld_chunks["data_type_major"]:
        case 1:
            print(f"data_type_major: {mld_chunks['data_type_major']} (ringtone)")
        case 2:
            print(f"data_type_major: {mld_chunks['data_type_major']} (music)")
        case _:
            print(f"data_type_major: {mld_chunks['data_type_major']} (unknown)")
            
    match mld_chunks["data_type_minor"]:
        case 0:
            print(f"data_type_minor: {mld_chunks['data_type_minor']} (music)")
        case 1:
            print(f"data_type_minor: {mld_chunks['data_type_minor']} (all)")
        case 2:
            print(f"data_type_minor: {mld_chunks['data_type_minor']} (part)")
        case _:
            print(f"data_type_minor: {mld_chunks['data_type_minor']} (unknown)")

    print(f"number_of_tracks: {mld_chunks['number_of_tracks']} ({mld_chunks['number_of_tracks']*4} chords)")

    if mld_chunks.get("sorc"):
        from_str = to_bin(mld_chunks["sorc"])[0:7]
        match from_str:
            case "0000000":
                print(f"from: {from_str} (download from network)")
            case "0000001":
                print(f"from: {from_str} (using terminal input function)")
            case "0000010":
                print(f"from: {from_str} (input using terminal external I/F)")
            case _:
                print(f"from: {from_str} (unknown)")

        isProtected =  bool(to_bin(mld_chunks["sorc"])[7])
        print(f"isProtected: {isProtected}")

    if mld_chunks.get("vers"):
        integer_part = int(mld_chunks["vers"][0:2])
        decimal_part = int(mld_chunks["vers"][2:4])
        print(f"MFi Version: {integer_part}.{decimal_part:02}")
        
    if mld_chunks.get("date"):
        try:
            print(f"date: {datetime.datetime.strptime(mld_chunks["date"].decode("ascii"), '%Y%m%d')}")
        except:
            print(f"date: {mld_chunks["date"]}")

    if mld_chunks.get("copy"):
        print(f"copyright: {mld_chunks["copy"].decode("cp932", "ignore")}")

    if mld_chunks.get("supt"):
        print(f"plugin: {mld_chunks["supt"].decode("cp932", "ignore")}")

    if mld_chunks.get("prot"):
        print(f"provider: {mld_chunks["prot"]}")

    if mld_chunks.get("note"):
        print(f"note: {mld_chunks["note"]}")

    if mld_chunks.get("exst"):
        print(f"exst: {mld_chunks["exst"]}")

    if mld_chunks.get("auth"):
        print(f"author: {mld_chunks["auth"]}")

    if mld_chunks.get("ainf"):
        print(f"ainf: {mld_chunks["ainf"]}")

    if mld_chunks.get("thrd"):
        print(f"thrd: {mld_chunks["thrd"]}")

    if mld_chunks.get("cuep"):
        print(f"cuep: {mld_chunks["cuep"]}")

    for key, value in mld_chunks.items():
        if key not in ("file_size", "tracks", "titl", "data_type_major", "data_type_minor", "number_of_tracks",
                       "vers", "date", "copy", "prot", "note", "exst", "sorc", "supt", "auth", "ainf", "thrd", "cuep"
                       ):
            raise Exception(key, value)
    
if __name__ == "__main__":
    if os.path.isdir(sys.argv[1]):
        for root, dirs, files in os.walk(sys.argv[1]):
            for file in files:
                if file.lower().endswith(".mld"):
                    print(f"\n[{file}]")
                    main(os.path.join(root, file))
    else:
        for file_path in sys.argv[1:]:
            print(f"\n[{os.path.basename(file_path)}]")
            main(file_path)
