
var adminSelectedSourceValue = "";
var adminSelectedNightValue = "";

var activityPlot = null;
var activityPlotLayout = null;
var activityPlotConfig = null;
var leafletMap = null;
var leafletMarkers = null;

function initActivityPlot() {
    try {
        if (activityPlot === null) {
            activityPlotLayout = {
                paper_bgcolor: "rgb(228, 228, 228)",
                plot_bgcolor: "rgb(228, 228, 228)",
                xaxis: {
                    type: "date",
                },
                yaxis: {
                    range: [0, 101],
                    title: {
                        text: "Peak frequency (kHz)",
                        font: { size: 10 },
                    }
                },
                title: {
                    text: "",
                    font: { size: 12 },
                },
                margin: {
                    l: 50,
                    r: 20,
                    b: 40,
                    t: 50,
                    pad: 4
                },
            };
            activityPlotConfig = {
                responsive: true,
                autosize: true,
                scrollZoom: true,
                displaylogo: false,
                modeBarButtonsToRemove: [
                    "select2d", "lasso2d",
                    "zoomIn2d", "zoomOut2d",
                    "autoScale2d",
                ]
            }
        }
    } catch (err) {
        activityPlot = false;
        alert("ERROR initLeafletMap: " + err);
        console.log(err);
    };
}

function updateActivityPlot() {
    clearActivityPlot()
    initActivityPlot();
    if (activityPlot === false) {
        return
    }
    const data = [{
        x: activityPlotDateTime,
        y: activityPlotArray,
        mode: "markers"
    }];
    activityPlotLayout.title.text = adminSelectedNightValue;
    Plotly.newPlot("activityPlotId", data, activityPlotLayout, activityPlotConfig);
}

function clearActivityPlot() {
    Plotly.purge('activityPlotId');
}

function initLeafletMap() {
    try {
        if (leafletMap === null) {
            leafletMap = new L.Map('leafletMapId');
            var osmUrl = 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
            var osmAttrib = 'Map data © <a href="http://openstreetmap.org">OpenStreetMap</a> contributors';
            var osm = new L.TileLayer(osmUrl, { minZoom: 4, maxZoom: 16, attribution: osmAttrib });
            leafletMap.setView(new L.LatLng(57.66194, 12.63896), 9);
            leafletMap.addLayer(osm);

            leafletMarkers = L.layerGroup();
            leafletMap.addLayer(leafletMarkers);
        }
    } catch (err) {
        leafletMap = false;
        alert("ERROR initLeafletMap: " + err);
        console.log(err);
    };
}

function updateMap() {
    initLeafletMap();
    if (leafletMap === false) {
        return
    }
    leafletMarkers.clearLayers();
    var arrayLength = mapLatitudeArray.length;
    for (var i = 0; i < arrayLength; i++) {
        try {
            leafletMarkers.addLayer(L.marker([mapLatitudeArray[i], mapLongitudeArray[i]]));
        } catch (err) {
            console.log(err);
        };
    }
    // Default position.
    var meanLat = 59.767825
    var meanLong = 14.803527
    // Calculate mean values for center position.
    if (arrayLength > 0) {
        var sumLat = 0;
        for (let value of mapLatitudeArray) {
            sumLat += value;
        }
        meanLat = sumLat / arrayLength;
        var sumLong = 0;
        for (let value of mapLongitudeArray) {
            sumLong += value;
        }
        meanLong = sumLong / arrayLength;
    }
    leafletMap.flyTo(new L.LatLng(meanLat, meanLong));
}

function clearMapContent() {

}

function adminSourceLoad() {
    getAdminSourceDirs()
}

function adminSourceChanged() {
    adminSelectedSourceValue = byId("adminSelectSourceId").value;
    adminSelectedNightValue = "";
    var select = byId("adminSelectNightId");
    while (select.firstChild) {
        select.removeChild(select.firstChild);
    }
    getAdminNights(adminSelectedSourceValue);

}

function adminNightChanged() {
    adminSelectedSourceValue = byId("adminSelectSourceId").value;
    adminSelectedNightValue = byId("adminSelectNightId").value;
    getAdminNightInfo(adminSelectedSourceValue, adminSelectedNightValue)
    if ((byId("adminViewActivityId").hidden == false) ||
        (byId("adminViewMapId").hidden == false)) {
        getRecordingsData(adminSelectedSourceValue, adminSelectedNightValue);
    }
    optionList = byId("adminSelectNightId");
    optionIndex = optionList.selectedIndex;
    if (optionIndex <= 1) {
        byId("adminPreviousId").disabled = true;
    } else {
        byId("adminPreviousId").disabled = false;
    }
    if (optionIndex >= optionList.options.length - 1) {
        byId("adminNextId").disabled = true;
    } else {
        byId("adminNextId").disabled = false;
    }
}

function adminUpdate() {
    adminSelectedSourceValue = byId("adminSelectSourceId").value;
    getAdminNights(adminSelectedSourceValue);
}

function adminToggleViewData() {
    if (byId("adminViewDataId").hidden == true) {
        byId("adminViewDataButtonId").classList.add("is-inverted");
        byId("adminViewDataId").hidden = false;
    } else {
        byId("adminViewDataButtonId").classList.remove("is-inverted");
        byId("adminViewDataId").hidden = true;
    };
}

function adminToggleViewActivity() {
    if (byId("adminViewActivityId").hidden == true) {
        byId("adminViewActivityButtonId").classList.add("is-inverted");
        byId("adminViewActivityId").hidden = false;
        getRecordingsData(adminSelectedSourceValue, adminSelectedNightValue);
    } else {
        byId("adminViewActivityButtonId").classList.remove("is-inverted");
        byId("adminViewActivityId").hidden = true;
        clearActivityPlot()
    };
}

function adminToggleViewMap() {
    if (byId("adminViewMapId").hidden == true) {
        byId("adminViewMapButtonId").classList.add("is-inverted");
        byId("adminViewMapId").hidden = false;
        getRecordingsData(adminSelectedSourceValue, adminSelectedNightValue);
    } else {
        byId("adminViewMapButtonId").classList.remove("is-inverted");
        byId("adminViewMapId").hidden = true;
        clearMapContent();
    };
}

function adminPrevious() {
    optionList = byId("adminSelectNightId");
    optionIndex = optionList.selectedIndex;
    if (optionIndex > 1) {
        optionList.selectedIndex = optionIndex - 1;
        adminNightChanged()
    }
}

function adminNext() {
    optionList = byId("adminSelectNightId");
    optionIndex = optionList.selectedIndex;
    if (optionIndex < optionList.options.length - 1) {
        optionList.selectedIndex = optionIndex + 1;
        adminNightChanged()
    }
}


function adminCommand(command) {
    // let selectedValue = byId("recModeSelectId").options[byId("recModeSelectId").selectedIndex].value
    hideDivision(byId("confirmRemoveQ0Id"));
    hideDivision(byId("confirmRemoveNaId"));
    hideDivision(byId("confirmDeleteNightId"));
    if (command == "confirmRemoveQ0") {
        showDivision(byId("confirmRemoveQ0Id"));
    }
    else if (command == "confirmRemoveNa") {
        showDivision(byId("confirmRemoveNaId"));
    }
    else if (command == "confirmDeleteNight") {
        showDivision(byId("confirmDeleteNightId"));
    }
    else {
        var sourceId = byId("adminSelectSourceId").value;
        var nightId = byId("adminSelectNightId").value;
        adminExecuteCommand(sourceId, nightId, command);

        adminUpdate()
    }
}
