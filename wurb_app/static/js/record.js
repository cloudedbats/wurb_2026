var defaultLatitude = 0.0;
var defaultLongitude = 0.0;

function recToggleSettings() {
    if (byId("recSettingsId").hidden == true) {
        byId("recRecordId").hidden = true;
        byId("recLocationId").hidden = true;
        byId("recSettingsId").hidden = false;
        byId("buttonSettingsId").classList.add('is-inverted');
        byId("recSettingsTextId").textContent = "Hide settings";
    } else {
        byId("recRecordId").hidden = false;
        byId("recLocationId").hidden = false;
        byId("recSettingsId").hidden = true;
        byId('buttonSettingsId').classList.remove('is-inverted');
        byId("recSettingsTextId").textContent = "Settings";
    };
}

function recHideSettings() {
    byId("recRecordId").hidden = false;
    byId("recLocationId").hidden = false;
    byId("recSettingsId").hidden = true;
    byId('buttonSettingsId').classList.remove('is-inverted');
    byId("recSettingsTextId").textContent = "Settings";
}

// For detector mode.
function modeSelectOnChange(updateDetector) {
    let selectedValue = byId("recModeSelectId").options[byId("recModeSelectId").selectedIndex].value
    hideDivision(byId("recManualTriggeringId"));
    hideDivision(byId("recDetectorPowerOffId"));
    if (selectedValue == "mode-off") {
        if (updateDetector) {
            saveSettings()
        }
    }
    else if (selectedValue == "mode-on") {
        if (updateDetector) {
            saveSettings()
        }
    }
    else if (selectedValue == "mode-auto") {
        if (updateDetector) {
            saveSettings()
        }
    }
    else if (selectedValue == "mode-manual") {
        showDivision(byId("recManualTriggeringId"));
        if (updateDetector) {
            saveSettings()
        }
    }
    else if (selectedValue == "mode-scheduler-on") {
        if (updateDetector) {
            saveSettings()
        }
    }
    else if (selectedValue == "mode-scheduler-auto") {
        if (updateDetector) {
            saveSettings()
        }
    }
    else if (selectedValue == "load-user-default") {
        loadSettings(settingsType = "user-default")
    }
    else if (selectedValue == "load-start-up") {
        loadSettings(settingsType = "start-up")
    }
    else if (selectedValue == "load-factory-default") {
        loadSettings(settingsType = "factory-default")
    }
    else if (selectedValue == "detector-power-off") {
        showDivision(byId("recDetectorPowerOffId"));
    }
}

// For the geographic location tile.
function geoLocationSourceOnChange(updateDetector) {
    let selectedValue = byId("geoSourceSelectId").options[byId("geoSourceSelectId").selectedIndex].value
    byId("geoButtonTextId").innerHTML = "Save"
    if (selectedValue == "geo-default") {
        getDefaultLocation();
        byId("geoButtonTextId").innerHTML = "Save"
        byId("geoLatitudeDdId").disabled = false;
        byId("geoLongitudeDdId").disabled = false;
        byId("geoLocationButtonId").disabled = false;
        if (updateDetector) {
            saveLocationSource()
        }
    }
    else if (selectedValue == "geo-gps") {
        byId("geoButtonTextId").innerHTML = "Use as default position"
        byId("geoLatitudeDdId").disabled = true;
        byId("geoLongitudeDdId").disabled = true;
        byId("geoLocationButtonId").disabled = false;
        if (updateDetector) {
            saveLocationSource()
        }
    }
    else if (selectedValue == "geo-gps-or-last-found") {
        byId("geoButtonTextId").innerHTML = "Save"
        byId("geoLatitudeDdId").disabled = true;
        byId("geoLongitudeDdId").disabled = true;
        byId("geoLocationButtonId").disabled = true;
        if (updateDetector) {
            saveLocationSource()
        }
    }
    else {
        byId("geoLatitudeDdId").disabled = true;
        byId("geoLongitudeDdId").disabled = true;
        byId("geoLocationButtonId").disabled = true;
    }
}

