def kernelErr(id):
    data = {
        "icrc": {
            "id": "icrc",
            "name": "Interface CRC error",
            "description": "Interface CRC error during Ultra DMA transfer - often either a bad cable or power problem, though possibly an incorrect Ultra DMA mode setting by the driver."
        },
        "idnf": {
            "id": "idnf",
            "name": "Sector ID Not Found",
            "description": " If the sector that holds this information is corrupt there is no way for the hard drive to locate this sector and it will return the result IDNF."
        },
        "unc": {
            "id": "unc",
            "name": "Uncorrectable error",
            "description": "Uncorrectable error - often due to bad sectors on the disk."
        }
    }
    return data[id]