
function byId(id) {
    return document.getElementById(id);
};

// Generic functions.
function hideDivision(divId) {
    if (divId != 'undefined') {
        divId.style.visibility = "hidden";
        divId.style.overflow = "hidden";
        divId.style.height = "0";
        divId.style.width = "0";
    }
};

function showDivision(divId) {
    if (divId != 'undefined') {
        divId.style.visibility = null;
        divId.style.overflow = null;
        divId.style.height = null;
        divId.style.width = null;
    }
};

function hideModules() {
    byId("moduleRecordId").classList.remove("is-inverted");
    byId("moduleAnnotationsId").classList.remove("is-inverted");
    byId("moduleAdminId").classList.remove("is-inverted");
    byId("heroBodyRecordId").hidden = true;
    byId("heroBodyAnnotationsId").hidden = true;
    byId("heroBodyAdminId").hidden = true;
    byId("heroBodyAboutId").hidden = true;
};

function activateModuleRecord() {
    hideModules();
    byId("moduleRecordId").classList.add("is-inverted");
    byId("heroBodyRecordId").hidden = false;
    recHideSettings();
};

function activateModuleAnnotations() {
    hideModules()
    byId("moduleAnnotationsId").classList.add("is-inverted");
    byId("heroBodyAnnotationsId").hidden = false;
    annoHideShortcuts();
};

function activateModuleAdministration() {
    hideModules()
    byId("moduleAdminId").classList.add("is-inverted");
    byId("heroBodyAdminId").hidden = false;
};

function activateModuleAbout() {
    hideModules()
    // byId("moduleAdminId").classList.add("is-inverted");
    byId("heroBodyAboutId").hidden = false;
};

function toggleModuleAbout() {
    if (byId('heroBodyAboutId').hidden) {
        // byId("moduleAdminId").classList.add("is-inverted");
        activateModuleAbout()
    } else {
        // byId("moduleAdminId").classList.add("is-inverted");
        activateModuleRecord();
    }
}

function fetchModuleRecord() {
    hideModules()
    fetch("/pages/record", { method: "GET" })
        .then(function (response) {
            if (response.ok) {
                return response.text();
            } else {
                return Promise.reject(response);
            }
        })
        .then(function (html) {
            byId("heroBodyRecordId").innerHTML = html;
            byId("moduleRecordId").classList.remove("is-inverted");



            activateModuleRecord()




        })
        .catch(function (err) {
            console.warn("Error in javascript fetch: ", err);
        })
};

function fetchModuleAnnotations() {
    hideModules()
    fetch("/pages/annotations", { method: "GET" })
        .then(function (response) {
            if (response.ok) {
                return response.text();
            } else {
                return Promise.reject(response);
            }
        })
        .then(function (html) {
            byId("heroBodyAnnotationsId").innerHTML = html;
            byId("moduleAnnotationsId").classList.remove("is-inverted");

            annoSourceLoad();
            adminSourceLoad();

        })
        .catch(function (err) {
            console.warn("Error in javascript fetch: ", err);
        })
};

function fetchModuleAdministration() {
    hideModules()
    fetch("/pages/admin", { method: "GET" })
        .then(function (response) {
            if (response.ok) {
                return response.text();
            } else {
                return Promise.reject(response);
            }
        })
        .then(function (html) {
            byId("heroBodyAdminId").innerHTML = html;
            byId("moduleAdminId").classList.remove("is-inverted");
        })
        .catch(function (err) {
            console.warn("Error in javascript fetch: ", err);
        })
};

function fetchModuleAbout() {
    hideModules()
    fetch("/pages/about", { method: "GET" })
        .then(function (response) {
            if (response.ok) {
                return response.text();
            } else {
                return Promise.reject(response);
            }
        })
        .then(function (html) {
            byId("heroBodyAboutId").innerHTML = html;
        })
        .catch(function (err) {
            console.warn("Error in javascript fetch: ", err);
        })
};

// Called from body onLoad.
function fetchModules() {
    setTimeout(fetchAllModules, 1000);
    // setTimeout(loadWebsocket, 1500);
};

function fetchAllModules() {
    fetchModuleRecord();
    fetchModuleAnnotations();
    fetchModuleAdministration();
    fetchModuleAbout();

    setTimeout(loadWebsocket, 2000);
};

function loadWebsocket() {

    var ws_url = (window.location.protocol === "https:") ? "wss://" : "ws://"
    ws_url += window.location.host // Note: Host includes port.
    ws_url += "/record/ws";
    startWebsocket(ws_url);
    //alert("Onload done...")
}
