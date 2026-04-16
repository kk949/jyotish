"""
routers/chart.py  — chart generation endpoints
"""
import os, json, tempfile
from typing import Literal, Optional
from fastapi import APIRouter, Body, HTTPException, Query, Response
from models.requests import BirthData, ChartRequest
from services.chart_service import compute_chart
from core.exceptions import InvalidBirthDataError
import jyotichart as chart_lib
import logging
from fastapi.concurrency import run_in_threadpool

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Charts"])

def _fix_color(color: Optional[str]) -> Optional[str]:
    if not color:
        return color

    color = str(color).strip()

    named_colors = [
        "black", "white", "red", "blue", "green", "yellow",
        "gray", "grey", "orange", "pink", "purple", "brown"
    ]
    if color.lower() in named_colors:
        return color

    if not color.startswith("#"):
        return f"#{color}"

    return color


def _sign_num(name: str) -> int:
    signs = {"Aries":1,"Taurus":2,"Gemini":3,"Cancer":4,"Leo":5,"Virgo":6,
             "Libra":7,"Scorpio":8,"Sagittarius":9,"Capricorn":10,"Aquarius":11,"Pisces":12}
    return signs.get(name, 1)

def _sign_name(num: int) -> str:
    names = {1:"Aries",2:"Taurus",3:"Gemini",4:"Cancer",5:"Leo",6:"Virgo",
             7:"Libra",8:"Scorpio",9:"Sagittarius",10:"Capricorn",
             11:"Aquarius",12:"Pisces"}
    return names.get(num, "Aries")

def _house_num(planet_sign, lagna_sign) -> int:
    ps = _sign_num(planet_sign) if isinstance(planet_sign, str) else int(planet_sign)
    ls = _sign_num(lagna_sign)  if isinstance(lagna_sign, str)  else int(lagna_sign)
    h  = (ps - ls) % 12
    return h or 12



def _build_svg(chart_data: dict, request: ChartRequest) -> str:
    div = request.divisional_chart.upper() if request.divisional_chart else "D1"
    if div not in chart_data:
        raise HTTPException(400, f"Divisional chart {div} not found")

    # -----------------------------
    # Create Chart Object
    # -----------------------------
    if request.chart_type == "north":
        c = chart_lib.NorthChart(request.chart_name, request.person_name, IsFullChart=True)
    else:
        c = chart_lib.SouthChart(request.chart_name, request.person_name, IsFullChart=True)

    # -----------------------------
    # Config
    # -----------------------------
    house_colors = request.clr_houses or ["white"] * 12
    house_colors = [_fix_color(c) for c in house_colors]

    cfg = dict(
        aspect=request.aspect,
        clr_background=_fix_color(request.clr_background),
        clr_outbox=_fix_color(request.clr_outbox),
        clr_line=_fix_color(request.clr_line),
        clr_sign=_fix_color(request.clr_sign),
        clr_houses=house_colors
    )

    if request.chart_type == "south":
        cfg["clr_Asc"] = _fix_color(request.clr_Asc)

    c.updatechartcfg(**cfg)

    # -----------------------------
    # Ascendant
    # -----------------------------
    lagna_sign = chart_data[div]["ascendant"]["sign"]
    c.set_ascendantsign(_sign_name(lagna_sign))

    # -----------------------------
    # Planets
    # -----------------------------
    for pname, pd in chart_data[div]["planets"].items():
        if pname in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Rahu","Ketu"]:
            request_planet_colors = request.planet_colors or request.clr_planets
            planet_colour = (
                request_planet_colors.get(pname)
                if isinstance(request_planet_colors, dict)
                else pd.get("color")
            ) or "black"
            planet_colour = _fix_color(planet_colour) or "black"
            c.add_planet(
                planet=pname,
                symbol=pname[:2],
                housenum=_house_num(pd["sign"], lagna_sign),
                retrograde=pd.get("retrograde", False),
                colour=planet_colour,
            )

    # -----------------------------
    # Draw SVG (temp dir) + Read back
    # -----------------------------
    with tempfile.TemporaryDirectory() as temp_dir:
        status = c.draw(temp_dir, "chart")
        if isinstance(status, str) and status.startswith("Input Error"):
            raise HTTPException(500, status)

        svg_path = os.path.join(temp_dir, "chart.svg")
        svg_content = None
        encodings = ["utf-8", "utf-16", "utf-16-le", "utf-16-be", "latin-1"]

        for encoding in encodings:
            try:
                with open(svg_path, "r", encoding=encoding) as f:
                    svg_content = f.read()
                if svg_content and ("<svg" in svg_content.lower()):
                    break
            except Exception:
                continue

        if not svg_content:
            with open(svg_path, "rb") as f:
                return f.read().decode("utf-8", errors="ignore")

    # -----------------------------
    # Final Fixes
    # -----------------------------
    if not svg_content.strip().startswith("<?xml"):
        svg_content = '<?xml version="1.0" encoding="UTF-8"?>\n' + svg_content

    return svg_content.strip()

