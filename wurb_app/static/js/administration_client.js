
var activityPlotArray = []
var activityPlotDateTime = []
var mapLatitudeArray = []
var mapLongitudeArray = []

async function getAdminSourceDirs() {
    // fetch("/module-admin/get-rec-sources", { method: "GET" })
    fetch("/administration/sources", { method: "GET" })
        .then(function (response) {
            if (response.ok) {
                return response.json();
            } else {
                return Promise.reject(response);
            }
        })
        .then(function (json) {
            // Populate options to select list.
            var select = byId("adminSelectSourceId");
            // Empty.
            while (select.firstChild) {
                select.removeChild(select.firstChild);
            }
            // Add first option.
            var option = document.createElement("option");
            option.textContent = "Select:";
            option.value = "select";
            select.appendChild(option);
            // Use received json.
            for (var i = 0; i < json.length; i++) {
                var content = json[i];
                var option = document.createElement("option");
                option.textContent = content.name;
                option.value = content.id;
                select.appendChild(option);
            }
            // Select first row as default.
            var select = byId("adminSelectSourceId");
            if (json.length >= 1) {
                select.selectedIndex = 1
            } else {
                select.selectedIndex = 0
            }
            adminSourceChanged()
        })
        .catch(function (err) {
            console.warn("Error in javascript fetch: ", err);
        })
};

async function getAdminNights(sourceId) {
    fetch("/administration/nights?" + new URLSearchParams({
        sourceId: sourceId,
    }), { method: "GET" })
        .then(function (response) {
            if (response.ok) {
                return response.json();
            } else {
                return Promise.reject(response);
            }
        })
        .then(function (json) {
            // Populate options to select list.
            var select = byId("adminSelectNightId");
            // Empty.
            while (select.firstChild) {
                select.removeChild(select.firstChild);
            }
            // Add first option.
            var option = document.createElement("option");
            option.textContent = "Select:";
            option.value = "select";
            select.appendChild(option);
            // Use received json.
            for (var i = 0; i < json.length; i++) {
                var content = json[i];
                var option = document.createElement("option");
                option.textContent = content.id;
                option.value = content.id;
                select.appendChild(option);
            }
            // Select same row as before.
            var select = byId("adminSelectNightId");
            var found = false;
            for (var i = 0; i < select.options.length; i++) {
                if (select.options[i].value == adminSelectedNightValue) {
                    select.selectedIndex = i;
                    found = true;
                    break;
                }
            }
            if (found == false) {
                if (json.length >= 1) {
                    select.selectedIndex = 1
                } else {
                    select.selectedIndex = 0
                }
            }
            adminNightChanged()
        })
        .catch(function (err) {
            console.warn("Error in javascript fetch: ", err);
        })
};

async function getAdminNightInfo(sourceId, nightId) {

    byId("adminMonitoringNightId").textContent = ""
    byId("adminDirPathId").textContent = ""
    byId("adminNumberOfSoundFilesId").textContent = ""
    byId("adminNumberOfQ0Id").textContent = ""
    byId("adminNumberOfQ1Id").textContent = ""
    byId("adminNumberOfQ2Id").textContent = ""
    byId("adminNumberOfQ3Id").textContent = ""
    byId("adminNumberOfNoAssignedId").textContent = ""

    byId("adminPreviousId").disabled = true;
    byId("adminNextId").disabled = true;

    fetch("/administration/info?" + new URLSearchParams({
        sourceId: sourceId,
        nightId: nightId,
    }), { method: "GET" })
        .then(function (response) {
            if (response.ok) {
                return response.json();
            } else {
                return Promise.reject(response);
            }
        })
        .then(function (json) {
            byId("adminMonitoringNightId").textContent = json.monitoringNight
            byId("adminDirPathId").textContent = json.dirPath
            byId("adminNumberOfSoundFilesId").textContent = json.numberOfSoundFiles
            byId("adminNumberOfQ0Id").textContent = json.numberOfQ0
            byId("adminNumberOfQ1Id").textContent = json.numberOfQ1
            byId("adminNumberOfQ2Id").textContent = json.numberOfQ2
            byId("adminNumberOfQ3Id").textContent = json.numberOfQ3
            byId("adminNumberOfNoAssignedId").textContent = json.numberOfNoAssigned
        })
        .catch(function (err) {
            console.warn("Error in javascript fetch: ", err);
        })
};

async function getRecordingsData(sourceId, nightId) {

    activityPlotArray = []
    activityPlotDateTime = []
    mapLatitudeArray = []
    mapLongitudeArray = []
    var latitude_float = 0.0
    var longitude_float = 0.0

    clearActivityPlot()
    clearMapContent()

    fetch("/annotations/recordings?" + new URLSearchParams({
        sourceId: sourceId,
        nightId: nightId,
    }), { method: "GET" })
        .then(function (response) {
            if (response.ok) {
                return response.json();
            } else {
                return Promise.reject(response);
            }
        })
        .then(function (json) {
            // Use received json.
            for (var i = 0; i < json.length; i++) {
                var content = json[i];
                // Prepare for activityPlot.
                activityPlotArray.push(content.peakKhz);
                activityPlotDateTime.push(content.localDate + " " + content.localTime);
                try {
                    latitude_float = parseFloat(content.latitude);
                    longitude_float = parseFloat(content.longitude);
                    if (isNaN(latitude_float) || isNaN(latitude_float)) {
                        // NaN.
                    } else {
                        if ((latitude_float != 0.0) && (longitude_float != 0.0)) {
                            mapLatitudeArray.push(latitude_float);
                            mapLongitudeArray.push(longitude_float);
                        }
                    }
                } catch (err) {
                    // Not a valid lat/long.
                };
            }

            if (byId("adminViewActivityId").hidden == false) {
                updateActivityPlot();
            }
            if (byId("adminViewMapId").hidden == false) {
                updateMap();
            }
        })
        .catch(function (err) {
            console.warn("Error in javascript fetch: ", err);
        })
}

async function adminExecuteCommand(sourceId, nightId, command) {
    fetch("/administration/command?" + new URLSearchParams({
        sourceId: sourceId,
        nightId: nightId,
        command: command,
    }), { method: "POST" })
        .then(function (response) {
            if (response.ok) {
                return response.json();
            } else {
                return Promise.reject(response);
            }
        })
        .then(function (json) {
            if (json.command == "createAndDownloadReport") {
                reportSrc = "/administration/downloads/report?";
                reportSrc += "sourceId=";
                reportSrc += json.sourceId;
                reportSrc += "&nightId=";
                reportSrc += json.nightId;
                // Create temporary element.
                let hidden_a = document.createElement('a');
                hidden_a.setAttribute('href', reportSrc);
                hidden_a.setAttribute('download', json.report_name);
                document.body.appendChild(hidden_a);
                hidden_a.click();
                document.body.removeChild(hidden_a);
            }
        })
        .catch(function (err) {
            console.warn("Error in javascript fetch: ", err);
        })
};
