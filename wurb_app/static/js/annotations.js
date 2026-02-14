
var currentRecord = {};
var copyPasteBufferActive = false;
var copyPasteBufferQuality = "";
var copyPasteBufferTags = "";
var copyPasteBufferComments = "";

var selectedSourceValue = "";
var selectedNightValue = "";
var selectedRecValue = "";

function annoToggleShortcuts() {
    if (byId("annoShortcutsId").hidden == true) {
        byId("annoBodyId").hidden = true;
        byId("annoShortcutsId").hidden = false;
        byId("buttonShortcutsId").classList.add('is-inverted');
        byId("annoShortcutsTextId").textContent = "Hide shortcuts";
    } else {
        byId("annoBodyId").hidden = false;
        byId("annoShortcutsId").hidden = true;
        byId('buttonShortcutsId').classList.remove('is-inverted');
        byId("annoShortcutsTextId").textContent = "Shortcuts";
    };
}

function annoHideShortcuts() {
    byId("annoBodyId").hidden = false;
    byId("annoShortcutsId").hidden = true;
    byId('buttonShortcutsId').classList.remove('is-inverted');
    byId("annoShortcutsTextId").textContent = "Shortcuts";
}

function annoSourceLoad() {
    getSourceDirs()
}

function annoSourceChanged() {
    selectedSourceValue = byId("annoSelectSourceId").value;
    selectedNightValue = "";
    selectedRecValue = "";
    var select = byId("annoSelectNightId");
    while (select.firstChild) {
        select.removeChild(select.firstChild);
    }
    var select = byId("annoSelectRecId");
    while (select.firstChild) {
        select.removeChild(select.firstChild);
    }
    getNights(selectedSourceValue);
}

function annoNightChanged() {
    selectedSourceValue = byId("annoSelectSourceId").value;
    selectedNightValue = byId("annoSelectNightId").value;
    var select = byId("annoSelectRecId");
    while (select.firstChild) {
        select.removeChild(select.firstChild);
    }
    getRecordings(selectedSourceValue, selectedNightValue)
}

function annoRecChanged() {
    selectedSourceValue = byId("annoSelectSourceId").value;
    selectedNightValue = byId("annoSelectNightId").value;
    selectedRecValue = byId("annoSelectRecId").value;
    getRecordInfo(selectedSourceValue, selectedNightValue, selectedRecValue);
}

function annoUpdate() {
    selectedSourceValue = byId("annoSelectSourceId").value;
    getNights(selectedSourceValue);
}

function annoToggleViewMetadata() {
    if (byId("annoViewMetadataId").hidden == true) {
        byId("annoViewMetadataButtonId").classList.add("is-inverted");
        byId("annoViewMetadataId").hidden = false;
    } else {
        byId("annoViewMetadataButtonId").classList.remove("is-inverted");
        byId("annoViewMetadataId").hidden = true;
    };
}

function annoToggleViewSpectrogram() {
    if (byId("annoViewSpectrogramId").hidden == true) {
        byId("annoViewSpectrogramButtonId").classList.add("is-inverted");
        byId("annoViewSpectrogramId").hidden = false;
        byId("annoSpectrogramLoadingId").hidden = false;

        var sourceId = currentRecord.sourceId;
        var nightId = currentRecord.nightId;
        var recordId = currentRecord.recordId;
        getSpectrogramAsBuffer(sourceId, nightId, recordId);
    } else {
        byId("annoViewSpectrogramButtonId").classList.remove("is-inverted");
        byId("annoViewSpectrogramId").hidden = true;
        byId("annoSpectrogramLoadingId").hidden = true;
    };
}

function annoToggleViewDetails() {
    if (byId("annoViewDetailsId").hidden == true) {
        byId("annoViewDetailsButtonId").classList.add("is-inverted");
        byId("annoViewDetailsId").hidden = false;
    } else {
        byId("annoViewDetailsButtonId").classList.remove("is-inverted");
        byId("annoViewDetailsId").hidden = true;
    };
}

function annoEnableDisableButtons() {
    if (copyPasteBufferActive == true) {
        byId("annoPasteId").disabled = false;
        byId("annoPasteNextId").disabled = false;
    } else {
        byId("annoPasteId").disabled = true;
        byId("annoPasteNextId").disabled = true;
    }
}

