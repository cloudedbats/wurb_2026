
async function getSourceDirs() {
    // fetch("/module-admin/get-rec-sources", { method: "GET" })
    fetch("/annotations/sources", { method: "GET" })
        .then(function (response) {
            if (response.ok) {
                return response.json();
            } else {
                return Promise.reject(response);
            }
        })
        .then(function (json) {
            // Populate options to select list.
            var select = byId("annoSelectSourceId");
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
            var select = byId("annoSelectSourceId");
            if (json.length >= 1) {
                select.selectedIndex = 1
            } else {
                select.selectedIndex = 0
            }
            annoSourceChanged()
        })
        .catch(function (err) {
            console.warn("Error in javascript fetch: ", err);
        })
};

async function getNights(sourceId) {
    fetch("/annotations/nights?" + new URLSearchParams({
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
            var select = byId("annoSelectNightId");
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
            var select = byId("annoSelectNightId");
            var found = false;
            for (var i = 0; i < select.options.length; i++) {
                if (select.options[i].value == selectedNightValue) {
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
                // annoNightChanged()
            }
            annoNightChanged()
        })
        .catch(function (err) {
            console.warn("Error in javascript fetch: ", err);
        })
};

async function getRecordings(sourceId, nightId) {
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
            // Populate options to select list.
            var select = byId("annoSelectRecId");
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
                option.textContent = "Rec " + (i + 1) + ": "
                option.textContent += content.localDate + " " + content.localTime
                option.textContent += " - " + content.peakKhz + " kHz";
                option.value = content.recId;
                select.appendChild(option);
            }
            // Select same row as before.
            var select = byId("annoSelectRecId");
            var found = false;
            for (var i = 0; i < select.options.length; i++) {
                if (select.options[i].value == selectedRecValue) {
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
                // annoRecChanged()
            }
            annoRecChanged()
        })
        .catch(function (err) {
            console.warn("Error in javascript fetch: ", err);
        })
}

async function getRecordInfo(sourceId, nightId, recordId) {
    byId("annoRecordingShortInfoId").textContent = "";
    byId("annoMetadataRecordFileId").textContent = "";
    byId("annoMetadataQualityId").textContent = "";
    byId("annoMetadataTagsId").textContent = "";
    byId("annoMetadataCommentsId").textContent = "";
    // byId("annoMetadataPrefixId").textContent = "";
    byId("annoMetadataLocalDateId").textContent = "";
    byId("annoMetadataLocalTimeId").textContent = "";
    // byId("annoMetadataDatetimeUtcId").textContent = "";
    byId("annoMetadataLatitudeId").textContent = "";
    byId("annoMetadataLongitudeId").textContent = "";
    byId("annoMetadataPeakKhzId").textContent = "";
    byId("annoMetadataPeakDbfsId").textContent = "";

    fetch("/annotations/metadata?" + new URLSearchParams({
        sourceId: sourceId,
        nightId: nightId,
        recordId: recordId,
    }), { method: "GET" })
        .then(function (response) {
            if (response.ok) {
                return response.json();
            } else {
                return Promise.reject(response);
            }
        })
        .then(function (json) {
            var shortInfo = " - Record " + json.index + " of " + json.maxIndex
            byId("annoRecordingShortInfoId").textContent = shortInfo;

            byId("annoMetadataRecordFileId").textContent = json.recordFile;
            byId("annoMetadataQualityId").textContent = json.quality;
            byId("annoMetadataTagsId").textContent = json.tags;
            byId("annoMetadataCommentsId").textContent = json.comments;
            // byId("annoMetadataPrefixId").textContent = json.prefix;
            byId("annoMetadataLocalDateId").textContent = json.localDate;
            byId("annoMetadataLocalTimeId").textContent = json.localTime;
            // byId("annoMetadataDatetimeUtcId").textContent = json.dateTimeUtc;
            byId("annoMetadataLatitudeId").textContent = json.latitude;
            byId("annoMetadataLongitudeId").textContent = json.longitude;
            byId("annoMetadataPeakKhzId").textContent = json.peakKhz;
            byId("annoMetadataPeakDbfsId").textContent = json.peakDbfs;
            byId("annoFirstId").disabled = true;
            byId("annoPreviousId").disabled = true;
            byId("annoNextId").disabled = true;
            byId("annoLastId").disabled = true;

            // Save all received data in client.
            currentRecord = json
            annoSetQuality(json.quality);
            annoSetTags(json.tags);
            annoSetComments(json.comments);

            // // // imageSrc = "http://localhost:8080/annotations/spectrogram?"
            // // imageSrc = "/annotations/spectrogram?"
            // // imageSrc += "sourceId="
            // // imageSrc += json.sourceId
            // // imageSrc += "&nightId="
            // // imageSrc += json.nightId
            // // imageSrc += "&recordId="
            // // imageSrc += json.recordId
            // // byId("annoSpectrogramSrcId").src = imageSrc;

            // // imageBuffer = "http://localhost:8080/annotations/spectrogram-html?"
            // imageBuffer = "/annotations/spectrogram-html?"
            // imageBuffer += "sourceId="
            // imageBuffer += json.sourceId
            // imageBuffer += "&nightId="
            // imageBuffer += json.nightId
            // imageBuffer += "&recordId="
            // imageBuffer += json.recordId
            // byId("annoSpectrogramBufferId").src = imageBufferSrc;

            // // // Create temporary element.
            // // // <img src='data:image/png;base64,{data}'/>"
            // // let hidden_a = document.createElement('a');
            // // hidden_a.setAttribute('href', reportSrc);
            // // hidden_a.setAttribute('download', json.report_name);
            // // document.body.appendChild(hidden_a);
            // // hidden_a.click();
            // // document.body.removeChild(hidden_a);

            byId("annoFirstTextId").textContent = "First"
            byId("annoLastTextId").textContent = "Last"
            byId("annoFirstId").disabled = false;
            byId("annoPreviousId").disabled = false;
            byId("annoNextId").disabled = false;
            byId("annoLastId").disabled = false;
            var optionList = byId("annoSelectNightId");
            var optionIndex = optionList.selectedIndex;
            if (json.maxIndex <= 1) {
                byId("annoPreviousId").disabled = true;
                byId("annoNextId").disabled = true;
                if (optionIndex > 1) {
                    byId("annoFirstTextId").textContent = "Previous night"
                    byId("annoFirstId").disabled = false;
                }
                if (optionIndex < optionList.options.length - 1) {
                    byId("annoLastTextId").textContent = "Next night"
                    byId("annoLastId").disabled = false;
                }
            }
            else if (json.index == 1) {
                byId("annoPreviousId").disabled = true;
                byId("annoFirstId").disabled = true;
                if (optionIndex > 1) {
                    byId("annoFirstTextId").textContent = "Previous night"
                    byId("annoFirstId").disabled = false;
                }
            }
            else if (json.index == json.maxIndex) {
                byId("annoNextId").disabled = true;
                byId("annoLastId").disabled = true;
                if (optionIndex < optionList.options.length - 1) {
                    byId("annoLastTextId").textContent = "Next night"
                    byId("annoLastId").disabled = false;
                }
            }

            if (byId("annoViewSpectrogramId").hidden == true) {
                // No action.
            } else {
                byId("annoSpectrogramLoadingId").hidden = false;
                getSpectrogramAsBuffer(sourceId, nightId, recordId)
            }
            // Select row in recording list.
            var select = byId("annoSelectRecId");
            select.selectedIndex = json.index
        })
        .catch(function (err) {
            console.warn("Error in javascript fetch: ", err);
        })
};

