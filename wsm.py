# No need to touch anything in this file
# Use the config.json file to configure all settings.
#
# Requires:
#  * PyWin32 package: http://sourceforge.net/projects/pywin32/
#  * WMI package: https://pypi.python.org/pypi/WMI/

import wmi
import json
import smtplib
import subprocess
from tkinter import *
from email.mime.text import MIMEText

config_file = 'config.json'
log_file = 'wsm.log'
smtp_server = ''
from_email = ''
email_subject = 'WSM Alert'


# Checks the requested service on the set systems using a WMI call and report the result
#
# Input (JSON Converted to array):
# [
#   {
#       "system":"COMPUTER NAME or IP",
#       "service":"NAME of SERVICE to watch",
#       "auth":
#       {
#           "user":"NAME of a USER that has ADMIN rights on the computer",
#           "password":"That users PASSWORD"
#       },
#       "actions":
#       [
#           {
#               "state":[],
#               "action":[]
#           }
#       ]
#   }
# ]
#
# Output (Dictionary):
# {'status': (int), 'system': (str), 'service': (str), 'state':(str)}


def check_service(service_array):
    try:
        user = service_array["auth"]["user"]
        pwd = service_array["auth"]["password"]
        sys = service_array["system"]
        srv = service_array["service"]

        if (user != "") and (pwd != ""):
            c = wmi.WMI(sys, user=user, password=pwd)
        else:
            c = wmi.WMI(sys)
        for s in c.Win32_Service(Name=srv):
            state = {'status': 99, 'system': sys, 'service': srv, 'state': s.State}
    except wmi.x_access_denied:
        state = {'status': -1, 'system': sys, 'service': srv, 'state': "Access Denied"}
    except:
        state = {'status': -99, 'system': sys, 'service': srv, 'state': "Unknown"}
    return state


### Actions

# Processes the config.json actions section and call the function/s for that action/s
#
# Input:
#   actions_array (JSON converted array)
#   [
#     {
#         "state":["stopped"],
#         "action":["exec", "email"],
#         "cmd":"notepad.exe",
#         "email_to":["user1@faulk.me", "user2@faulk.me"]
#     }
#   ]
#
#   state - The reported state of the service
#   system - The system the service is on
#   service - The name of the service


def do_action(actions_array, state, system, service):
    for a in actions_array:
        if state.lower() in a["state"]:
            for do in a["action"]:
                if do.lower() == "exec":
                    _actions[do](system, service, state, a["cmd"])
                elif do.lower() == "email":
                    _actions[do](system, service, state, a["email_to"])
                else:
                    _actions[do](system, service, state)


# Writes an entry to the log file
def action_log(system, service, state):
    text = "system:" + system + "|service:" + service + "|state:" + state + "|action:log\n"
    print(text)
    open(log_file, "a").write(text)


# sends an email to the email/s addddress/es provided.
def action_email(system, service, state, to_email):
    text = "The system '" + system + "' is reporting a state of '" + state + "' for the service '" + service + "'"
    print("Email: " + text)
    s = smtplib.SMTP(smtp_server)
    msg = MIMEText(text)
    msg['Subject'] = email_subject
    msg['From'] = from_email
    for e in to_email:
        msg['To'] = e
        s.sendmail(from_email, e, msg.as_string())
    s.quit()


# Pops a message box up with an alert about the status of a service
def action_alert(system, service, state):
    text = "The system '" + system + "' is reporting a state of '" + state + "' for the service '" + service + "'"
    print("Alerting: " + text)
    root = Tk()
    root.title("Alert")
    Label(root, text=text).pack()
    Button(root, text="OK", command=root.destroy).pack()
    root.mainloop()


# Executes a process
def action_exec(system, service, state, cmd):
    subprocess.call([cmd])
    print("Execute action called " + system + " - " + service + " - " + cmd)


# Used as a way to create a switch/case command in Python
_actions = {
    "log": action_log,
    "exec": action_exec,
    "email": action_email,
    "alert": action_alert,
}
### End Actions


# Load the config options from the config.json file
def load_config(config_array):
    global log_file
    global smtp_server
    global from_email
    global email_subject
    log_file = config_array["log_file"]
    smtp_server = config_array["smtp_server"]
    from_email = config_array["from_email"]
    from_email = config_array["email_subject"]


# opens the config.json file and dumps it as an array
with open(config_file) as data_file:
    data = json.load(data_file)

load_config(data["configurations"])

for srv in data["services"]:
    if srv["system"] == "":
        srv["system"] = "localhost"

    sc = check_service(srv)

    service = sc["service"]
    system = sc["system"]
    state = sc["state"]

    if sc["status"] > 0:
        print(service + " on " + system + " returned: " + state)
    else:
        print(system + " returned the error: " + state)

    do_action(srv["actions"], state, system, service)
