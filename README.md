# Synology Disk Health Fetcher
This script will get the NAS disks health (SMART & kernel) data and will send it as a post API request.  
  
It will check the most relevant SMART IDs and kernel errors regarding the NAS disks.  
Then it will check the total value and the increment of the value in the last X amount of days. The default period is 30 days.  
After this is done, it will send a JSON object to a specified API via POST with the disks information and status.  

The most relevant attributes in the disk objects are:
```yaml
// Disk vendor
"vendor": string

// Disk model name
"model": string

// Disk serial number
"serial": string

// Status shown by Storage Manager in DSM
"overview_status": string

// Array of objects containing warning items (SMART ID & Kernel errors) with all time values and increments
"flag": [
  {
    "name": string,
    "desc": string,
    "value": number,
    "increment": number
  }
]

// predictive status based on overview status warning items found
"status": string
```

### Request body example
<details>
  <summary>See example</summary>
  
  ```yaml
  {
    "NAS_SN": "XXXXX",
    "disks": [
      // Healthy disk
      {
        "adv_damage_weight": "0",
        "adv_status": "not_support",
        "bad_sec_ct": "0",
        "below_remain_life_thr": "0",
        "capacity": "4000787030016",
        "container": "DS1019+",
        "dsl_attr": [
          [
            "403",
            "57",
            "1",
            "1",
            "0",
            "0",
            "0"
          ],
          [...]
        ],
        "erase_time": "366",
        "exc_bad_sec_ct": "",
        "firm": "1401",
        "firmware": "1401",
        "hibernation": {
          "deepsleep": 3,
          "hibernation": 1
        },
        "ihm_code": "",
        "ihm_status": "not_support",
        "ihm_test_log": [],
        "ihm_weight": 0,
        "ironwolf": "0",
        "kernel_err": {
          "icrc": 0,
          "idnf": 0,
          "reset_fail": 0,
          "retry": 0,
          "timeout": 0,
          "unc": 0
        },
        "model": "HAT5300-4T",
        "overview_status": "normal",
        "overview_weight": 0,
        "path": "/dev/sdc",
        "remain_life": "-1",
        "serial": "XXXXX",
        "slot": "3",
        "smart": "normal",
        "smart_attr": [
          [
            "1",
            "100",
            "100",
            "050",
            "0"
          ],
          [...]
        ],
        "smart_damage_weight": "0",
        "smart_disable": 0,
        "smart_info": "normal",
        "smart_suppress": 0,
        "smart_test": "normal",
        "smart_test_disable": 0,
        "smart_test_log": [],
        "smart_test_suppress": 0,
        "smart_weight": 0,
        "temperature": "22",
        "type": "HDD",
        "vendor": "Synology",
        "wdda_code": -1,
        "wdda_result": "not_support",
        "flag": [],
        "status": "normal"
      },

      // Unhealthy disk
      {
        "adv_damage_weight": "0",
        "adv_status": "not_support",
        "bad_sec_ct": "2",
        "below_remain_life_thr": "0",
        "capacity": "3000592982016",
        "container": "DS1019+",
        "dsl_attr": [],
        "erase_time": "360",
        "exc_bad_sec_ct": "",
        "firm": "01.01L01",
        "firmware": "01.01L01",
        "hibernation": {
          "deepsleep": 21,
          "hibernation": 3
        },
        "ihm_code": "",
        "ihm_status": "not_support",
        "ihm_test_log": [],
        "ihm_weight": 0,
        "ironwolf": "0",
        "kernel_err": {
          "icrc": 0,
          "idnf": 0,
          "reset_fail": 0,
          "retry": 0,
          "timeout": 0,
          "unc": 3
        },
        "model": "WD3001FAEX-00MJRA0",
        "overview_status": "normal",
        "overview_weight": 0,
        "path": "/dev/sde",
        "remain_life": "-1",
        "serial": "XXXXX",
        "slot": "5",
        "smart": "normal",
        "smart_attr": [
          [
            "1",
            "200",
            "200",
            "051",
            "0"
          ],
          [...]
        ],
        "smart_damage_weight": "0",
        "smart_disable": 0,
        "smart_info": "normal",
        "smart_suppress": 0,
        "smart_test": "normal",
        "smart_test_disable": 0,
        "smart_test_log": [
          {
            "result": "smart_complete",
            "time": "2023/02/17 00:00:02",
            "type": "quick"
          },
          {
            "result": "smart_complete",
            "time": "2023/01/18 13:33:56",
            "type": "extend"
          }
        ],
        "smart_test_suppress": 0,
        "smart_weight": 0,
        "temperature": "28",
        "type": "HDD",
        "vendor": "WDC",
        "wdda_code": -1,
        "wdda_result": "not_support",
        "flag": [
          {
            "name": "Uncorrectable Sector Count",
            "desc": "The total number of uncorrectable errors when reading/writing a sector. A rise in the value of this attribute indicates defects of the disk surface and/or problems in the mechanical subsystem.",
            "value": 2,
            "increment": 2
          },
          {
            "name": "UDMA CRC Error Count",
            "desc": "The number of errors in data transfer via the interface cable as determined by ICRC (Interface Cyclic Redundancy Check).",
            "value": 1,
            "increment": 0
          },
          {
            "name": "Multi-Zone Error Rate",
            "desc": "The total number of errors when writing a sector.",
            "value": 20,
            "increment": 20
          },
          {
            "name": "Uncorrectable error",
            "desc": "Uncorrectable error - often due to bad sectors on the disk.",
            "value": 3,
            "increment": 3
          }
        ],
        "status": "warning"
      }
    ]
  }
  ```
</details>

## Usage:
#### API URL:
In order to make the script functional, it will be needed to set the API URL to where the data will be sent.  
This can be set in the global URL variable, [line 9](https://github.com/joeperpetua/Synology-Disk-Health-Fetcher/blob/main/main.py?plain=1#L9). The default URL is a testing URL from [Request Inspector](https://requestinspector.com):
```python
URL = 'https://requestinspector.com/inspect/sdhf'
```
#### Period to check:
The time period to check for value increments is specified in days and the default value will be 30 days.  
This can be changed in the global PERIOD variable, [line 10](https://github.com/joeperpetua/Synology-Disk-Health-Fetcher/blob/main/main.py?plain=1#L10).
```python
PERIOD = 30
```
#### Logging:
The logging will be done in a file called sdhf.log, this file will created in the same directory where the script is executed.  
A normal script execution will be logged as:
```yaml
2023-02-24 19:15:41,322 [INFO] Running verification with period of 30 days.
2023-02-24 19:15:41,468 [INFO] SMART data sent to server successfully.
```

## Setup:
It is highly suggested to run this script on an independent shared folder subfolder. Please avoid running custom scripts in the root partition of your NAS.  
  
You can [download](https://github.com/joeperpetua/Synology-Disk-Health-Fetcher/releases) the script and run it daily with a scheduled task made from DSM Control Panel.  
[Task Scheduler - Documentation](https://kb.synology.com/DSM/help/DSM/AdminCenter/system_taskscheduler?version=7)  
[Tips for creating tasks and writing scripts in Task Scheduler](https://kb.synology.com/DSM/tutorial/common_mistake_in_task_scheduler_script)  
  
User-Defined script example:
```bash
cd /volume1/homes/admin/SDHF/;
python /volume1/homes/admin/SDHF/main.py
```
  
Please be aware that the script runs on Python 3 only. This is installed by default in DSM 7.


## Issues
In case of finding any issues or bugs, please [create an issue](https://github.com/joeperpetua/Synology-Disk-Health-Fetcher/issues/new) in the repository.

