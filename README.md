#  CloudedBats - WURB-2026

Welcome to WURB-2026, the Do-It-Yourself ultrasonic sound detector for bat monitoring.

## What is WURB-2026?

WURB is an abbreviation for Wireless Ultrasonic Recorder for Bats. It contains the software needed 
for you to build your own bat detector, and the software is completely open and free.

WURB-2026 is the fourth major version of the WURB software. The three earlier repositories are called 
"cloudedbats_wurb" from 2017, "cloudedbats_wurb_2020", and "cloudedbats_wurb_2024".
Functionally wurb_2026 is similar to cloudedbats_wurb_2024. The user interface has been updated
and some new features are added. Some other features are removed for various reasons.

The WURB-2026 detector can be used for both active and passive bat monitoring. If it is connected to
internet it can be completely remotely controlled and therefore it is a good candidate for a permanent 
monitoring station.

## Pros and cons

There are many options to choose from when looking for equipment to monitor bat sounds. 
Many users want a weatherproof case, a user manual, and a phone number to call for support.
Other users want to be able to use a soldering iron to build their own detector from scratch.
This detector falls in between because no soldering is required and you have to purchase and assemble the hardware parts of the detector yourself.

Pros:

- Most parts can be purchased where electronics are sold.
- If you want to invest in a good microphone, there is no difference in sound quality compared to professional detectors. But it is also possible to use significantly cheaper microphones.
- Since the Raspberry Pi can run the Linux operating system and has support for WiFi, modem cables (Ethernet) and 4G/LTE devices can be connected, there are great possibilities for configuring how the detector communicates with the outside world.
- Since it is a modular structure, the parts can be used in other contexts. For example, a USB microphone can be connected to a mobile phone instead.
- Since the detector contains its own web server, you do not need to install other software on your mobile phone or computer to use it. A web browser is enough.
- It is fun and educational to build it yourself.

Cons:

- You have to buy and assemble all the components yourself.
- Some knowledge of Linux is required to install the software. If you don't have this knowledge yourself, you will have to ask for help. If you say you want help with a Raspberry Pi to study bats, it is probably not that difficult to get help.
- The power consumption is higher than for equivalent ready-made detectors. For single nights a power bank works well and in other contexts you can use the same power supply via USB that is used to charge mobile phones. A rule of thumb is that it draws about 5W, i.e. 1A at 5V, but the waste heat can be good for keeping the microphone dry if it is mounted in the same box.

And finally, if you already have a system with the WURB-2026 installed, 
it's easy to start recording infrared or thermal videos with the WIRC-2026 system.
Read more here: https://github.com/cloudedbats/wirc_2026 

## Hardware

IMAGE

The following hardware is required:

- Raspberry Pi minicomputer with Linux (or any computer running Windows, or macOS).
- Ultrasonic microphone.
- Micro SD card.
- GPS USB dongle.
- A USB stick or SSD drive (this is optional).
- WiFi, modem cable (Ethernet) or a 4G/LTE modem to connect to the internet.
- Power supply.

The software is installed on the micro SD card. Recorded files can be stored there too, 
or at an external USB memory stick or SSD disk.

WURB-2026 is primarily designed to run on the Raspberry Pi minicomputer.
However, it is also possible to generate executables that can be run on 
Windows or macOS. See the "pyinstaller" section below if you wish to do so.

## Software

## User interface

WURB-2026 is running an internal web server and any web browser can be used 
from both computers and mobile phones.

![WURB-2026](images/WURB_2026_UIx3.jpg?raw=true  "WURB-2026 User interface.")

There are three pages in the user interface. 
The first page, called "Record", is used to record files. 
There is a button "Setting" where adjustments can be done like setting directory
names, length of recorded files, scheduler parameters, etc.

The second page, called "Annotations", can be used to check recorded files and 
to make annotations directly in the field or afterwards.

The third page, called "Administration", is used to manage complete monitoring nights.
It gives an overview both where and when there has been activites.

## Documentation

The user documentation is (anytime soon) available here: TODO.

## Installation - Raspberry Pi

If you are a new user of Raspberry Pi, there is a lot of information to read here:

https://www.raspberrypi.com/documentation/

Use the "Raspberry Pi Imager" to install the operating system:

https://www.raspberrypi.com/software/

- Select Raspberry Pi OS Lite (64-bit), Debian Trixie with no desktop.

Edit settings. **Note that the user must be "wurb".**
Replace other parts, marked as bold, to match your needs:

- Hostname: **wurb01**
- User: wurb
- Password: **secret-password**
- WiFi SSID: **home-network**
- Password: **home-network-password**
- Wireless LAN country: **SE**
- Time zone: **Europe/Stockholm**
- Keyboard: **se**
- Activate SSH.

### Installation on the Raspberry Pi.

Move the micro SD card to the Raspberry Py and attach power.
It is important that the Raspberry Pi is connected to your local network,
either via WiFi or the modem cable.

