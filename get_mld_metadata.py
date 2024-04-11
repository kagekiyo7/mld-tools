# -*- coding: utf-8 -*-

import os
import sys
import pprint
import datetime

def get_metadata(mld: bytes):
    metadata = {}
    # header part
    data_info_size = int.from_bytes(mld[0x08:0x0A]) - 3
    metadata["file_byte"] = int.from_bytes(mld[0x04:0x08]) + 8
    
    metadata["data_type_major"] = mld[0x0A]
    metadata["data_type_minor"] = mld[0x0B]
    metadata["number_of_tracks"] = mld[0x0C]
    
    # data infomation part
    data_info = mld[0x0D:0x0D+data_info_size]
    data_info_i = 0
    while data_info_i < data_info_size:
        magic = data_info[data_info_i:data_info_i+4].decode("shift_jis", errors="ignore")
        size = int.from_bytes(data_info[data_info_i+4:data_info_i+6])
        data = data_info[data_info_i+6:data_info_i+6+size]
        match magic:
            case "titl":
                metadata["title"] = data.decode("shift_jis", errors="ignore")
            case "sorc":
                metadata["from"] = convert_to_bin(data)[0:7]
                metadata["protect"] = bool(int(convert_to_bin(data)[7]))
            case "vers":
                metadata["version"] = data.decode("shift_jis", errors="ignore")
            case "date":
                date = data.decode("shift_jis", errors="ignore")
                metadata["date"] = datetime.datetime.strptime(date, '%Y%m%d')
            case "copy":
                metadata["copyright"] = data.decode("shift_jis", errors="ignore")
            # case "prot":
                # metadata["prot"] = data.decode("shift_jis", errors="ignore")
            case "note":
                metadata["note_length"] = int.from_bytes(data)
            case "exst":
                metadata["extended_status_dependent_length"] = int.from_bytes(data)
            case "supt":
                metadata["generator"] = data.decode("shift_jis", errors="ignore")
            # case "auth":
                # metadata["auth"] = int.from_bytes(data)
            # case "ainf":
                # metadata["ainf"] = int.from_bytes(data)
            # case "thed":
                # metadata["thed"] = int.from_bytes(data)
            case _:
                if not ("unknown_magic" in metadata): metadata["unknown_magic"] = [] 
                metadata["unknown_magic"].append({
                    "magic": magic,
                    "int": int.from_bytes(data),
                    "str": data.decode('shift_jis', errors='ignore')
                 })
        data_info_i += 6 + size
    return metadata

def convert_to_bin(bytes) -> str:
    bin_list = list()
    for byte in bytes:
        bin_list.append(format(byte, '08b'))

    return ''.join(map(str, bin_list))

def is_valid_mld(mld: bytes):
    if len(mld) < (0x0C): return False
    data_info_size = int.from_bytes(mld[0x08:0x0A]) - 3
    if len(mld) < (0x0D+data_info_size): return False
    file_byte = int.from_bytes(mld[0x04:0x08]) + 8
    #3MB
    if file_byte > (3 * 1000 * 1000): return False
    return True

def main(file_path):
    with open(file_path, "rb") as file:
        metadata_binary = file.read()
    if not is_valid_mld(metadata_binary):
        print("It's not a mld.")
        return
    metadata = get_metadata(metadata_binary)
    
    # format
    match metadata["data_type_major"]:
        case 1:
            metadata["data_type_major"] = f"{metadata['data_type_major']} (ringtorn)"
        case 2:
            metadata["data_type_major"] = f"{metadata['data_type_major']} (music)"
        case _:
            metadata["data_type_major"] = f"{metadata['data_type_major']} (unknown)"
            
    match metadata["data_type_minor"]:
        case 0:
            metadata["data_type_minor"] = f"{metadata['data_type_minor']} (music)"
        case 1:
            metadata["data_type_minor"] = f"{metadata['data_type_minor']} (all)"
        case 2:
            metadata["data_type_minor"] = f"{metadata['data_type_minor']} (part)"
        case _:
            metadata["data_type_minor"] = f"{metadata['data_type_minor']} (unknown)"

    metadata["number_of_tracks"] = f"{metadata['number_of_tracks']} ({metadata['number_of_tracks']*4} chords)"

    if ("from" in metadata):
        match metadata["from"]:
            case "0000000":
                metadata["from"] += " (download from network)"
            case "0000001":
                metadata["from"] += " (using terminal input function)"
            case "0000010":
                metadata["from"] += " (input using terminal external I/F)"
            case _:
                metadata["from"] += " (unknown: {metadata['from']})"

    if ("version" in metadata):
        integer_part = int(metadata["version"][0:2])
        decimal_part = int(metadata["version"][2:4])
        metadata["version"] += f" (MFi{integer_part}.{decimal_part})"
        
    if ("date" in metadata):
        metadata["date"] = metadata["date"].strftime('%Y/%m/%d')


    pprint.pprint(metadata)
    
if __name__ == "__main__":
    for file_path in sys.argv[1:]:
        main(file_path)
