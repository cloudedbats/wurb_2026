#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: https://github.com/cloudedbats/wurb_2026
# Author: Arnold Andreasson, info@cloudedbats.org
# License: MIT License (see LICENSE or http://opensource.org/licenses/mit).

import asyncio
import uvicorn
import logging

import wurb_core


async def main():
    """ """
    # WURB logger.
    wurb_core.logger.setup_rotating_log(
        logging_dir=wurb_core.logging_dir,
        log_name=wurb_core.log_file_name,
        debug_log_name=wurb_core.debug_log_file_name,
    )
    logger_name = wurb_core.logger.get_logger_name()
    logger = logging.getLogger(logger_name)
    logger.info("")
    logger.info("")
    logger.info("Welcome to CloudedBats WURB-2026")
    logger.info("Project: https://github.com/cloudedbats/wurb_2026")
    logger.info("================ ^ö^ =================")
    logger.info("")

    try:
        # WURB settings.
        logger.debug("WURB - main. Startup settings.")
        await wurb_core.wurb_settings.startup(settings_dir=wurb_core.settings_dir)

        # WURB core startup.
        logger.debug("WURB - main. Startup core.")
        wurb_core.wurb_manager.startup()
        await asyncio.sleep(0)

        # API and app config.
        port = wurb_core.config.get("wurb_app.port", default="8080")
        port = int(port)
        host = wurb_core.config.get("wurb_app.host", default="0.0.0.0")
        log_level = wurb_core.config.get("wurb_app.log_level", default="info")

        logger.debug("WURB - main. Uvicorn startup at port: " + str(port) + ".")
        config = uvicorn.Config(
            "wurb_api:app", loop="asyncio", host=host, port=port, log_level=log_level
        )

        # WURB API and app startup.
        server = uvicorn.Server(config)
        await server.serve()

        # Shutdown actions.
        logger.debug("WURB - main. Shutdown started.")
        await wurb_core.wurb_settings.shutdown()
        await wurb_core.wurb_manager.shutdown()
        logger.debug("WURB - main. Shutdown done.")
    except Exception as e:
        message = "WURB - main. Exception: " + str(e)
        logger.error(message)


if __name__ == "__main__":
    """ """
    asyncio.run(main())
