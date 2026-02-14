#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: https://github.com/cloudedbats/wurb_2026
# Author: Arnold Andreasson, info@cloudedbats.org
# License: MIT License (see LICENSE or http://opensource.org/licenses/mit).

import asyncio
import logging
import pathlib
import xlsxwriter

import wurb_core


class ReportExcel(object):
    """ """

    def __init__(self, config=None, logger=None, logger_name="DefaultLogger"):
        """ """
        self.config = config
        self.logger = logger
        if self.config == None:
            self.config = {}
        if self.logger == None:
            self.logger = logging.getLogger(logger_name)
        #
        self.clear()
        self.configure()

    def clear(self):
        """ """

    def configure(self):
        """ """
        self.summary_columns = [
            {
                "header": "Monitoring night",
                "sourceKey": "monitoringNight",
                "format": "text",
                "columnWidth": 30,
            },
            {
                "header": "Date",
                "sourceKey": "dateLocal",
                "format": "date",
                "columnWidth": 10,
            },
            {
                "header": "Time",
                "sourceKey": "timeLocal",
                "format": "time",
                "columnWidth": 10,
            },
            {
                "header": "Quality",
                "sourceKey": "annotationQuality",
                "format": "text",
                "columnWidth": 15,
            },
            {
                "header": "Tags",
                "sourceKey": "annotationTags",
                "format": "text",
                "columnWidth": 20,
            },
            {
                "header": "Comments",
                "sourceKey": "annotationComments",
                "format": "text",
                "columnWidth": 40,
            },
            {
                "header": "Species",
                # "sourceKey": "",
                "format": "text",
                "columnWidth": 20,
            },
            {
                "header": "Checked",
                # "sourceKey": "",
                "format": "text",
                "columnWidth": 10,
            },
            {
                "header": "Checked by",
                # "sourceKey": "",
                "format": "text",
                "columnWidth": 10,
            },
            {
                "header": "Peak (kHz)",
                "sourceKey": "peakKhz",
                "format": "decimal",
                "columnWidth": 10,
            },
            {
                "header": "Peak (dBFS)",
                "sourceKey": "peakDbfs",
                "format": "decimal",
                "columnWidth": 10,
            },
            {
                "header": "Latitude (DD)",
                "sourceKey": "latitude",
                "format": "decimal_4",
                "columnWidth": 12,
            },
            {
                "header": "Longitude (DD)",
                "sourceKey": "longitude",
                "format": "decimal_4",
                "columnWidth": 12,
            },
            {
                "header": "File name",
                "sourceKey": "recFileName",
                "format": "text",
                "columnWidth": 60,
            },
        ]
        self.detailed_columns = [
            {
                "header": "Monitoring night",
                "sourceKey": "monitoringNight",
                "format": "text",
                "columnWidth": 30,
            },
            {
                "header": "Date",
                "sourceKey": "dateLocal",
                "format": "date",
                "columnWidth": 10,
            },
            {
                "header": "Time",
                "sourceKey": "timeLocal",
                "format": "time",
                "columnWidth": 10,
            },
            {
                "header": "Quality",
                "sourceKey": "annotationQuality",
                "format": "text",
                "columnWidth": 15,
            },
            {
                "header": "Tags",
                "sourceKey": "annotationTags",
                "format": "text",
                "columnWidth": 20,
            },
            {
                "header": "Comments",
                "sourceKey": "annotationComments",
                "format": "text",
                "columnWidth": 40,
            },
            {
                "header": "Peak (kHz)",
                "sourceKey": "peakKhz",
                "format": "decimal",
                "columnWidth": 10,
            },
            {
                "header": "Peak (dBFS)",
                "sourceKey": "peakDbfs",
                "format": "decimal",
                "columnWidth": 10,
            },
            {
                "header": "Latitude (DD)",
                "sourceKey": "latitude",
                "format": "decimal_4",
                "columnWidth": 12,
            },
            {
                "header": "Longitude (DD)",
                "sourceKey": "longitude",
                "format": "decimal_4",
                "columnWidth": 12,
            },
            {
                "header": "File name",
                "sourceKey": "recFileName",
                "format": "text",
                "columnWidth": 60,
            },
            {
                "header": "Device name",
                "sourceKey": "deviceName",
                "format": "text",
                "columnWidth": 40,
            },
            {
                "header": "Detection algorithm",
                "sourceKey": "detectionAlgorithm",
                "format": "text",
                "columnWidth": 15,
            },
            {
                "header": "Limit kHz",
                "sourceKey": "detectionLimitKhz",
                "format": "decimal",
                "columnWidth": 15,
            },
            {
                "header": "Sensitivity dBFS",
                "sourceKey": "detectionSensitivityDbfs",
                "format": "decimal",
                "columnWidth": 15,
            },
            {
                "header": "Datetime UTC",
                "sourceKey": "dateTimeUtc",
                "format": "text",
                "columnWidth": 25,
            },
            {
                "header": "Geo source",
                "sourceKey": "geoSource",
                "format": "text",
                "columnWidth": 15,
            },
            {
                "header": "Scheduler start event",
                "sourceKey": "schedulerStartEvent",
                "format": "text",
                "columnWidth": 15,
            },
            {
                "header": "Scheduler start adjust",
                "sourceKey": "schedulerStartAdjust",
                "format": "decimal",
                "columnWidth": 15,
            },
            {
                "header": "Scheduler stop event",
                "sourceKey": "schedulerStopEvent",
                "format": "text",
                "columnWidth": 15,
            },
            {
                "header": "Scheduler stop adjust",
                "sourceKey": "schedulerStopAdjust",
                "format": "decimal",
                "columnWidth": 15,
            },
            {
                "header": "Sunset local",
                "sourceKey": "sunsetLocal",
                "format": "time",
                "columnWidth": 15,
            },
            {
                "header": "Sunrise local",
                "sourceKey": "sunriseLocal",
                "format": "time",
                "columnWidth": 15,
            },
            {
                "header": "Moon phase",
                "sourceKey": "moonPhase",
                "format": "text",
                "columnWidth": 15,
            },
        ]
        self.wurb_activity_columns = [
            {
                "header": "Datetime UTC",
                "sourceKey": "Datetime UTC",
                "format": "text",
                "columnWidth": 30,
            },
            {
                "header": "Local date",
                "sourceKey": "Local date",
                "format": "date",
                "columnWidth": 10,
            },
            {
                "header": "Local time",
                "sourceKey": "Local time",
                "format": "time",
                "columnWidth": 10,
            },
            {
                "header": "Latitude",
                "sourceKey": "Latitude",
                "format": "decimal_4",
                "columnWidth": 12,
            },
            {
                "header": "Longitude",
                "sourceKey": "Longitude",
                "format": "decimal_4",
                "columnWidth": 12,
            },
            {
                "header": "Recording status",
                "sourceKey": "Recording status",
                "format": "text",
                "columnWidth": 40,
            },
        ]

    def get_report_path(self, source_id, night_id):
        """ """
        report_path = pathlib.Path("Report.xlsx")
        if (source_id) and (night_id):
            source_dir = pathlib.Path(
                wurb_core.record_manager.get_source_dir(source_id)
            )
            night_dir = pathlib.Path(source_dir, night_id)
            if not night_dir.exists():
                night_dir.mkdir(parents=True)
            report_name = night_id + "_report.xlsx"
            report_path = pathlib.Path(night_dir, report_name)

        return report_path

    async def create_report(
        self,
        source_id,
        night_id,
        report_path,
    ):
        """ """
        metadata_rows = []
        # Get files for night.
        for index, rec_file in enumerate(wurb_core.record_manager.get_rec_files(source_id, night_id)):
            # Get metadata for recording.
            metadata = wurb_core.metadata.get_metadata(rec_file)
            metadata_rows.append(metadata)
            if (index % 1000) == 0:
                await asyncio.sleep(0.0)

        # Get wurb avtivity data.
        rec_dir_path = pathlib.Path(wurb_core.record_manager.get_source_dir(source_id))
        night_dir = pathlib.Path(rec_dir_path, night_id).resolve()
        wurb_activity_path = pathlib.Path(
            night_dir,
            "data",
            "wurb_activity.csv",
        )
        wurb_activity_content = []
        if wurb_activity_path.exists():
            with wurb_activity_path.open("r") as file:
                header = None
                for row in file.readlines():
                    row_parts = [x.strip() for x in row.split(",")]
                    if header == None:
                        header = row_parts
                    else:
                        row_dict = dict(zip(header, row_parts))
                        wurb_activity_content.append(row_dict)

        # Create Excel workbook.
        await asyncio.sleep(0.0)
        workbook = xlsxwriter.Workbook(str(report_path))
        self.define_cell_formats(workbook)

        # Summary worksheets.
        summary_worksheet = workbook.add_worksheet("Summary")
        self.add_content(summary_worksheet, metadata_rows, self.summary_columns)
        await asyncio.sleep(0.0)
        # Detailed worksheets.
        detailed_worksheet = workbook.add_worksheet("Detailed")
        self.add_content(detailed_worksheet, metadata_rows, self.detailed_columns)
        await asyncio.sleep(0.0)
        # WURB activity worksheets.
        wurb_activity_worksheet = workbook.add_worksheet("WURB activity")
        self.add_content(
            wurb_activity_worksheet, wurb_activity_content, self.wurb_activity_columns
        )
        # About worksheets.
        about_worksheet = workbook.add_worksheet("About")
        self.add_about_content(about_worksheet)

        # === Done. Close workbook. ===
        workbook.close()

    def add_content(self, worksheet, content_rows, columns):
        """ """
        # Header.
        headers = []
        for column_dict in columns:
            header = column_dict.get("header", "")
            headers.append(header)
        #
        worksheet.write_row(0, 0, headers, self.format_bold)
        # Rows.
        for row_nr, metadata_row in enumerate(content_rows):
            for column_nr, column_dict in enumerate(columns):
                source_key = column_dict.get("sourceKey", "")
                value = metadata_row.get(source_key, "")
                format = column_dict.get("format", "")
                if format == "integer":
                    try:
                        value_int = int(round(float(value), 0))
                        worksheet.write_number(
                            row_nr + 1, column_nr, value_int, self.format_integer
                        )
                    except:
                        worksheet.write_blank(
                            row_nr + 1, column_nr, "", self.format_integer
                        )
                elif format == "decimal":
                    try:
                        value_float = float(value)
                        worksheet.write_number(
                            row_nr + 1, column_nr, value_float, self.format_decimal
                        )
                    except:
                        worksheet.write_blank(
                            row_nr + 1, column_nr, "", self.format_decimal
                        )
                elif format == "decimal_2":
                    try:
                        value_float = float(value)
                        worksheet.write_number(
                            row_nr + 1, column_nr, value_float, self.format_decimal_2
                        )
                    except:
                        worksheet.write_blank(
                            row_nr + 1, column_nr, "", self.format_decimal_2
                        )
                elif format == "decimal_4":
                    try:
                        value_float = float(value)
                        worksheet.write_number(
                            row_nr + 1, column_nr, value_float, self.format_decimal_4
                        )
                    except:
                        worksheet.write_blank(
                            row_nr + 1, column_nr, "", self.format_decimal_4
                        )
                elif format == "decimal_6":
                    try:
                        value_float = float(value)
                        worksheet.write_number(
                            row_nr + 1, column_nr, value_float, self.format_decimal_6
                        )
                    except:
                        worksheet.write_blank(
                            row_nr + 1, column_nr, "", self.format_decimal_6
                        )
                elif format == "date":
                    try:
                        worksheet.write(row_nr + 1, column_nr, value, self.format_date)
                    except:
                        worksheet.write_blank(
                            row_nr + 1, column_nr, "", self.format_date
                        )
                elif format == "time":
                    try:
                        worksheet.write(row_nr + 1, column_nr, value, self.format_time)
                    except:
                        worksheet.write_blank(
                            row_nr + 1, column_nr, "", self.format_time
                        )
                else:
                    value_str = str(value)
                    worksheet.write_string(row_nr + 1, column_nr, value_str)

        # === Adjust column width. ===
        index = 0
        for column_dict in columns:
            width = column_dict.get("columnWidth", 10)
            worksheet.set_column(index, index, int(width))
            index += 1

    def add_about_content(self, worksheet):
        """ """
        # === Sheet: About. ===
        # Header.
        worksheet.write_row(0, 0, ["About"], self.format_bold)
        # Rows.
        readme_text = [
            [""],
            ["CloudedBats WURB-2026, version " + wurb_core.__version__ + "."],
            [""],
            ["This Excel file is a part of the CloudedBats open source project:"],
            ["- https://github.com/cloudedbats"],
            [""],
            ["For developers: "],
            ["Source code to generate the Excel file can be found here:"],
            ["- https://github.com/cloudedbats/wurb_2026"],
            [""],
        ]
        #
        row_nr = 1
        for row in readme_text:
            worksheet.write_row(row_nr, 0, row)
            row_nr += 1

        # === Adjust column width. ===
        worksheet.set_column("A:A", 100)

    def define_cell_formats(self, workbook):
        """ """
        self.format_bold = workbook.add_format({"bold": True})
        #
        self.format_bold_right = workbook.add_format({"bold": True, "align": "right"})
        #
        self.format_date = workbook.add_format()
        self.format_date.set_num_format("yyyy-mm-dd")
        #
        self.format_time = workbook.add_format()
        self.format_time.set_num_format("hh:mm:ss")
        #
        self.format_integer = workbook.add_format()
        self.format_integer.set_num_format("0")
        #
        self.format_decimal = workbook.add_format()
        self.format_decimal.set_num_format("0.0")
        #
        self.format_decimal_2 = workbook.add_format()
        self.format_decimal_2.set_num_format("0.00")
        #
        self.format_decimal_4 = workbook.add_format()
        self.format_decimal_4.set_num_format("0.0000")
        #
        self.format_decimal_6 = workbook.add_format()
        self.format_decimal_6.set_num_format("0.000000")