@router.post("/generate-chart")
async def generate_chart(request: ChartRequest):
    if not request.birth_data and not request.chart_data:
        raise HTTPException(400, "Either birth_data or chart_data must be provided")
    try:
        if request.birth_data:
            bd = request.birth_data
            chart_data = await run_in_threadpool(compute_chart,
                dob=f"{bd.day}/{bd.month}/{bd.year}",
                tob=f"{bd.hour}:{bd.minute}",
                lat=float(bd.latitude), lon=float(bd.longitude),
                tz=float(bd.timezone), name=bd.name,
                gender=bd.gender, place=bd.place, sec=bd.second or "0",
            )
        else:
            chart_data = request.chart_data

        svg = await run_in_threadpool(_build_svg, chart_data, request)
        return Response(content=svg, media_type="image/svg+xml",
                        headers={"Content-Disposition":"inline; filename=chart.svg",
                                 "Cache-Control":"no-cache"})
    except InvalidBirthDataError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        import traceback; raise HTTPException(500, f"{e}\n{traceback.format_exc()}")


@router.post("/chart/{chart_type}")
async def divisional_chart(chart_type: str,
                           payload: dict = Body(default=None),
                           chart_style: Literal["north","south"] = "north",
                           chart_name: str = "Birth Chart", person_name: str = "",
                           aspect: bool = True,
                           clr_background: str = "black", clr_outbox: str = "red",
                           clr_line: str = "yellow", clr_sign: str = "pink",
                           clr_Asc: str = "pink",
                           clr_houses: list = Query(default=None)):
    payload = payload or {}
    raw_birth = payload.get("data") or payload.get("birth_data")
    raw_chart = payload.get("chart_data")

    birth_obj = None
    if isinstance(raw_birth, dict):
        birth_obj = BirthData.model_validate(raw_birth)
    elif isinstance(payload, dict) and raw_chart is None and raw_birth is None:
        # allow sending raw BirthData fields directly as the body
        maybe_birth = payload
        if any(k in maybe_birth for k in ("year", "month", "day", "hour", "minute", "latitude", "longitude")):
            birth_obj = BirthData.model_validate(maybe_birth)

    req = ChartRequest(chart_type=chart_style, chart_name=chart_name,
                       person_name=person_name, birth_data=birth_obj,
                       chart_data=raw_chart, divisional_chart=chart_type.upper(),
                       aspect=aspect, clr_background=clr_background,
                       clr_outbox=clr_outbox, clr_line=clr_line,
                       clr_sign=clr_sign, clr_Asc=clr_Asc, clr_houses=clr_houses)
    return await generate_chart(req)


@router.post("/calculate")
def calculate(data: BirthData):
    try:
        chart_data = compute_chart(
            dob=f"{data.day}/{data.month}/{data.year}",
            tob=f"{data.hour}:{data.minute}",
            lat=float(data.latitude), lon=float(data.longitude),
            tz=float(data.timezone), name=data.name,
            gender=data.gender, place=data.place, sec=data.second or "0",
        )
        return chart_data
    except InvalidBirthDataError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        import traceback; raise HTTPException(500, f"{e}\n{traceback.format_exc()}")