async function saveRecordInfo(sourceId, nightId, recordId, quality, tags, comments) {
    fetch("/annotations/metadata?" + new URLSearchParams({
        sourceId: sourceId,
        nightId: nightId,
        recordId: recordId,
        quality: quality,
        tags: tags,
        comments: comments,
    }), { method: "PUT" })
        .then(function (response) {
            if (response.ok) {
                return response.json();
            } else {
                return Promise.reject(response);
            }
        })
        .then(function (json) {
            if (currentRecord.recordId == json.recordId) {
                byId("annoMetadataQualityId").textContent = json.quality
                byId("annoMetadataTagsId").textContent = json.tags
                byId("annoMetadataCommentsId").textContent = json.comments
            }
        })
        .catch(function (err) {
            console.warn("Error in javascript fetch: ", err);
        })
};

async function downloadRecFile(sourceId, nightId, recordId, recordFile) {

    // reportSrc = "/administration/downloads/report?";
    // reportSrc += "sourceId=";
    // reportSrc += json.sourceId;
    // reportSrc += "&nightId=";
    // reportSrc += json.nightId;
    // // Create temporary element.
    // let hidden_a = document.createElement('a');
    // hidden_a.setAttribute('href', reportSrc);
    // hidden_a.setAttribute('download', json.report_name);
    // document.body.appendChild(hidden_a);
    // hidden_a.click();
    // document.body.removeChild(hidden_a);


    fileSrc = "/annotations/file?"
    fileSrc += "sourceId="
    fileSrc += sourceId
    fileSrc += "&nightId="
    fileSrc += nightId
    fileSrc += "&recordId="
    fileSrc += recordId
    // Create temporary element.
    let hidden_a = document.createElement('a');
    hidden_a.setAttribute('href', fileSrc);
    hidden_a.setAttribute('download', recordFile);
    document.body.appendChild(hidden_a);
    hidden_a.click();
    document.body.removeChild(hidden_a);

};


async function getSpectrogramAsBuffer(sourceId, nightId, recordId) {

    // byId("annoSpectrogramBufferId").src = ""

    fetch("/annotations/spectrogram?" + new URLSearchParams({
        sourceId: sourceId,
        nightId: nightId,
        recordId: recordId,
    }), { method: "GET" })
        .then(function (response) {
            if (response.ok) {
                return response.json();
            } else {
                return Promise.reject(response);
            }
        })
        .then(function (json) {
            if (json != null) {
                if (json.imageBufferSrc == null) {
                    byId("annoSpectrogramBufferId").src = "";
                } else {
                    byId("annoSpectrogramBufferId").src = json.imageBufferSrc;
                }
            }
            byId("annoSpectrogramLoadingId").hidden = true;

        })
        .catch(function (err) {
            console.warn("Error in javascript fetch: ", err);
        })
};
