About
---

WSM is a Python 3+ script that can be configured to watch a service's state on a remote or local Windows system and perform an action when that service changes it's state, for example you could watch the IIS service on a Windows server and when that state equaled 'Stopped' WSM could send you an email, start an application, open an alert message or just log it to a file.

Install
---

This script was created using Python 3.2 and requires the following Python packages:

* PyWin32 package: http://sourceforge.net/projects/pywin32/
* WMI package: https://pypi.python.org/pypi/WMI/

Configuration
---

A ```config.json``` file is needed to configure WSM, a basic configuration file is included or can be found at the bottom of this page.

***

There are three settings that can be set:

* ```log_file``` - Path to and name of the log file.
* ```smtp_server``` - IP address or DNS name of an SMTP server (required if you want email alerts)
* ```from_email``` - The email address you want emails to look like they are being sent from (required if you want email alerts)
* ```email_subject``` - The subject line of an email being sent (required if you want email alerts)

__Example:__

    "configurations":
    {
        "log_file":"wsm.log",
        "smtp_server":"SMTP Server IP or DNS Name",
        "from_email":"from_WSM@faulk.me",
        "email_subject":"WSM Email Alert"
    }

Services
---

To watch a server you need to add a new section to the ```config.json``` file under the "services" section, you can see the layout below or by opening the ```config.json``` file that is included.

__Settings:__

* ```system``` - Computer IP or name
* ```service``` - The name of the service you want to monitor
* ```auth```
 * ```user``` - A user that has admin rights to the computer
 * ```password``` - The user's password

__Example:__

    "system":"COMPUTER NAME or IP",
    "service":"NAME of SERVICE to watch",
    "auth":
    {
        "user":"NAME of a USER that has ADMIN rights on the computer",
        "password":"That users PASSWORD"
    }

Actions
---

Actions are configured to do something when a service reaches a state of your choosing. You can have more then one action for any state and you can watch for more then one state of a service.

__States:__

* ```running```
* ```stopped```
* ```access denied```
* ```error```

__Actions:__

* ```log``` - Log the state to the log file
* ```alert``` - Pop-up a alert message box.
* ```email``` (Requires other option ```email_to```) - EMail a alert message to one or more email address
* ```exec``` (Requires other options ```cmd```) - Execute a program.

__Other Options:__

* ```email_to``` - This option is used by the action ```email``` and should be set to the email address/addresses that you want to alert when that action is executed.
* ```cmd``` - This option is used by the action ```exec``` and should be set to the path of a program you wish to execute when a action is executed.

__Example:__

    "actions":
    [
        {
            "state":["stopped"],
            "action":["exec", "email"],
            "cmd":"notepad.exe",
            "email_to":["user1@faulk.me", "user2@faulk.me"]
        }
    ]

*****

Basic Configuration Example
---

    {
        "configurations":
        {
            "log_file":"wsm.log",
            "smtp_server":"SMTP Server IP or DNS Name",
            "from_email":"from_WSM@faulk.me",
            "email_subject":"Subject Line"
        },
        "services":
        [
            {
                "system":"COMPUTER NAME or IP",
                "service":"NAME of SERVICE to watch",
                "auth":
                {
                    "user":"NAME of a USER that has ADMIN rights on the computer",
                    "password":"That users PASSWORD"
                },
                "actions":
                [
                    {
                        "state":["running"],
                        "action":["log"]
                    },
                    {
                        "state":["stopped"],
                        "action":["exec"],
                        "cmd":"notepad.exe"
                    },
                    {
                        "state":["error"],
                        "action":["email"],
                        "email_to":["user1@faulk.me", "user2@faulk.me"]
                    },
                    {
                        "state":["access denined"],
                        "action":["alert"]
                    }
                ]
            }
        ]
    }