function annoFirst() {
    var textContent = byId("annoFirstTextId").textContent;
    if (textContent == "Previous night") {
        optionList = byId("annoSelectNightId");
        optionIndex = optionList.selectedIndex;
        if (optionIndex > 1) {
            optionList.selectedIndex = optionIndex - 1;
            annoNightChanged();
        }
    } else {
        var sourceId = byId("annoSelectSourceId").value;
        var nightId = byId("annoSelectNightId").value;
        var recordId = currentRecord.firstRecordId;
        getRecordInfo(sourceId, nightId, recordId);
    }
}
function annoPrevious() {
    if (byId("heroBodyAnnotationsId").hidden == false) {
        var sourceId = byId("annoSelectSourceId").value;
        var nightId = byId("annoSelectNightId").value;
        var recordId = currentRecord.previousRecordId;
        getRecordInfo(sourceId, nightId, recordId);
    }
    if (byId("heroBodyAdminId").hidden == false) {
        // For the administration page and for shortcuts.
        adminPrevious()
    }
}
function annoNext() {
    if (byId("heroBodyAnnotationsId").hidden == false) {
        var sourceId = byId("annoSelectSourceId").value;
        var nightId = byId("annoSelectNightId").value;
        var recordId = currentRecord.nextRecordId;
        getRecordInfo(sourceId, nightId, recordId);
    }
    if (byId("heroBodyAdminId").hidden == false) {
        // For the administration page and for shortcuts.
        adminNext()
    }
}
function annoLast() {
    var textContent = byId("annoLastTextId").textContent;
    if (textContent == "Next night") {
        optionList = byId("annoSelectNightId");
        optionIndex = optionList.selectedIndex;
        if (optionIndex < (optionList.length - 1)) {
            optionList.selectedIndex = optionIndex + 1;
            annoNightChanged();
        }
    } else {
        var sourceId = byId("annoSelectSourceId").value;
        var nightId = byId("annoSelectNightId").value;
        var recordId = currentRecord.lastRecordId;
        getRecordInfo(sourceId, nightId, recordId);
    }
}

function annoSetQ0() {
    if (byId("heroBodyAnnotationsId").hidden == false) {
        byId("annoQ0Id").checked = true;
        annoSaveAnnotations();
    }
}
function annoSetQ1() {
    if (byId("heroBodyAnnotationsId").hidden == false) {
        byId("annoQ1Id").checked = true;
        annoSaveAnnotations();
    }
}
function annoSetQ2() {
    if (byId("heroBodyAnnotationsId").hidden == false) {
        byId("annoQ2Id").checked = true;
        annoSaveAnnotations();
    }
}
function annoSetQ3() {
    if (byId("heroBodyAnnotationsId").hidden == false) {
        byId("annoQ3Id").checked = true;
        annoSaveAnnotations();
    }
}
function annoSetQNotAssigned() {
    if (byId("heroBodyAnnotationsId").hidden == false) {
        byId("annoQNotAssignedId").checked = true;
        annoSaveAnnotations();
    }
}
function toggleTag(tagObject) {
    if (tagObject.classList.contains("is-inverted")) {
        tagObject.classList.remove("is-inverted");
    } else {
        tagObject.classList.add("is-inverted");
    };
    tagsAsStr = annoGetTags()
    annoSaveAnnotations();
}

function annoQuickClear() {
    if (byId("heroBodyAnnotationsId").hidden == false) {
        annoSetQuality("Not assigned");
        annoSetTags("");
        annoSetComments("");
        annoSaveAnnotations();
        // copyPasteBufferActive = false;
        // copyPasteBufferQuality = "";
        // copyPasteBufferTags = "";
        // copyPasteBufferComments = "";
        // annoEnableDisableButtons();
    }
}
function annoQuickCopy() {
    if (byId("heroBodyAnnotationsId").hidden == false) {
        annoCopyAnnotations();
        copyPasteBufferActive = true;
        annoEnableDisableButtons();
    }
}
function annoQuickPaste() {
    if (byId("heroBodyAnnotationsId").hidden == false) {
        annoPasteAnnotations();
        annoSaveAnnotations();
    }
}
function annoQuickPasteNext() {
    if (byId("heroBodyAnnotationsId").hidden == false) {
        annoPasteAnnotations();
        annoSaveAnnotations();
        annoNext();
    }
}

function annoQuickDownload() {
    var sourceId = currentRecord.sourceId;
    var nightId = currentRecord.nightId;
    var recordId = currentRecord.recordId;
    var recordFile = currentRecord.recordFile;
    downloadRecFile(sourceId, nightId, recordId, recordFile)
}

function annoSaveAnnotations() {
    var sourceId = currentRecord.sourceId;
    var nightId = currentRecord.nightId;
    var recordId = currentRecord.recordId;
    var quality = annoGetQuality();
    var tags = annoGetTags();
    var comments = annoGetComments();
    saveRecordInfo(sourceId, nightId, recordId, quality, tags, comments)
}

function annoCopyAnnotations() {
    copyPasteBufferQuality = annoGetQuality();
    copyPasteBufferTags = annoGetTags();
    copyPasteBufferComments = annoGetComments();
    copyPasteBufferActive = true;
}

function annoPasteAnnotations() {
    annoSetQuality(copyPasteBufferQuality);
    annoSetTags(copyPasteBufferTags);
    annoSetComments(copyPasteBufferComments);
}