// Disabled, HTTPS is needed.
// function activateGeoLocation() {
//   if (navigator.geolocation) {
//     navigator.geolocation.getCurrentPosition(showPosition, errorCallback, { timeout: 10000 });
//     // navigator.geolocation.getCurrentPosition(showLocation);
//     // navigator.geolocation.watchPosition(showLocation);
//     // navigator.geolocation.clearWatch(showLocation);
//   } else {
//     alert(`Geo location from client:\nNot supported by this browser.`);
//   };
// };
// function showPosition(location) {
//   byId("geoLatitudeId").value = location.coords.latitude;
//   byId("geoLongitudeId").value = location.coords.longitude;
// };
// function errorCallback(error) {
//   alert(`Geo location from client:\nERROR(" + error.code + " : " + error.message);
// };

// Functions used to updates fields based on response contents.
function updateStatus(status) {
    byId("recStatusId").innerHTML = status.recStatus;
    if (status.deviceName != "") {
        byId("recStatusId").innerHTML += "<br>"
        byId("recStatusId").innerHTML += status.deviceName;
    }
    byId("recDetectorTimeId").innerHTML = status.detectorTime;
    byId("detectorTimeId").innerHTML = status.detectorTime;
    byId("geoStatusId").innerHTML = status.locationStatus;
}

function updateLocation(location) {
    defaultLatitude = location.latitudeDd;
    defaultLongitude = location.longitudeDd;
    byId("geoSourceSelectId").value = location.geoSource
    if (location.geoSource == "geo-default") {
        byId("geoLatitudeDdId").value = location.defaultLatitudeDd
        byId("geoLongitudeDdId").value = location.defaultLongitudeDd
    } else {
        byId("geoLatitudeDdId").value = location.latitudeDd
        byId("geoLongitudeDdId").value = location.longitudeDd
    }
    // Check geolocation:
    geoLocationSourceOnChange(updateDetector = false);
}

function updateLatLong(latlong) {
    let selectedValue = byId("geoSourceSelectId").options[byId("geoSourceSelectId").selectedIndex].value
    if (selectedValue != "geo-default") {
        byId("geoLatitudeDdId").value = latlong.latitudeDd
        byId("geoLongitudeDdId").value = latlong.longitudeDd
    }
}

function updateSettings(settings) {

    lastUsedSettings = settings

    byId("recModeSelectId").value = settings.recMode
    byId("recFileDirectoryId").value = settings.fileDirectory
    byId("recFileDirectoryDateOptionId").value = settings.fileDirectoryDateOption
    byId("recFilenamePrefixId").value = settings.filenamePrefix
    byId("recDetectionLimitId").value = settings.detectionLimitKhz
    byId("recDetectionSensitivityId").value = settings.detectionSensitivityDbfs
    // byId("recDetectionAlgorithmId").value = settings.detectionAlgorithm
    byId("recRecLengthId").value = settings.recLengthS
    byId("recTypeId").value = settings.recType
    byId("settingsStartupOptionId").value = settings.startupOption
    byId("recSchedulerStartEventId").value = settings.schedulerStartEvent
    byId("recSchedulerStartAdjustId").value = settings.schedulerStartAdjust
    byId("recSchedulerStopEventId").value = settings.schedulerStopEvent
    byId("recSchedulerStopAdjustId").value = settings.schedulerStopAdjust
    // byId("recSchedulerPostActionId").value = settings.schedulerPostAction
    // byId("recSchedulerPostActionDelayId").value = settings.schedulerPostActionDelay
    byId("recUseGpsTimeId").value = settings.useGpsTime
    byId("recLastGpsAtStartupId").value = settings.lastGpsAtStartup

    modeSelectOnChange(updateDetector = false)
}

function saveSettingsClicked() {
    saveSettings()
    recToggleSettings()
}

function saveUserDefaultSettings() {
    saveSettings(settingsType = "user-defined")
}

function saveStartupSettings() {
    saveSettings(settingsType = "startup")
}

function updateLogTable(logRows) {
    htmlTableRows = ""
    for (rowIndex in logRows) {
        htmlTableRows += "<tr><td>"
        htmlTableRows += logRows[rowIndex]
        htmlTableRows += "</tr></td>"
    }
    byId("recLogTableId").innerHTML = htmlTableRows
}
