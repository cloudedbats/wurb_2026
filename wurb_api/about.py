#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: https://github.com/cloudedbats/wurb_2026
# Author: Arnold Andreasson, info@cloudedbats.org
# License: MIT License (see LICENSE or http://opensource.org/licenses/mit).

import logging
import pathlib
import fastapi
import fastapi.templating
import wurb_core

logger = logging.getLogger(wurb_core.logger_name)
templates_path = pathlib.Path(wurb_core.workdir_path, "wurb_app/templates")
templates = fastapi.templating.Jinja2Templates(directory=templates_path)
about_router = fastapi.APIRouter()


@about_router.get(
    "/pages/about", tags=["HTML pages"], description="About page loaded as HTML."
)
async def load_about_page(request: fastapi.Request):
    """ """
    try:
        logger.debug("API called: module_about.")
        return templates.TemplateResponse(
            "about.html",
            {
                "request": request,
                "wurb_version": wurb_core.__version__,
            },
        )
    except Exception as e:
        message = "API - load_about_page. Exception: " + str(e)
        logger.debug(message)

    except Exception as e:
        message = "AAAAA - BBBBB. Exception: " + str(e)
        self.logger.debug(message)