function annoGetQuality() {
    var quality = ""
    if (byId("annoQ0Id").checked == true) {
        quality = "Q0";
    }
    else if (byId("annoQ1Id").checked == true) {
        quality = "Q1";
    }
    else if (byId("annoQ2Id").checked == true) {
        quality = "Q2";
    }
    else if (byId("annoQ3Id").checked == true) {
        quality = "Q3";
    }
    else if (byId("annoQNotAssignedId").checked == true) {
        quality = "Not assigned";
    }
    return quality;
}

function annoSetQuality(quality) {
    if (quality == "Q0") {
        byId("annoQ0Id").checked = true;
    }
    else if (quality == "Q1") {
        byId("annoQ1Id").checked = true;
    }
    else if (quality == "Q2") {
        byId("annoQ2Id").checked = true;
    }
    else if (quality == "Q3") {
        byId("annoQ3Id").checked = true;
    }
    else if (quality == "Not assigned") {
        byId("annoQNotAssignedId").checked = true;
    }
}

function annoGetTags() {
    tags = ""
    if (byId("anno-FM-CF-FM-Id").classList.contains("is-inverted")) {
        tags += "FM-CF-FM,"
    }
    if (byId("anno-FM-Id").classList.contains("is-inverted")) {
        tags += "FM,"
    }
    if (byId("anno-FM-QCF-Id").classList.contains("is-inverted")) {
        tags += "FM-QCF,"
    }
    if (byId("anno-QCF-Id").classList.contains("is-inverted")) {
        tags += "QCF,"
    }
    if (byId("anno-FM+H2-Id").classList.contains("is-inverted")) {
        tags += "FM+H2,"
    }
    if (byId("anno-QCF+FM-Id").classList.contains("is-inverted")) {
        tags += "QCF+FM,"
    }

    if (byId("anno-Social-Id").classList.contains("is-inverted")) {
        tags += "Social,"
    }
    if (byId("anno-Birds-Id").classList.contains("is-inverted")) {
        tags += "Birds,"
    }
    if (byId("anno-Mammals-Id").classList.contains("is-inverted")) {
        tags += "Mammals,"
    }
    if (byId("anno-Crickets-Id").classList.contains("is-inverted")) {
        tags += "Crickets,"
    }
    if (tags.length > 1) {
        tags = tags.substring(0, tags.length - 1)
    }
    return tags;
}

function annoSetTags(tagsAsStr) {
    // Add trailing/leading , for compare strings.
    tagsAsStr = "," + tagsAsStr + ","
    if (tagsAsStr.includes(",FM-CF-FM,")) {
        byId("anno-FM-CF-FM-Id").classList.add("is-inverted")
    } else {
        byId("anno-FM-CF-FM-Id").classList.remove("is-inverted")
    }
    if (tagsAsStr.includes(",FM,")) {
        byId("anno-FM-Id").classList.add("is-inverted")
    } else {
        byId("anno-FM-Id").classList.remove("is-inverted")
    }
    if (tagsAsStr.includes(",FM-QCF,")) {
        byId("anno-FM-QCF-Id").classList.add("is-inverted")
    } else {
        byId("anno-FM-QCF-Id").classList.remove("is-inverted")
    }
    if (tagsAsStr.includes(",QCF,")) {
        byId("anno-QCF-Id").classList.add("is-inverted")
    } else {
        byId("anno-QCF-Id").classList.remove("is-inverted")
    }
    if (tagsAsStr.includes(",FM+H2,")) {
        byId("anno-FM+H2-Id").classList.add("is-inverted")
    } else {
        byId("anno-FM+H2-Id").classList.remove("is-inverted")
    }
    if (tagsAsStr.includes(",QCF+FM,")) {
        byId("anno-QCF+FM-Id").classList.add("is-inverted")
    } else {
        byId("anno-QCF+FM-Id").classList.remove("is-inverted")
    }

    if (tagsAsStr.includes(",Social,")) {
        byId("anno-Social-Id").classList.add("is-inverted")
    } else {
        byId("anno-Social-Id").classList.remove("is-inverted")
    }
    if (tagsAsStr.includes(",Birds,")) {
        byId("anno-Birds-Id").classList.add("is-inverted")
    } else {
        byId("anno-Birds-Id").classList.remove("is-inverted")
    }
    if (tagsAsStr.includes(",Mammals,")) {
        byId("anno-Mammals-Id").classList.add("is-inverted")
    } else {
        byId("anno-Mammals-Id").classList.remove("is-inverted")
    }
    if (tagsAsStr.includes(",Crickets,")) {
        byId("anno-Crickets-Id").classList.add("is-inverted")
    } else {
        byId("anno-Crickets-Id").classList.remove("is-inverted")
    }
}

function annoGetComments() {
    var comments = byId("annoCommentsId").value
    return comments;
}

function annoSetComments(comment) {
    byId("annoCommentsId").value = comment
}
