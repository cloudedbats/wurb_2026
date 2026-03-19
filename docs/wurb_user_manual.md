# WURB-2026 User manual

Welcome to the user manual for the Do-It-Yourself bat detector WURB-2026.

This document describes how to run the bat detector and how the
web based graphical user interface is organized.
There is also a section for advanced users who want to modify the
configuration file.

Since the WURB detector is a DIY system you must buy and assembly the
hardware parts yourself, and also install the software needed.
The software and installation instruction can be found here:
<https://github.com/cloudedbats/wurb_2026>

The detector is based on the Raspberry Pi minicomputer.
If you want to know more about all the possibilities that computer
offer you should take a look in this document:
[Raspberry Pi basics](./raspberry_pi_basics.md)

## How to start the user interface

If the detector is built as described in the installation instructions,
simply connect power to start it. Then wait while it boots up.
The Raspberry Pi 5 has an on/off button, but earlier models do not,
so these must be turned off by cutting the power.

The WURB detector is not equipped with a screen or similar.
Instead it works as a web server and the user interface can run with any
web browser that runs on any computer or mobile phone/tablet that has
access to the detector.

The examples below assumes that your detectors hostname is "wurb01".

### Local network

When the detector is connected to your home network the detectors IP address
will be resolved by mDNS if ".local" is added to the host name.
The WURB web server use port 8080 and
the address in the web browser should look like this:

    http://wurb01.local:8080

### Hotspot mode

If the detector is running in hotspot mode, as described in the installation
description, it will work as follows.

From your computer/mobile phone/tablet check if there is a WiFi network
named "WiFi-wurb01" available.
Connect to it and enter the password "chiroptera".

The detector will use the IP address 10.42.0.1 and you have to use that since
there is no mDNS alternative for this IP address.
The address in the web browser should look like this:

    http://10.42.0.1:8080

### Remote access

If the detector is remotely deployed there are different alternatives to access
it on distance.
Check the [Raspberry Pi basics](./raspberry_pi_basics.md)
document and search for "Tailscale".

## The user interface

<p align="center">
<img width="70%" height="auto" src="../images/2_header_modules.png">
</p>

On the top there are three buttons used for navigation between the detectors three
main modules.
They are:

- **Record.**
This is the module where you set up the detector to record sound files.
It is divided into two parts.
One part is for the microphone and another part is for GPS location.

- **Annotations.**
In this module you can check each recorded file and also assign some annotations
at the same time as the detector records new files.
In some way it looks like a post processing tool,
but it is just meant to be a light version to be used when out in the field.

- **Administration.**
If you have used the annotations modul, then there is this module with the
focus on monitoring nights instead of single sound files.
Files marked as trash can be removed and an Excel report can be generated based
on the information that is provided in the previous module.
There is also one diagram and one map that can show where and when there has
been activity during the night.

## Module "Record"

<p align="center">
<img align="right" width="50%" height="auto" src="../images/1_module-record.png">
</p>

**Important**: If the detector is running in hotspot mode you must press the
button **Set time** when the detector is started up.

Otherwise the time will be set from the time value stored at last shutdown.
If the detector can reach internet, then time will be set automatically,
but this is not the case when running in hotspot mode.
Time is also set properly if a GPS unit is attached, but that may take some time
and will only happen when the GPS unit lock on to a specified number of satellites.

Another important thing is to always have a **default position** registered in
the system.
This can be done manually and they are expressed as latitude / longitude in the
decimal-degree format, for example longitude = 15.00 degrees for the central
meridian in Sweden.
This positions is needed for the scheduler to calculate sunset, sunrise, etc.
even when a GPS unit fails to deliver the right position.

<br clear="right"/>

### Sound recorder

<p align="center">
<img align="right" width="50%" height="auto" src="../images/3_sound_recorder.png">
</p>

#### 1: Detector modes

The detector can be used for both active and passive monitoring.
To make it easy to switch between different modes of usage there is a list of
available options.
There are also some additional options where you can load predefined settings,
and shut down or restart the detector.

