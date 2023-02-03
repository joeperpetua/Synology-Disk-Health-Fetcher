def smartDataByID(id):
    data = {
        "ID_5": {
            "id": 5,
            "name": "Reallocated Sectors Count",
            "description": "Count of reallocated sectors. When the hard drive finds a read/write/verification error, it marks this sector as reallocated and transfers data to a special reserved area (spare area). This process is also known as remapping and reallocated sectors are called remaps. This is why, on modern hard disks, bad blocks cannot be found while testing the surface — all bad blocks are hidden in reallocated sectors. However, the more sectors that are reallocated, the more read/write speed will decrease."
        },
        "ID_196": {
            "id": 196,
            "name": "Reallocation Event Count",
            "description": "Count of remap operations. The raw value of this attribute shows the total number of attempts to transfer data from reallocated sectors to a spare area. Both successful & unsuccessful attempts are counted."
        },
        "ID_197": {
            "id": 197,
            "name": "Current Pending Sector Count",
            "description": "Number of unstable sectors (waiting to be remapped). If the unstable sector is subsequently written or read successfully, this value is decreased and the sector is not remapped. Read errors on the sector will not remap the sector, it will only be remapped on a failed write attempt. This can be problematic to test because cached writes will not remap the sector, only direct I/O writes to the disk."
        },
        "ID_198": {
            "id": 198,
            "name": "Uncorrectable Sector Count",
            "description": "The total number of uncorrectable errors when reading/writing a sector. A rise in the value of this attribute indicates defects of the disk surface and/or problems in the mechanical subsystem."
        },
        "ID_199": {
            "id": 199,
            "name": "UDMA CRC Error Count",
            "description": "The number of errors in data transfer via the interface cable as determined by ICRC (Interface Cyclic Redundancy Check)."
        },
        "ID_200": {
            "id": 200,
            "name": "Multi-Zone Error Rate",
            "description": "The total number of errors when writing a sector."
        }
    }
    return data[f'ID_{id}']