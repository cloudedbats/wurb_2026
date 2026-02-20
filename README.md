# CloudedBats - WURB-2026

Welcome to WURB-2026, the Do-It-Yourself ultrasonic sound detector for bat monitoring.

## What is WURB-2026?

WURB stands for Wireless Ultrasonic Bat Recorder.
It contains the software you need to build your own bat detector,
and the software is completely open source and free.

WURB-2026 is the fourth major release of the WURB software.
The three previous archives are named "cloudedbats_wurb" from 2017,
"cloudedbats_wurb_2020" and "cloudedbats_wurb_2024".
Functionally, wurb_2026 is similar to cloudedbats_wurb_2024.
The user interface has been updated and some new features have been added.
Some other features have been removed for various reasons.

The WURB-2026 detector can be used for both active and passive bat monitoring.
If connected to the internet, it can be controlled completely remotely and is
therefore a good candidate for a permanent monitoring station.

## Pros and Cons

There are many options to choose from when looking for equipment to monitor bat sounds.
Many users want a pre-built detector with a weatherproof case, a user manual,
and a phone number to call for support.
Other users want to use a soldering iron to build their own detector from scratch.
This detector falls in between because no soldering is required
and you have to buy and assemble the detector hardware parts yourself.

Pros:

- Most parts can be purchased where electronics are sold.

- If you want to invest in a good microphone, there is no difference in sound
quality compared to professional detectors.
However, it is also possible to use significantly cheaper microphones.

- Since the Raspberry Pi can run the Linux operating system and has support for WiFi,
modem cables (Ethernet) and 4G/LTE devices can be connected,
there are great possibilities to configure how the detector communicates with the outside world.

- Since it is a modular structure, the parts can be used in other contexts.
For example, a USB microphone can be connected to a mobile phone instead.
The areas of use for a leftover Raspberry Pi computer are very large.

- Since the detector contains its own web server, you do not need to install any other
software on your mobile phone or computer to use it. A web browser is enough.

- It is fun and educational to build it yourself.

Cons:

- You have to buy and assemble all the components yourself.

- Some knowledge of Linux is required to install the software.
If you do not have this knowledge yourself, you will have to ask for help.
If you say that you want help with a Raspberry Pi to study bats, 
it is probably not that difficult to get help.

- The power consumption is higher than for equivalent ready-made detectors.
For single nights, a power bank works well and in other contexts you can use
the same power supply via USB that is used to charge mobile phones.
A rule of thumb is that it draws about 5W, i.e. 1A at 5V, but the waste heat
can be good for keeping the microphone dry if it is mounted in the same box.

And finally, if you already have a system with the WURB-2026 installed,
it is easy to start recording infrared or thermal videos with the WIRC-2026 system.
Read more here: <https://github.com/cloudedbats/wirc_2026>

## Hardware

IMAGE

The following hardware is required:

- Raspberry Pi minicomputer with Linux (or any computer running Windows or macOS).

- Ultrasonic microphone.

- Micro SD card.

- GPS USB dongle (optional).

- A USB stick or SSD drive (optional).

- WiFi, modem cable (Ethernet) or a 4G/LTE modem to connect to the internet.
(This is also optional, the detector can run completely stand-alone and share its own network.)

- Power supply.

The software is installed on the micro SD card.
Recorded files can also be stored there, or on an external USB stick or SSD drive.

The WURB-2026 is primarily designed to run on the Raspberry Pi minicomputer.
However, it is also possible to generate executable files that can run on
Windows or macOS. See the "pyinstaller" section below if you wish to do so.

## Software

## User Interface

The WURB-2026 runs an internal web server and any web browser can be used and they can be connected from both computers and mobile phones.

![WURB-2026](images/WURB_2026_UIx3.jpg?raw=true  "WURB-2026 User interface.")

There are three pages in the user interface.
The first page, called **Record**, is used to record files.
There is a "Settings" button where adjustments can be made,
such as setting directory names, length of recorded files, scheduling parameters, etc.

The second page, called **Annotations**, can be used to check recorded files and to
make annotations directly in the field or afterwards.

The third page, called **Administration**, is used to manage complete surveillance nights.
It provides an overview of both where and when activities have occurred.

## Documentation

User documentation is (soon) available here: TODO.

## Installation - Raspberry Pi

If you are new to Raspberry Pi, there is a lot of information to read here:

<https://www.raspberrypi.com/documentation/>

Use the "Raspberry Pi Imager" to install the operating system:

<https://www.raspberrypi.com/software/>

- Select **Raspberry Pi OS Lite (64-bit), Debian Trixie without desktop**.

Edit settings. **Note that the user must be "wurb".**
Replace other parts, marked in bold, to match your needs:

- Hostname: **wurb01**
- User: wurb
- Password: **secret-password**
- WiFi SSID: **home-network**
- Password: **home-network-password**
- Wireless LAN country: **SE**
- Timezone: **Europe/Stockholm**
- Keyboard: **se**
- Enable SSH.

