import requests, \
    urllib3, \
    xml.etree.ElementTree as ET
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

tufin_host = "192.168.0.101"
tufin_user = "admin"
tufin_password = "yourpassword here!"
log_file = "tufinlog.log"

now = datetime.now()
current_time = now.strftime("%H-%M-%S")


# print("Current Time =", current_time)

def use_stdata():
    openlog = open(log_file, "w")
    response = requests.get("https://%s/securetrack/api/devices" % (tufin_host), auth=(tufin_user, tufin_password),
                            verify=False)
    # print(response.content)
    root = ET.fromstring(response.content)
    for device in root.iter('device'):
        device_id = device.find('id').text
        device_name = device.find('name').text
        device_ip = device.find('ip').text
        # device_revs =device.find('latest_revision').text
        print("ID: %s\tName: %s\tIP: %s" % (device_id, device_name, device_ip))
        openlog.write("ID: %s\tName: %s\tIP: %s \n" % (device_id, device_name, device_ip))

        # Get the device configuration and write it to the log

        configresponse = requests.get("https://%s/securetrack/api/devices/%s/config/" % (tufin_host, device_id),
                                      auth=(tufin_user, tufin_password), verify=False)
        configroot = ET.fromstring(configresponse.content)
        # print(configresponse.content)
        configuration = configroot.find('device_config')
        print(configroot.text)
        config_file = open("config_%s" % (device_name), "w")
        # config_file.write(current_time)
        config_file.write(configroot.text)
        config_file.close()

        revresponse = requests.get("https://%s/securetrack/api/devices/%s/revisions/" % (tufin_host, device_id),
                                   auth=(tufin_user, tufin_password), verify=False)
        # print(revresponse.content)
        revsroot = ET.fromstring(revresponse.content)
        for rev in revsroot.iter('revision'):
            revid = rev.find('id').text
            admin = rev.find('admin').text
            time = rev.find('time').text
            date = rev.find('date').text
            rulesresponse = requests.get("https://%s/securetrack/api/revisions/%s/rules/" % (tufin_host, revid),
                                         auth=(tufin_user, tufin_password), verify=False)
            print("\tRev ID: %s\tAdmin: %s\tTime: %s\tDate: %s" % (revid, admin, time, date))
            openlog.write("\tRev ID: %s\tAdmin: %s\tTime: %s\tDate: %s \n" % (revid, admin, time, date))
            openlog.write("\n")
            # print(rulesresponse.content)
            rulesroot = ET.fromstring(rulesresponse.content)
            for rule in rulesroot.iter('rule'):
                ruleid = rule.find('id').text
                cmdline = rule.find('textual_rep').text
                print("\t\tRule ID: %s\tCmdline: %s" % (ruleid, cmdline))
                openlog.write("\t\tRule ID: %s\tCmdline: %s \n" % (ruleid, cmdline))
        openlog.write("\n")
        print()
    openlog.close()


if __name__ == "__main__":
    use_stdata()

# Write all data to log file for splunk ingestion....

