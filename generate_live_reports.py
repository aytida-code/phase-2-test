"""Issue live API probes and produce the final verification artifacts."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from docx import Document
from openpyxl import Workbook

BASE_URL = "http://127.0.0.1:8000"
ARTIFACTS = Path("tests-artifacts")


def request(method: str, path: str) -> tuple[int, object]:
    """Make one real HTTP request and return its received status and JSON body."""
    request_object = Request(f"{BASE_URL}{path}", method=method)
    try:
        with urlopen(request_object, timeout=10) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        return error.code, json.loads(error.read().decode("utf-8"))
    except URLError as error:
        return 0, {"error": str(error.reason)}


def result(method: str, endpoint: str, description: str, status: int, passed: bool, reason: str) -> dict[str, object]:
    """Build one report row from a response actually received above."""
    return {
        "Method": method,
        "Endpoint": endpoint,
        "Description": description,
        "Status Code": status if status else "N/A",
        "Pass/Fail": "PASS" if passed else "FAIL",
        "Reason": reason,
    }


def main() -> int:
    """Run all required endpoint checks and write JSON, XLSX, and DOCX artifacts."""
    ARTIFACTS.mkdir(exist_ok=True)
    rows: list[dict[str, object]] = []

    post_status, created = request("POST", "/letters/generate")
    created_ok = (
        post_status == 201
        and isinstance(created, dict)
        and isinstance(created.get("id"), int)
        and created.get("value") in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        and "created_at" in created
    )
    rows.append(
        result(
            "POST",
            "/letters/generate",
            "Generate and persist one random letter",
            post_status,
            created_ok,
            "Received 201 with persisted A-Z record" if created_ok else f"Received body: {created}",
        )
    )

    list_status, letters = request("GET", "/letters")
    persisted = isinstance(created, dict) and any(
        isinstance(item, dict) and item.get("id") == created.get("id") and item.get("value") == created.get("value")
        for item in letters
    ) if isinstance(letters, list) else False
    ordered = isinstance(letters, list) and all(
        (letters[index].get("created_at"), letters[index].get("id"))
        >= (letters[index + 1].get("created_at"), letters[index + 1].get("id"))
        for index in range(len(letters) - 1)
    )
    list_ok = list_status == 200 and persisted and ordered
    rows.append(
        result(
            "GET",
            "/letters",
            "List persisted letters, newest first",
            list_status,
            list_ok,
            "Received ordered array containing the newly persisted record" if list_ok else f"Received body: {letters}",
        )
    )

    missing_status, missing = request("GET", "/letters/999999")
    missing_ok = missing_status == 404 and missing == {"detail": "Letter not found"}
    rows.append(
        result(
            "GET",
            "/letters/999999",
            "Return the specified missing-letter response",
            missing_status,
            missing_ok,
            "Received expected 404 missing-letter response" if missing_ok else f"Received body: {missing}",
        )
    )

    (ARTIFACTS / "test_results.json").write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "API Test Results"
    sheet.append(["#", "Method", "Endpoint", "Description", "Status Code", "Pass/Fail", "Reason"])
    for number, row in enumerate(rows, start=1):
        sheet.append([number, row["Method"], row["Endpoint"], row["Description"], row["Status Code"], row["Pass/Fail"], row["Reason"]])
    workbook.save(ARTIFACTS / "api_test_report.xlsx")

    document = Document()
    document.add_heading("Random Letter Generator — Live Verification", level=1)
    document.add_paragraph("Live verification used PostgreSQL at the configured localhost:5432 DATABASE_URL.")
    document.add_heading("Observed endpoint results", level=2)
    table = document.add_table(rows=1, cols=4)
    table.style = "Table Grid"
    for cell, heading in zip(table.rows[0].cells, ["Method", "Endpoint", "Status", "Result"]):
        cell.text = heading
    for row in rows:
        cells = table.add_row().cells
        for cell, value in zip(cells, [row["Method"], row["Endpoint"], str(row["Status Code"]), row["Pass/Fail"]]):
            cell.text = value
    document.add_paragraph("All rows are recorded from HTTP responses received by this report run.")
    document.save(ARTIFACTS / "project_report.docx")

    return 0 if all(row["Pass/Fail"] == "PASS" for row in rows) else 1


if __name__ == "__main__":
    sys.exit(main())
