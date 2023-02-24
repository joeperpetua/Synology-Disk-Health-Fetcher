import glob
import json
import logging
from urllib.request import Request, urlopen
from lib.smartInfo import smartDataByID
from lib.kernInfo import kernelErr

logging.basicConfig(filename='smart-data.log', level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

# DEV_URL = ["./tmp/data-dev.json", "./tmp/data-dev-old.json"]

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
            if int(attr[0]) == id and int(attr[4]) > 0:
                flag_item = {
                    "name": smartDataByID(attr[0])['name'],
                    "desc": smartDataByID(attr[0])['description'],
                    "value": int(attr[4]),
                    "increment": int(attr[4])
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
            if key == err and int(current_disk['kernel_err'][key]) > 0:
                flag_item = {
                    "name": kernelErr(key)['name'],
                    "desc": kernelErr(key)['description'],
                    "value": int(current_disk['kernel_err'][key]),
                    "increment": int(current_disk['kernel_err'][key])
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
        current_disk = checkSmart(current_disk, ids_to_check)
        current_disk = checkKern(current_disk, kernel_errs_to_check)
        current_disk = checkStatus(current_disk)
        disks.append(current_disk)

    latest_file.close() 

    if "oldest_disks" in locals():
        for old_disk in oldest_disks:
            old_disk = initDisk(old_disk)
            for disk in disks:
                if old_disk['serial'] == disk['serial']:
                    old_disk = checkSmart(old_disk, ids_to_check)
                    old_disk = checkKern(old_disk, kernel_errs_to_check)
                    disk = compareFlags(old_disk, disk)
        oldest_file.close()
    
    return disks

def main():
    url = 'https://requestinspector.com/inspect/smart_data_api'
    period = 30
    query = {}
    logging.info(f'Running verification with period of {period} days.')

    with open('/proc/sys/kernel/syno_serial') as f:
        query['serial_number'] = f.read()
        f.close()
    latest_path, oldest_path = getFiles(period)
    query['disks'] = getDisks(latest_path, oldest_path)

    request = Request(url, json.dumps(query).encode('utf-8'))
    request.add_header('Content-Type', 'application/json')
    try:
        urlopen(request)
    except:
        logging.exception('POST request failed.')
    else:
        logging.info(f'SMART data sent to server successfully.')

if __name__ == "__main__":
    main()