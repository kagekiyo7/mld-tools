def parse_mld(mld_data: bytes):
    if mld_data[0:4] !=  b"melo":
        raise ValueError('The magic number "melo" is missing.')
    
    if len(mld_data) < 0x0C:
        raise ValueError('Required data cannot be read.')
    
    chunks = {
        "tracks": [],
    }

    # header part
    chunks["file_size"] = int.from_bytes(mld_data[0x04:0x08]) + 8
    chunks["data_type_major"] = mld_data[0x0A]
    chunks["data_type_minor"] = mld_data[0x0B]
    chunks["number_of_tracks"] = mld_data[0x0C]

    data_info_size = int.from_bytes(mld_data[0x08:0x0A]) - 3

    # data infomation part
    data_info = mld_data[0x0D:0x0D+data_info_size]
    data_info_i = 0

    while data_info_i < data_info_size:
        if all(97 <= byte <= 122 for byte in data_info[data_info_i:data_info_i+4]):
            magic = data_info[data_info_i:data_info_i+4].decode("ascii")
        else:
            raise ValueError("The chunk magic does not consist of lowercase alphabetic characters.")

        size_len = 2
        size = int.from_bytes(data_info[data_info_i+4:data_info_i+4+size_len], "big")

        if size == 0:
            data = None
        else:
            data = data_info[data_info_i+6:data_info_i+6+size]

        chunks[magic] = data
        data_info_i += 4 + size_len + size

    if data_info_i != data_info_size:
        raise ValueError('Unable to properly parse the data information section.')
    
    # Track part
    track_info = mld_data[0x0D+data_info_size:]
    track_info_i = 0

    while track_info_i < len(track_info):
        if all(97 <= byte <= 122 for byte in track_info[track_info_i:track_info_i+4]):
            magic = track_info[track_info_i:track_info_i+4].decode("ascii")
        else:
            try:
                text = track_info[track_info_i:].decode("cp932", "ignore")
                chunks["tracks"].append({"unknown_text": text})
                track_info_i = len(track_info)
                break
            except:
                raise ValueError("Unable to properly parse the track information section.")
                
        size_len = 4
        size = int.from_bytes(track_info[track_info_i+4:track_info_i+4+size_len], "big")

        if size == 0:
            data = None
        else:
            data = track_info[track_info_i+4+size_len:track_info_i+4+size_len+size]

        chunks["tracks"].append({magic: data})
        track_info_i += 4 + size_len + size

    if track_info_i != len(track_info):
        raise ValueError('Unable to properly parse the track information section.')

    return chunks