The hostname **wurb01** will be used throughout this installation guide.
If you plan to use more than one, it is a good idea to change it.

### Installation on Raspberry Pi

Move the microSD card and slide it into the Raspberry Pi and connect power.

It is important that the Raspberry Pi is connected to your local network,
either via WiFi or modem cable.

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

Install and enable the services that use WURB-2026.

    sudo cp raspberrypi_files/wurb_2026.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable wurb_2026.service
    sudo systemctl start wurb_2026.service

It should now be up and running. Open a browser with the following address:

    <http://wurb01.local:8080>

## Additional configuration on the Raspberry Pi

### Raspberry Pi as a WiFi hotspot

If the detector is to be accessed outside the home network, 
it can be run in hotspot mode and activate its own WiFi network.

In the example below, the WiFi name will be "WiFi-wurb01" and the password "chiroptera".
Use different names to avoid conflicts if there are more detectors within range.

    sudo nmcli con add con-name wurb-hotspot ifname wlan0 type wifi ssid WiFi-wurb01
    sudo nmcli con modify wurb-hotspot wifi-sec.key-mgmt wpa-psk
    sudo nmcli con modify wurb-hotspot wifi-sec.psk chiroptera
    sudo nmcli con modify wurb-hotspot 802-11-wireless.mode ap 802-11-wireless.band bg ipv4.method shared

### Connect to other WiFi networks, etc.

Use this tool to check and manage network connections:

    sudo nmtui

If you run the "nmtui" tool and disable the connection to your home network,
the detector will switch directly to hotspot mode.
The SSH session will be stopped immediately because the Raspberry Pi only contains one WiFi device
which can either be used to connect to a WiFi network or to run as a hotspot.
Then you need to use an Ethernet cable, an additional USB WiFi dongle, or a USB 4G/LTE modem to reach the internet.

When using the hotspot, the detector will use the IP address 10.42.0.1 and then
<http://10.42.0.1:8080> should be used to access the detectors user interface.

### USB stick or external SSH device

If you plan to store recorded files on USB sticks or disks, you will need to either mount them manually via SSH
or install software that will mount them automatically.
These commands configure the automatic version.

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

These will be automatically mounted when connected, but please turn off the detector before removing them.

## Configuration, logging and recorded files

There are three directories with useful content when using the WURB-2026.

- **/home/wurb/wurb_settings**
contains a yaml file with configuration parameters and the database used for settings.

- **/home/wurb/wurb_logging**
contains log files.

- **/home/wurb/wurb_recordings** 
contains the recorded audio files.

Configuration is mainly something that is loaded at startup
and settings are for changes made by the user while the device is in use.

If an external USB stick or SSD is connected, the **wurb_recordings** directory will be placed there.

The automatic mounting order can be changed. Check the **wurb_settings/wurb_config.yaml** file and make adjustments if necessary.

If the external memory device is formatted as FAT32, it will work without any changes.
Be aware of the 2TB limit for FAT32.

If you want to access the directories on the Raspberry Pi from your computer, SFTP clients can be used. Examples include **FileZilla** or **WinSCP**.

Settings to use when connecting from an SFTP client:

    Protocol: SFTP
    Port: 22 (Is default for SFTP)
    Host: wurb01.local (Or 10.42.0.1 if you run it as a hot spot)
    User: wurb
    Password: your-secret-password (The same as you use for SSH)

Many USB ultrasonic microphones are automatically detected when connected, but there are many new models emerging.

If you want to use a different type of microphone, connect it to the Raspberry Pi and boot it up.
The log file "wurb_logging/wurb_debug_log.txt" then contains information about connected devices that
can be used in the wurb_settings/wurb_config.yaml file.

## Executable file - pyinstaller for Windows

This instruction should be used to create a single executable file that contains
everything needed to run the detector software.
This can be done similarly on macOS or Linux if "venv\Scripts\activate"
is replaced with "source venv/bin/activate".

Depending on how Python is installed on your computer, you may need to
specify the full path to Python.

    git clone https://github.com/cloudedbats/wurb_2026.git
    cd wurb_2026/
    python3 -m venv venv
    venv\Scripts\activate
    pip install -r requirements_pyaudio.txt

Check if it works correctly.

    python3 wurb_main.py

The detector should now be able to run.
Launch a browser with the address <http://localhost:8080>.

To build an executable "exe" file, run this
(still inside the wurb_2026 directory with "venv" enabled).

    pip install pyinstaller
    pyinstaller wurb_main_pyinstaller.spec

The executable file will then be created in a directory called "dist".
Move it to a convenient location and/or share it with your friends.
The wurb_settings, wurb_logging and wurb_recordings directories are placed
relative to where the executable is located.

## Contact

Arnold Andreasson, Sweden.

<info@cloudedbats.org>
