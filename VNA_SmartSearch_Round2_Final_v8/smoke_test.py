#!/usr/bin/env python3
"""Fast pre-pitch checks. Uses only the Python standard library."""

from __future__ import annotations

import importlib.util
import py_compile
import shutil
import subprocess
import sys
import types
from pathlib import Path


ROOT = Path(__file__).resolve().parent
WEB = ROOT / "web"
MCP = ROOT / "mcp_server"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load_server_without_sdk():
    """Load tool functions with a tiny decorator stub; no MCP install required."""

    class MCPStub:
        def __init__(self, *_args, **_kwargs):
            pass

        def tool(self, *args, **kwargs):
            return lambda fn: fn

        def resource(self, *args, **kwargs):
            return lambda fn: fn

        def run(self, *args, **kwargs):
            return None

    mcp_module = types.ModuleType("mcp")
    mcp_server_module = types.ModuleType("mcp.server")
    mcp_server_module.MCPServer = MCPStub
    sys.modules["mcp"] = mcp_module
    sys.modules["mcp.server"] = mcp_server_module
    sys.path.insert(0, str(MCP))

    spec = importlib.util.spec_from_file_location("vna_demo_server", MCP / "server.py")
    require(spec is not None and spec.loader is not None, "Cannot load MCP server")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    expected = [
        ROOT / "run.py",
        WEB / "index.html",
        WEB / "index-ai.html",
        WEB / "proxy.py",
        MCP / "server.py",
        MCP / "data.py",
        MCP / "requirements.txt",
    ]
    for path in expected:
        require(path.is_file(), f"Missing file: {path.relative_to(ROOT)}")

    for path in [ROOT / "run.py", WEB / "proxy.py", MCP / "server.py", MCP / "data.py"]:
        py_compile.compile(str(path), doraise=True)

    server_source = (MCP / "server.py").read_text(encoding="utf-8")
    require(server_source.count("@mcp.tool") == 10, "MCP tool count is not exactly 10")

    for page in [WEB / "index.html", WEB / "index-ai.html"]:
        html = page.read_text(encoding="utf-8")
        require("</html>" in html.lower(), f"Incomplete HTML: {page.name}")
        require("id=\"input\"" in html and "id=\"send\"" in html, f"Chat controls missing: {page.name}")
        require("route_unavailable" in html, f"Fail-closed route handling missing: {page.name}")
        require("subtotal_aud||0" not in html, f"Unsafe missing-fare fallback remains: {page.name}")

    stable_html = (WEB / "index.html").read_text(encoding="utf-8")
    for marker in ["id=\"langEn\"", "id=\"langVi\"", "id=\"customerMode\"", "id=\"technicalMode\"", "id=\"restoreChat\"", "id=\"maximizeChat\"", "continueVna", "partyTotal", "tpNoSmartFee", "tpHandoff", "missingQuestion", "foldText", "setChatMaximized"]:
        require(marker in stable_html, f"Stable UX feature missing: {marker}")
    for unsafe_claim in ["UAVS Hackathon 2026 · Team Four Pho", "Live from Vietnam Airlines", "Price locked"]:
        require(unsafe_claim not in stable_html, f"Unsupported customer-facing claim remains: {unsafe_claim}")

    server = load_server_without_sdk()
    search = server.search_flights(
        origin="SYD", destination="HAN", date_from="2027-02-01",
        date_to="2027-02-10", passengers=2,
    )
    require(search["count"] > 0, "search_flights returned no fixtures")
    require(all(item["date"].startswith("2027-") for item in search["results"]), "MCP is not using 2027 fixtures")
    flight_id = search["results"][0]["id"]
    require("fare_breakdown" in server.get_fare_details(flight_id), "get_fare_details failed")
    handoff = server.create_booking_intent(flight_id, 2)
    require(handoff.get("handoff_url") == "https://www.vietnamairlines.com/au/en/home", "unsafe or fake handoff URL")
    require("member_price_aud" in server.get_lotusmiles_price(flight_id), "get_lotusmiles_price failed")
    require("route" in server.suggest_flexible_dates("SYD", "HAN", "2027-02-05"), "suggest_flexible_dates failed")
    require("seats_left" in server.check_availability(flight_id, 2), "check_availability failed")
    require("add_ons" in server.get_baggage_options(flight_id), "get_baggage_options failed")
    require("bundle_total_aud" in server.compare_family_bundle(flight_id, 4), "compare_family_bundle failed")
    require("weekly_frequency" in server.get_route_info("SYD", "HAN"), "get_route_info failed")
    multi = server.plan_multi_origin_trip(
        [{"origin": "SYD", "passengers": 2}, {"origin": "MEL", "passengers": 2}],
        "HAN",
        "2027-02-01",
        "2027-02-10",
        4000,
    )
    require(multi.get("total_passengers") == 4, "plan_multi_origin_trip failed")

    unavailable = server.plan_multi_origin_trip(
        [{"origin": "BNE", "passengers": 2}, {"origin": "PER", "passengers": 2}],
        "HAN",
        "2027-02-01",
        "2027-02-10",
        4000,
    )
    require(unavailable.get("error") == "route_unavailable", "Missing BNE→HAN route was not rejected")
    require(
        any(route["origin"] == "BNE" for route in unavailable.get("unavailable_routes", [])),
        "Unavailable BNE→HAN route was not identified",
    )
    require(
        unavailable.get("grand_total_aud") is None
        and unavailable.get("within_budget") is None
        and unavailable.get("budget_headroom_aud") is None,
        "An incomplete plan must not have a total or budget verdict",
    )

    mel_dad = server.plan_multi_origin_trip(
        [{"origin": "SYD", "passengers": 1}, {"origin": "MEL", "passengers": 1}],
        "DAD",
        "2027-02-01",
        "2027-02-10",
        2500,
    )
    require(mel_dad.get("error") == "route_unavailable", "Missing MEL→DAD route was not rejected")

    duplicate = server.plan_multi_origin_trip(
        [{"origin": "SYD", "passengers": 2}, {"origin": "SYD", "passengers": 2}],
        "HAN",
        "2027-02-01",
        "2027-02-10",
        5000,
    )
    require(
        duplicate.get("total_passengers") == 4
        and len(duplicate.get("legs", [])) == 1
        and duplicate["legs"][0]["passengers"] == 4,
        "Duplicate origins were not merged into one four-passenger leg",
    )

    three_origins = server.plan_multi_origin_trip(
        [
            {"origin": "SYD", "passengers": 1},
            {"origin": "MEL", "passengers": 1},
            {"origin": "PER", "passengers": 1},
        ],
        "HAN",
        "2027-02-01",
        "2027-02-10",
        4000,
    )
    require(
        three_origins.get("total_passengers") == 3 and len(three_origins.get("legs", [])) == 3,
        "Three-origin planning regressed",
    )

    node = shutil.which("node")
    if node:
        subprocess.run([node, str(ROOT / "web_logic_test.js")], cwd=ROOT, check=True)

    print("PASS: project structure")
    print("PASS: Python syntax")
    print("PASS: web entry points")
    print("PASS: bilingual customer UX and prototype disclosures")
    print("PASS: all 10 MCP tool functions")
    print("PASS: fail-closed routes, duplicate origins and three-origin plans")
    print("PASS: Tết 2027 web/MCP fixture boundary and safe VNA handoff")
    if not node:
        print("SKIP: JavaScript logic test (Node.js not installed)")
    print("READY: run `python run.py` for the stable demo")


if __name__ == "__main__":
    main()