Connect with SSH from a terminal window with this command.

    ssh wurb@wurb01.local

Start with an update/upgrade.

    sudo apt update
    sudo apt upgrade -y

### Install the WURB-2026 detector software

Install the necessary Linux/Debian packages.

    sudo apt install git python3-venv python3-dev -y
    sudo apt install libopenblas-dev pmount -y
    sudo apt install python3-pyaudio portaudio19-dev -y

Install the WURB-2026 software.

    git clone https://github.com/cloudedbats/wurb_2026.git
    cd wurb_2026/
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

Install and activate the services that uses WURB-2026.

    sudo cp raspberrypi_files/wurb_2026.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable wurb_2026.service
    sudo systemctl start wurb_2026.service

Now it should be up and running. Start a web browser with this address:

    http://wurb01.local:8080

## Extra config on Raspberry Pi

### Raspberry Pi as a WiFi hotspot.

If the detector should be accessed away from the home network, then it can run
in a hotspot mode and enable it's own WiFi network.
In the example below the WiFi name will be "WiFi-Wurb" and password "chiroptera".
Use different names to avoid conflicts if there are more detectors in range.

    sudo nmcli con add con-name wurb-hotspot ifname wlan0 type wifi ssid WiFi-Wurb
    sudo nmcli con modify wurb-hotspot wifi-sec.key-mgmt wpa-psk
    sudo nmcli con modify wurb-hotspot wifi-sec.psk chiroptera
    sudo nmcli con modify wurb-hotspot 802-11-wireless.mode ap 802-11-wireless.band bg ipv4.method shared

### Connect to other WiFi networks, etc.

Use this tool to check the network connections:

    sudo nmtui

If you run the "nmtui" tool and deactivate the connection to your home network the
detector will directly switch over to the hotspot mode.
The SSH session will stop immediately since the Raspberry Pi only contains one WiFi unit
that either can be used to connect to a WiFi network, or to run as a hotspot.
Then you have to use an Ethernet cable, and extra USB WiFi or a 4G/LTE modem to reach internet.

When using the hotspot the detector will use the IP address 10.42.0.1 and then either
"<http://wurb01.local:8080>" or "<http://10.42.0.1:8080>" can be used to access the detectors
user interface.

### USB memory stick or external SSH drive

If you are planning to store recorded files on USB memory sticks the you have to either
mount them manually via SSH, or install some software that mounts them automatically.
These commands will setup the automatic version.

    cd /home/wurb/wurb_2026
    sudo cp raspberrypi_files/usb_pmount.rules /etc/udev/rules.d/
    sudo cp raspberrypi_files/usb_pmount_handler@.service /lib/systemd/system/
    sudo cp raspberrypi_files/usb_pmount_script /usr/local/bin/
    sudo chmod +x /usr/local/bin/usb_pmount_script
    sudo udevadm control --reload-rules
    sudo udevadm trigger

Some useful commands to check attached USB devices are:

    ls /media/
    df -h
    sudo fdisk -l

Note that in the configuration file for the detector "wurb_settings/wurb_config.yaml"
these USB devices are accessible and named like "media_path: /media/USB-sda1".

### The Pettersson M500 mic

This is needed if you are planning to use the Pettersson M500 microphone,
the one that is running at 500 kHz (not M500-384).

    cd /home/wurb/wurb_2026
    sudo cp raspberrypi_files/pettersson_m500_batmic.rules /etc/udev/rules.d/
    sudo udevadm control --reload-rules
    sudo udevadm trigger

## Executable file - Windows

First step is to check that Python is installed.
Then the WURB-2026 has to be installed.
Dependent on how Python is installed on your computer you may have to
type in the whole path to Python.

    git clone https://github.com/cloudedbats/wurb_2026.git
    cd wurb_2026/
    python3 -m venv venv
    venv/Script/activate
    pip install -r requirements_pyaudio.txt

The detector should now be possible to run.
Then start a web browser with the address "<http://localhost:8080>".

    python3 wurb_main.py

To build an executable "exe" file run this.

    pip install pyinstaller
    pyinstaller wurb_main_pyinstaller.spec

The executable file will then be created in a directory called "dist".

## Configurations for the detector

When the detector is started for the first time three directories will be created.
They are **wurb_settings**, **wurb_logging** and **wurb_recordings**.
The two first directories are located on the SD card directly under /home/wurb.
"wurb_recordings" can be placed at some different locations depending
on configuration settings and available attached devices for storage.

Check the file **wurb_settings/wurb_config.yaml** and make adjustments if needed.

If you want to use another type of microphones, then attach it to the detector
and start the detector.
In the log file "wurb_logging/wurb_debug_log.txt" there will be some
info about connected devices that can be used in the wurb_config.yaml file.

More info on this topic in the upcoming user manual.

## Contact

Arnold Andreasson, Sweden.

<info@cloudedbats.org>


