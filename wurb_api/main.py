#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: https://github.com/cloudedbats/wurb_2026
# Author: Arnold Andreasson, info@cloudedbats.org
# License: MIT License (see LICENSE or http://opensource.org/licenses/mit).

import logging
import pathlib
import fastapi
import fastapi.staticfiles
import fastapi.templating
import fastapi.responses
from pydantic import BaseModel
from typing import Optional

# CloudedBats WURB.
import wurb_core
import wurb_api

logger = logging.getLogger(wurb_core.logger_name)

app = fastapi.FastAPI(
    title="CloudedBats WURB-2026",
    description="CloudedBats WURB-2026, the DIY bat detector.",
    version=wurb_core.__version__,
)

# Relative paths.
static_path = pathlib.Path(wurb_core.workdir_path, "wurb_app/static")
templates_path = pathlib.Path(wurb_core.workdir_path, "wurb_app/templates")

app.mount(
    "/static",
    fastapi.staticfiles.StaticFiles(directory=static_path),
    name="static",
)
templates = fastapi.templating.Jinja2Templates(directory=templates_path)


@app.on_event("startup")
async def startup_event():
    """ """
    logger.debug("API called: startup.")


@app.on_event("shutdown")
async def shutdown_event():
    """ """
    logger.debug("API called: shutdown.")


# Include modules.
app.include_router(wurb_api.record_router)
app.include_router(wurb_api.annotations_router)
app.include_router(wurb_api.admin_router)
app.include_router(wurb_api.about_router)


@app.get("/", tags=["HTML pages"], description="Main application page loaded as HTML.")
async def load_main_application_page(request: fastapi.Request):
    """ """
    try:
        logger.debug("API called: webpage.")
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "wurb_version": wurb_core.__version__,
            },
        )
    except Exception as e:
        message = "API - load_main_application_page. Exception: " + str(e)
        logger.debug(message)


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    favicon_path = pathlib.Path(
        wurb_core.workdir_path, "wurb_app/static/images/favicon.ico"
    )
    return fastapi.responses.FileResponse(favicon_path)
