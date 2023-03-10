import glob
import json
import logging
import re
from urllib.request import Request, urlopen

logging.basicConfig(filename='sdhf.log', level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

URL = 'https://requestinspector.com/inspect/sdhf'
PERIOD = 30
# DEV_URL = ["./tmp/data-dev.json", "./tmp/data-dev-old.json"]

def smartDataByID(id):
    """
    Return SMART attribute name and description for given ID.

    Arguments:

    id - number
    """
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

def kernelErr(id):
    """
    Return kernel error name and description for given ID.

    Arguments:

    id - number
    """
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

def getFiles(period):
    """
    Return latest and oldest prediction file paths taking into account the period given.

    Arguments:

    period - number
    """
    if "DEV_URL" in globals():
        return DEV_URL[0], DEV_URL[1]
    
    paths = glob.glob('/var/log/diskprediction/*.json')
    paths.sort(reverse=True)
    # get only latest checks and oldest within the period to analyze
    if len(paths) >= period:
        return paths[0], paths[--period]
    else:
        return paths[0], None

def initDisk(disk):
    """
    Return a disk dictionary with the extra attributes for status (string) and flag (array).

    Arguments:

    disk - dictionary
    """
    disk["flag"] = []
    disk["status"] = "normal"
    return disk

def checkStatus(current_disk):
    """
    Return a disk dictionary after setting the status attribute if flags are present.

    Arguments:

    current_disk - dictionary
    """
    if current_disk['overview_status'] == "critical" or current_disk['overview_status'] == "failing":
        flag_item = {
            "name": "Disk status is not normal",
            "desc": f"Please check the status of the disk. Current status: {current_disk['overview_status']}",
            "value": 0,
            "increment": 0
        }
        current_disk['flag'].append(flag_item)
        current_disk['status'] = "error"
    if current_disk['smart'] == "critical" or current_disk['smart'] == "failing":
        flag_item = {
            "name": "SMART status is not normal",
            "desc": f"Please check the status of the disk. Current SMART status: {current_disk['smart']}",
            "value": 0,
            "increment": 0
        }
        current_disk['flag'].append(flag_item)
        current_disk['status'] = "error"
    return current_disk

def checkSmart(current_disk, ids_to_check):
    """
    Return a disk dictionary after setting a flag if a non-zero SMART value was found.

    Arguments:

    current_disk - dictionary

    ids_to_check - number array
    """
    for attr in current_disk['smart_attr']:
        for id in ids_to_check:
            value = int(float(re.sub("[^0-9.]", "", attr[4])))
            if int(attr[0]) == id and value > 0:
                flag_item = {
                    "name": smartDataByID(attr[0])['name'],
                    "desc": smartDataByID(attr[0])['description'],
                    "value": value,
                    "increment": value
                }
                current_disk['flag'].append(flag_item)
                current_disk['status'] = "warning"
    return current_disk

def checkKern(current_disk, kernel_errs_to_check):
    """
    Return a disk dictionary after setting a flag if a Kernel error was found.

    Arguments:

    current_disk - dictionary

    kernel_errs_to_check - number array
    """
    for key in current_disk['kernel_err']:
        for err in kernel_errs_to_check:
            value = int(float(current_disk['kernel_err'][key]))
            if key == err and value > 0:
                flag_item = {
                    "name": kernelErr(key)['name'],
                    "desc": kernelErr(key)['description'],
                    "value": value,
                    "increment": value
                }
                current_disk['flag'].append(flag_item)
                current_disk['status'] = "warning"
    return current_disk

def compareFlags(old_disk, latest_disk):
    """
    Return a disk dictionary after comparing the values of the oldest and latest prediction file and setting the correct increment for the checking period.

    Arguments:

    old_disk - dictionary

    latest_disk - dictionary
    """
    for item in latest_disk['flag']:
        for old_item in old_disk['flag']:
            if item['name'] == old_item['name']:
                item['increment'] -= old_item['value']
    return latest_disk

def getDisks(latest_path, oldest_path):
    """
    Return a dictionary array after getting all disks in the system and processing their data.

    Arguments:

    latest_path - string

    oldest_path - string
    """
    if oldest_path is not None:
        oldest_file = open(oldest_path)
        oldest_json = json.load(oldest_file)
        oldest_disks = oldest_json['disks']

    latest_file = open(latest_path)
    latest_json = json.load(latest_file)
    latest_disks = latest_json['disks']

    disks = []
    ids_to_check = [5, 196, 197, 198, 199, 200]
    kernel_errs_to_check = ["unc", "idnf", "icrc"]
    
    for disk in latest_disks:
        current_disk = initDisk(disk)
        if "nvme" not in current_disk['path']:
            current_disk = checkSmart(current_disk, ids_to_check)
        else:
            logging.info(f"Disk {current_disk['serial']} is nvme, skipping SMART ID check.")
        current_disk = checkKern(current_disk, kernel_errs_to_check)
        current_disk = checkStatus(current_disk)
        disks.append(current_disk)

    latest_file.close() 

    if "oldest_disks" in locals():
        for old_disk in oldest_disks:
            old_disk = initDisk(old_disk)
            for disk in disks:
                if old_disk['serial'] == disk['serial']:
                    if "nvme" not in current_disk['path']:
                        old_disk = checkSmart(old_disk, ids_to_check)
                    old_disk = checkKern(old_disk, kernel_errs_to_check)
                    disk = compareFlags(old_disk, disk)
        oldest_file.close()
    
    return disks

def main():
    query = {}
    logging.info(f'Running verification with period of {PERIOD} days.')
    try:
        with open('/proc/sys/kernel/syno_serial') as f:
            query['NAS_SN'] = f.read().replace('\n', '')
            f.close()
    except: 
        logging.exception('Getting NAS serial number failed.')
        logging.warning(f'Stopping without success.')
        exit()

    try:
        latest_path, oldest_path = getFiles(PERIOD)
    except:
        logging.exception('Getting disk prediction files failed.')
        logging.warning(f'Stopping without success.')
        exit()

    try:
        query['disks'] = getDisks(latest_path, oldest_path)
    except:
        logging.exception('Getting disk data failed.')
        logging.warning(f'Stopping without success.')
        exit()

    request = Request(URL, json.dumps(query).encode('utf-8'))
    request.add_header('Content-Type', 'application/json')
    try:
        urlopen(request)
    except:
        logging.exception('POST request failed.')
        logging.warning(f'Stopping without success.')
        exit()
    else:
        logging.info(f'SMART data sent to server successfully.')

if __name__ == "__main__":
    main()