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