<br clear="right"/>

- **Microphone - Off**
In this mode the detector is on but the sound stream from the microphone is
turned off.

- **Recording - On (continuously)**
Recording is on and all sound will continuously be saved to files.
The file length will still be as specified, for example 5 seconds, and no sound
frames will be lost
between the files if they are to be concatenated into bigger files later.

- **Recording - Auto detection**
This mode can be used for both active and passive monitoring.
The recording is started when sound is detected, see settings below for more details.
A one seconds long prefetch buffer of recorded sound before the triggering event
will be saved to file,
and then the recording will last until the specified file length is reached.
If needed, the recording will continue and result in more files, all of them with
the same length.

- **Recording - Manual triggering**
This is mainly used for active monitoring.
A button with the text "Trigger" will appear.
The same prefetch buffer as for auto detection is used.

- **Scheduler - Recording on**
The detector can calculate when sunset, dusk, dawn and sunrise occur if a
position expressed in latitude/longitude is available and the correct time is set.
This makes it possible to let the detector automatically adjust the start and stop
times for recordings when it is deployed for passive monitoring during longer periods.
Except for this it works in the same way as "Recording - On (continuously)"
described above.

- **Scheduler - Auto detection**
This is mainly the same as "Recording - Auto detection" but it is started and
stopped related to the scheduler settings.

- **Load "User default" settings**
It is possible to save settings as "User default".
When selecting this mode the detector is reset to this state.
More info on how to save this "User default" setting in the settings section below.

- **Load "Start-up" settings**
This is another option similar to the previous one.
The only difference is that this one can be defined as the state the detector
should have when started.

- **Load "Factory default" settings**
This is used to restore the detector to its initial state.
It will not change the stored "User default" and "Start-up" settings.
It is then easy to go back to either "User default" or "Start-up" later if
they are stored.

- **Detector - Power off**
Three buttons will appear: "Shutdown", "Restart" and "Cancel".

#### 2. Status

USB microphones can be attached and removed without turning the detector off.
Each time a recording session is activated, then the detector will scan for
connected microphones.
The name of the used one is displayed here.

Check the [Raspberry Pi basics](./raspberry_pi_basics.md) document
for a list of directly supported microphones.

#### 3. Info log /  show status

This logging table displays the same information that can be found in the log
files located in the detectors internal file system.
Most useful are the rows that tells when sound is detected and the peak
frequency/strength for that sound.
This information will also be stored in the file names of the recorded files,
but it may differ if a stronger sound was detected later before the file was stored.

By pressing **Show status** some more info can be displayed in the info log table.

#### 4. Detector time

There is a button called **Set time**.
It is important to press this button to use the time from the client
computer/mobile phone to set the detector time if the detector is
running in hotspot mode.

The Raspberry Pi does not contain an internal clock module and must rely on
external sources for that.
If it is connected to internet, then the time will be set from internet at startup.
If an USB GPS receiver is used, then time will be set automatically 30 sec
after it has locked in the satellites.
If none of the above is in place, then you have to do this manually by
pressing "Set time" each time after startup.

### Geographic location

<p align="center">
<img align="right" width="50%" height="auto" src="../images/4_geographic_location.png">
</p>

It is important to know where and when a recording is made,
and therefore the detector has support for a GPS receiver.
This is optional, but recommended, and it also solves the problem with the missing
internal clock module in the Raspberry Pi since the GPS signals also includes
timestamps.

Each recorded file has a filename that contains both time and location.
This makes it easy to find recordings on your hard disks by searching for parts
of the date or latitude/longitude strings.
This feature also makes it easy to use the detector for transect monitoring.

<br clear="right"/>

There are some different modes available:

- **Default position**
Use this if you want to use the scheduler and/or tag the files without using
a GPS receiver.
It is recommended to use two or three decimals for manually entered positions
to distinguish them from
the more exact GPS received positions.

- **GPS**
Scheduler is only available when there are GPS satellites detected.
This is an useful option if GPS is not always attached.

