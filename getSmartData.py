import glob
import json
from lib.smartInfo import smartDataByID

def getFiles(period):
    paths = glob.glob('/var/log/diskprediction/*.json')
    paths.sort(reverse=True)
    # get only latest checks and oldest within the period to analyze
    if len(paths) >= period:
        return paths[0], paths[--period]
    else:
        return paths[0], None

def initDisk(disk):
    disk["flag"] = []
    disk["status"] = ""
    return disk

def getDisks(latest_path, oldest_path):
    # disks are defined by the disks present in the latest prediction file
    if oldest_path is not None:
        oldest_file = open(oldest_path)
        oldest_json = json.load(oldest_file)
        oldest_disks = oldest_json['disks']

    latest_file = open(latest_path)
    latest_json = json.load(latest_file)
    latest_disks = latest_json['disks']

    disks = []
    ids_to_check = [5, 196, 197, 198, 199, 200]
    
    for disk in latest_disks:
        # init disk
        current_disk = initDisk(disk)
        # check for non-zero values
        for attr in current_disk['smart_attr']:
            for id in ids_to_check:
                if int(attr[0]) == id and int(attr[4]) > 0:
                    flag_item = {
                        "name": smartDataByID(attr[0])['name'],
                        "desc": smartDataByID(attr[0])['description'],
                        "value": attr[4],
                        "increment": 0
                    }
                    current_disk['flag'].append(flag_item)
        disks.append(current_disk)
    
    # iterate oldest disks
    # check increments
    # define status
    
    # return disks


def main():
    # amount of days to compare. Default 30
    period = 30
    # get files
    latest_path, oldest_path = getFiles(period)
    print(latest_path, oldest_path)

    disks = getDisks(latest_path, oldest_path)

if __name__ == "__main__":
    main()