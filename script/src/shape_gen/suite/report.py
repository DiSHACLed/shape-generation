from pathlib import Path
import json

from ..config import RESULTS

REPORT_JSON = Path(f'{RESULTS}/report.json') # three-dimensional table (concept, tool, key)

concepts = [ "info", "violations", "time", "memory" ]

def report_add(concept: str, tool: str, key: str, data: str) -> None:
    report = {}
    if REPORT_JSON.exists():
        report = json.loads(REPORT_JSON.read_text())

    report.setdefault(concept, {}).setdefault(tool, {})[key] = data

    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(report, indent=2))

REPORT_EXCEL = Path(f'{RESULTS}/report.xlsx') # three-dimensional table (concept, tool, key)

def excel() -> None:
    import openpyxl

    report = {}
    if REPORT_JSON.exists():
        report = json.loads(REPORT_JSON.read_text())

    wb = openpyxl.Workbook()
    wb.remove(wb.active)  # remove default sheet

    for concept in concepts:
        ws = wb.create_sheet(title=concept)
        concept_data = report.get(concept, {})

        tools = list(concept_data.keys())
        keys = sorted({key for tool_data in concept_data.values() for key in tool_data})

        # header row
        ws.append([""] + tools)

        # data rows
        for key in keys:
            row = [key] + [concept_data.get(tool, {}).get(key, "") for tool in tools]
            ws.append(row)

    REPORT_EXCEL.parent.mkdir(parents=True, exist_ok=True)
    wb.save(REPORT_EXCEL)