- **GPS or Last found GPS**
This alternative is useful if you have many detectors, but only one GPS receiver.
Connect the GPS receiver during deployment and wait until the position is found
and time is set from GPS.
Then the GPS receiver can be removed and be used to deploy the next detector.

### Modify settings

<p align="center">
<img align="right" width="50%" height="auto" src="../images/5_settings.png">
</p>

#### 1. Settings - Basic

This basic part contains settings that can be useful to modified at each deployment.
You can modify:

- The name of the directory where recorded files are stored.
- The prefix for each sound file.
- The lower limit in kHz for the sound detection algorithm.
- The sensitivity level in dBFS for the sound detection algorithm.

#### 2. Settings - Scheduler

The scheduler needs proper time and position to be able to calculate when the
sun goes down and up.
It is activated when the detector mode is either "Scheduler - Recording on" or
"Scheduler - Auto detection"
and the values for latitude and longitude differ from zero.
Be sure that the time also is properly set.

It is possible to define one start event and one stop event each day.
Either at fixed times or in relation to sunset, dusk, dawn and sunrise.

#### 3. Settings - More

This set of settings are normally not modified that often.
Available settings are:

- If date should automatically be added to the directory where recorded files
are stored.
- The length of the recorded sound files. Valid values are 4 - 60 sec.
- Recorded file type; Full Spectrum (FS) or Time Expansion (TE) where 10x is
the only option.
Note: Both alternatives contains the exact same amount of samples,
the only difference is in the header part that tells which sampling frequency
that was used.
For example 384 kHz in FS mode and 38.4 kHz in TE mode. The sound will the be
played in slow-motion.
- If time should be set from GPS when using a Raspberry Pi.
- If last found GPS value is to be cleared or reused from earlier session at startup.
- Finally there are two buttons and a possibility to select the start-up
configuration.
The buttons **User default** and **Start-up** are used to save settings that
are easily available in the detectors mode selection list.

<br clear="right"/>

## Module "Annotations"

<p align="center">
<img align="right" width="50%" height="auto" src="../images/6_annotations.png">
</p>

TODO...

<br clear="right"/>

### Navigation

### Data and spectrogram

### Quality, tags and comments

### Shortcuts

## Module "Administration"

<p align="center">
<img align="right" width="50%" height="auto" src="../images/7_administration.png">
</p>

TODO...

<br clear="right"/>

### Navigation

It is similar as in the Annotations module, but without the "Recordings" part.

### Data, activities and map

### Cleanup

### Excel report

## Advanced topics and troubleshooting

For the advanced part it may be needed to log in to the detector with SSH.
Start a terminal window and then type:

    ssh wurb@wurb01.local   # If it is connected to the local network.
    ssh wurb@10.42.0.1   # If it is running in hotspot mode.

### Settings and configuration

There is a difference between settings and configuration.
Settings is something that the user can modify when the system is up and running.
Configuration is something that is done at system startup.
Some parts of the configuration system is on a more technical level and should
only be modified
by users with an understanding of how the software works.

In the WURB system settings are stored in a small database and configuration is
stored in a YAML-file.
Both can be found in the directory "wurb_settings".

    /home/wurb/wurb_settings/wurb_settings.db
    /home/wurb/wurb_settings/wurb_config.yaml

#### Settings

There are four sets of settings stored in the database and they can be loaded in
the Record module.
They are described earlier in this document and the are "Current settings",
"User default setting", "Start-up settings" and  "Factory default settings".

If there are problems, or if you want to do a reset to factory settings/configuration,
then the easiest way is to just remove the wurb_settings directory and restart.

    cd /home/wurb
    rm -r wurb_setting

#### Configuration

TODO...

#### Add a new microphone

TODO...

#### Add a new GPS receiver

TODO...

#### Change directories used for recorded files

TODO...

#### WURB software update

TODO...

## Contact

Arnold Andreasson, Sweden.

<info@cloudedbats.org>
