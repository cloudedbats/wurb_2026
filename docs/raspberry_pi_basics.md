# Raspberry Pi basics

Raspberry Pi is a very useful small computer that is well suited for DIY projects
of various kinds.

In this case it is used to study bats by recording ultrasound.
Then there is another parallel system for recording infrared video.
The system for ultrasound is called **WURB**, Wireless Ultrasonic Recorder for Bats.
The system for infrared video is called **WIRC**, Wireless InfraRed Camera.

Software and installation instructions for WURB and WIRC can be found here:

- <https://github.com/cloudedbats/wurb_2026>
- <https://github.com/cloudedbats/wirc_2026>

In this document I have collected some basic information about the hardware parts
used in the WURB detector, experiences about what I think works well,
recommended components/accessories, and finally some tips for troubleshooting.

## What is Raspberry Pi?

Raspberry Pi is a small (size as a credit card) single-board computer that has
become very popular among people who build their own systems.
Although it is small and cheap, it contains all the capabilities of a much more
expensive desktop or server computer.

In addition to the computer itself, a very large market has emerged for additional
accessories that are specifically aimed at DIY projects. In parallel with this,
there is of course also a very large and committed community.

If you want to read more about Raspberry Pi, you can read here:

- <https://www.raspberrypi.com/documentation/>
- <https://www.raspberrypi.com/documentation/computers/raspberry-pi.html>
- <https://www.raspberrypi.com/documentation/accessories/>

If you are not familiar with the Linux operating system and the basics of how to
use a terminal window, I recommend that you ask for help from someone with this
knowledge.
This knowledge is only necessary when installing the software on your detector,
when troubleshooting, and when you want to update the program code to the
latest version.

## Why Raspberry Pi for bat monitoring?

For this purpose, the Raspberry Pi has exactly what is needed to build a bat detector.

There are four USB ports where you can connect the ultrasonic microphone,
a GPS dongle, an external USB memory card or SSD, or an USB 4G/LTE modem when needed.
The microphone is the only mandatory part, the rest is optional.

Then there is a wireless network (WiFi) built in, a modem cable connector (Ethernet).
The power supply is via 5V USB connectors in the same way as you charge a
mobile phone. This  allows you to use a regular power bank for power supply when
needed, and adapters from 12V to 5V are easy to find if needed.

In this project, one goal has been to not require soldering or connections via
the 40-pin header when building your own detector.
USB-connected devices are prioritized and these should be automatically identified
by the software when connected. An exception is the camera sensors used in WIRC
because they are connected with a flat cable (called "FPC Camera Cable") to special
camera connectors on the Raspberry Pi board.

## Recommendations

### Raspberry Pi Models

**Raspberry Pi 4** is the model that I use most and recommend if anyone asks.
I have had these both as mobile detectors and as stationary detectors where they
have been up all year round without problems. However,
the microphones can be sensitive to damp weather and other damage.
It also handles variations in power supply significantly better than its
successor RPi 5.

**Raspberry Pi 3B** also works but the processor is slower and you may encounter
gaps in the recordings if the processor is busy with other things such as creating
a spectrogram.
In addition, installation and other maintenance take more time.
Apart from that, it is definitely a model that you can use. Some advantages are
that it is often cheaper and draws a little less power.

The **Raspberry Pi 5** is a significantly faster computer, it has an on/off button
and if you connect a special battery it also contains a real-time-clock (RTC).
Unfortunately, there are a couple of disadvantages that make it less suitable for
WURB and WIRC.
It is very sensitive to incorrect power supply and USB cables used and it goes
into sleep mode if it does not receive enough power. This is especially a problem
if you are in the field and do not have sufficient power supply or when they are
remotely controlled and you don't easily can just restart them.

But if you use the recommended power adapter from Raspberry Pi or find another
acceptable solution, it is a fantastically fast little computer.
Also check the section "power supply" below.

