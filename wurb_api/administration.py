#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: https://github.com/cloudedbats/wurb_2026
# Author: Arnold Andreasson, info@cloudedbats.org
# License: MIT License (see LICENSE or http://opensource.org/licenses/mit).

import logging
import pathlib
import fastapi
import fastapi.templating
from fastapi.responses import JSONResponse, FileResponse
from typing import Union
import wurb_core

logger = logging.getLogger(wurb_core.logger_name)
templates_path = pathlib.Path(wurb_core.workdir_path, "wurb_app/templates")
templates = fastapi.templating.Jinja2Templates(directory=templates_path)
admin_router = fastapi.APIRouter()


@admin_router.get(
    "/pages/admin",
    tags=["HTML pages"],
    description="Administration page loaded as HTML.",
)
async def load_admin_page(request: fastapi.Request):
    """ """
    try:
        logger.debug("API called: module_admin.")
        return templates.TemplateResponse(
            "administration.html",
            {
                "request": request,
                "wurb_version": wurb_core.__version__,
            },
        )
    except Exception as e:
        message = "API - load_admin_page. Exception: " + str(e)
        logger.debug(message)


@admin_router.get(
    "/administration/sources",
    tags=["Administration"],
    description="Get source directories for recordings.",
)
async def get_recording_sources(request: fastapi.Request):
    """ """
    try:
        logger.debug("API called: get_recording_sources.")
        json_data = wurb_core.record_manager.get_rec_sources()
        return JSONResponse(content=json_data)
    except Exception as e:
        message = "API - get_recording_sources. Exception: " + str(e)
        logger.debug(message)


@admin_router.get(
    "/administration/nights",
    tags=["Administration"],
    description="Get directories for recording nights.",
)
async def get_recording_nights(
    sourceId: str,
):
    """ """
    try:
        logger.debug("API called: get_recording_nights.")
        json_data = wurb_core.record_manager.get_rec_nights(source_id=sourceId)
        return JSONResponse(content=json_data)
    except Exception as e:
        message = "API - get_recording_nights. Exception: " + str(e)
        logger.debug(message)


@admin_router.get(
    "/administration/info",
    tags=["Administration"],
    description="Get info for one recording event/night.",
)
async def get_administration_info(
    sourceId: str,
    nightId: str,
):
    """ """
    try:
        logger.debug("API called: get_administration_info.")
        json_data = await wurb_core.admin_manager.get_admin_info(
            source_id=sourceId, night_id=nightId
        )
        return JSONResponse(content=json_data)
    except Exception as e:
        message = "API - get_administration_info. Exception: " + str(e)
        logger.debug(message)


@admin_router.post(
    "/administration/command",
    tags=["Administration"],
    description="Get info for one recording event/night.",
)
async def administration_command(
    sourceId: str,
    nightId: str,
    command: str,
):
    """ """
    try:
        logger.debug("API called: administration_command: " + command)

        json_data = {}
        json_data["sourceId"] = sourceId
        json_data["nightId"] = nightId
        json_data["command"] = command
        if command == "removeQ0":
            await wurb_core.cleanup.remove_q0(source_id=sourceId, night_id=nightId)
        elif command == "removeNa":
            await wurb_core.cleanup.remove_not_assigned(
                source_id=sourceId, night_id=nightId
            )
        elif command == "deleteMonitoringNight":
            await wurb_core.cleanup.delete_monitoring_night(
                source_id=sourceId, night_id=nightId
            )
        elif command in ["createReport", "createAndDownloadReport"]:
            report_path = wurb_core.report_excel.get_report_path(
                source_id=sourceId, night_id=nightId
            )
            await wurb_core.report_excel.create_report(
                source_id=sourceId, night_id=nightId, report_path=report_path
            )
            json_data["report_name"] = str(report_path.name)
        return JSONResponse(content=json_data)
    except Exception as e:
        message = "API - administration_command. Exception: " + str(e)
        logger.debug(message)


@admin_router.get(
    "/administration/downloads/report",
    tags=["Administration"],
    description="Get a report for download.",
)
async def get_report(
    sourceId: str,
    nightId: str,
):
    """ """
    try:
        report_path = wurb_core.report_excel.get_report_path(
            source_id=sourceId,
            night_id=nightId,
        )
        return FileResponse(report_path)
    except Exception as e:
        message = "API - get_report. Exception: " + str(e)
        logger.debug(message)