**Raspberry Pi Zero 2W** can maybe be used as long as you do not stress it
with anything other than recording audio continuously (don't activate FFT).
But there is only one microUSB available for attached accessories.

About **Internal memory**.
Since Raspberry Pi 3 works, the size of the internal memory is not critical,
but if you can afford to go up a bit in memory size it is preferable.
The size of the internal memory largely determines the price of the model and
memory capsules are something that is expensive right now. Personally I mostly
use the 4GB versions of Raspberry Pi 4.

### Micro SD memory card

In these computers, micro SD cards are normally used instead of a hard drive
or SSD disk. The micro SD card is used both for installing the operating system,
various software such as WURB and WIRC and for user data.
Most relatively fast SD cards should work.
I usually use **SanDisk Extreme PRO microSDXC**. The size 64 GB is enough for
most applications, even if you save the recorded audio files on this card.
Be careful when buying these because the price can vary greatly.

### Power Supply

Raspberry Pi 3B+ and older use micro-USB for power supply.
Raspberry Pi 4 and later use USB-C.

For Raspberry Pi 5, it should be a USB-C PD so that it can automatically figure
out how much the power supply can deliver. More information can be found later
in the document in the troubleshooting section.

In cases where you want to supply power from 12V, there are two options.
One way is to use a 12V to 5V adapter that you normally use in your car.
Another is to get a HAT (Hardware-At-Top) which can often convert an input
voltage between 6V and 30V.

Another option is PoE, Power-over-Ethernet. One advantage is that you get both
network and power in the same cable and these usually work over long distances,
such as 50-100m.
Then you need one PoE injector and one PoE splitter.
For the PoE splitter part there are also HAT cards for Raspberry Pi available.

This calculation shows approximately for how long a detector can be powered by
a power bank.
A good rule of thumb is that a Raspberry Pi draws approximately 5W of power,
which is equal to 1A at 5V.
A 20000 mAh power bank contains energy according to this calculation
20Ah * 3.6V = 72Wh. So 72Wh / 5W = 14.4 hours.

### Ultrasonic microphones

When choosing an ultrasonic microphone, it is good to be aware of Nyquist's theorem.
It states that the sampling rate of a microphone should be twice as high as the
actual sound you want to record. For European species, a sampling rate of 384 kHz
is sufficient, and a sampling rate of 192 kHz can work for a large number of
species that rarely have parts of their sound pulses above 90 kHz.
If there are real sounds above the Nyquist frequency (half the sampling frequency),
an "anti aliasing" filter is needed to handle this. Unfortunately,
not all ultrasonic microphones on the market have this type of filter.

TODO...IMAGE...

The ultrasonic microphones that are automatically identified by the WURB software
are those shown in the image. From left they are:

1. **Pettersson u384 and u256** Older versions have micro-USB and newer ones
have USB-C.
2. **Pettersson M500-384** Not that there is a problem when using this model
and Raspberry Pi 4. Check the troubleshooting section below.
3. **Dodotronic**, various models are directly supported.
4. **AudioMoth** with the microphone firmware installed (<https://www.openacousticdevices.info/usb-microphone>).
5. Some models in the **Pipistrelle family** (<https://www.pippyg.com>) are
supported. For example "Griff" and "Griff Mini".

Other sound cards with a USB connector can be used, but then you have to add
them to the system's configuration file. See the user manuals advanced section
for more information.

### GPS units

The most important metadata for a recorded audio file is when and where.
Without this information, the audio file is basically useless in many contexts.
WURB therefore supports GPS devices and GPS can deliver both time and position.
These values ​​are then included in the filename of each audio file.

This is especially useful when the detector is used for transect inventory or
when the detector is placed out at new locations every night.
Since Raspberry Pi does not normally have a built-in RTC, Real-time-clock,
using a GPS device is an option to automatically set the time as soon as the
device has found a sufficient number of satellites.

TODO...IMAGE...

These USB devices will hopefully be automatically recognized when plugged in.
If not, there is an instruction in the user manuals advanced section.

Sometimes it can take a very long time for a GPS device to lock onto the satellites,
especially if the devices have not been used for a while.
There are two things that can be recommended if this is a problem.
Use an USB extender so that the GPS device is not disturbed by signals from the
Raspberry Pi or other electronics.
The second trick is to leave them on for a few days before using them.
It is fine to connect them to a power source of your choice with 5V USB,
but note that a power bank may be automatically be turned off as these devices
draw very little power.

### USB memory devices

In principle, any type of USB memory device can be connected.
If it is formatted as FAT32, it should work regardless of whether it is a regular
USB memory stick, a hard drive or SSD.
Note that there is a limit of 2 TB for FAT32 that can be tricky to exceed.

The software in WURB supports two USB devices and detects when these are full
and then switches to the next one.
If they are full or not connected, the files will then be stored on the
detector's SD card.

The audio files from monitored nights always end up in a directory named
"wurb_recordings". If WIRC is used, the video files will end up in a corresponding
directory named "wirc_recordings".

There is a possibility to customize this via configuration files,
more information can be found in the advanced section of the user manual.

## Communication

Although a Raspberry Pi is a small computer, there are many possible ways to
communicate with it remotely or as a part of your local network.

Both WURB and WIRC run in what is called "headless mode",
which means that there is no graphic user interface in the same way as for a
desktop/laptop computer.
For maintenance you have to use SSH and connect from a terminal window.
However, the detector contain a web server and the detectors user interface can
be accessed via regular web browsers.
This works the same way regardless of whether the detector is locally connected
to your own home network,
if the detector shares it's own WiFi network as a hotspot,
or if it is placed somewhere out in the field with internet access.

### WiFi and local network

When installing the operating system via "Raspberry Pi Imager",
you have probably entered the name and password for your local WiFi network.
This WiFi connection works both when installing the system and when you later
want to run your detector.

In the following examples we assume that the hostname of your detector is "wurb01".
If you are on your local network, add ".local" after the hostname.
Use this command to connect with SSH:

    ssh wurb@wurb01.local

The WURB software use port 8080 and WIRC use 8082 by default.
Use a web browser to access the user interface for WURB and WIRC:

    http://wurb01.local:8080
    http://wurb01.local:8082

Note that if you reinstall the system and keep the same hostname, you may have
to clear a file containing known hosts.
This is part of a security system that is present on most computers.
On macOS, this file is located in a hidden folder and is called ".ssh/known_hosts".

### Modem cable (Ethernet)

I there are problems with the WiFi solution above, then you can use a modem cable
to connect the Rasperry Pi to an internet modem.
The rest works as described above.

Note that this alterative can be combined with Power-over-Ethernet (PoE).

### Raspberry Pi as a hotspot

Many users use the WiFi unit in the Raspberry Pi to let it share it's own network
as a WiFi hotspot.
Then it is easy to connect to it from a mobile phone to run the user interface
when out in the field.

In this case ".local" should not be used. Use this instead for SSH and for the
web addresses to the user interfaces:

    ssh wurb@wurb01
    http://wurb01:8080
    http://wurb01:8082

There is an instruction for how to install the WiFi hotspot in the installation
instruction.

Since the Raspberry Pi only have one internal WiFi unit it is not possible to
use it to connect to your home network again with WiFi.
One practical solution is to add a second WiFi unit as a USB connected one,
or use a modem cable when you are back home.

One important thing to notice if you are running the detector as a hotspot
without any connection to internet is that time is not set properly.
The solution to this is that there is a button in the user interface
called "Set time".
Another solution is to attach a GPS unit. When it has been running for some
time the GPS time will be used to set the detector time.

### WiFi for internet access

When the detector is installed as a permanent station at a place where WiFi is
available it can be used to remotely connect to it.
There is a command line tool with as simple graphical user interface that can
be used to configure WiFi connections:

    sudo nmtui

It is recommended to use a "guest" network since there is no need for the
detector to have access to someones local network.

To remotely connect to the detector with SSH, HTTP and SFTP I normally use
Tailscale. More info below.
For temporary use and if it is not set up as a hotspot you can share internet
from your mobile phone and then use Tailscale to access it from your phone,
or any other device with internet connection.

### 4G/LTE

If there is no WiFi available it is possible to use a 4G/LTE modem.
The USB modem Huawei E3372 is often recommended for use with Raspberry Pi
and I have used them a lot.
It is also possible to use a normal internet modem with 4G/LTE and then connect
to that one with a modem cable or WiFi.

Tailscale can also be used here.

### Bluetooth

Bluetooth is not used for WURB and WIRC, but it is a part of the Raspberry Pi
hardware and can be used in the future.

## File Access with SFTP

If the recorded files are stored at an external USB memory device,
then that device can be moved to a desktop/laptop computer for post processing.
If the files are stored on the micro SD card in the Raspberry Pi then it must
be downloaded with SFTP.
This is also a possibility if the detector is remotely deployed and connected
to internet in some way.

The SFTP client software I mostly use is **FileZilla** and it is available for
Windows, macOS and Linux.
For Windows users there is a similar software called **WinSCP**.

Connect with:

    Protocol: SFTP
    Host: wurb01     (or "wurb01.local" if on your local network)
    User: wurb
    Password: your-secret-password

Then the recorded sound files stored on the micro SD card can be found in this
directory "/home/wurb/wurb_recordings".
If they are stored on the USB memory devices they can be found
"/media/USB-sda1/wurb_recordings" or
here "/media/USB-sda2/wurb_recordings".
In summary, look here for the recorded sound files:

    /home/wurb/wurb_recordings
    /media/USB-sda1/wurb_recordings
    /media/USB-sda2/wurb_recordings

## Tailscale, or similar tunneling techniques

TODO...

## ADVANCED TOPICS

TODO...

### Troubleshooting

TODO...

## Contact

Arnold Andreasson, Sweden.

<info@cloudedbats.org>
