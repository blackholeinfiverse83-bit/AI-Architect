"""
Room-Based Geometry Generator — Phase 2
=========================================
Each room = enclosed volume (floor + ceiling + 4 thick walls).
Walls have real thickness (WALL_T = 0.2 m).
Adjacent rooms share a wall with exactly one door gap.
Rooms are positioned in a grid layout with wall-thickness separation.

Rules enforced:
  - Bedroom ≠ Hall ≠ Kitchen (different dimensions, visually separable)
  - Rooms positioned by row-based layout with GAP = WALL_T between them
  - Adjacency from spec_json["adjacency"] drives door placement
  - No dummy mesh — raises ValueError if rooms list is empty

Pipeline:
  spec["rooms"] + spec["adjacency"]
      → _layout_rooms()        — assign (x, y, w, l, h) per room
      → _compute_doors()       — door flags from adjacency + spatial proximity
      → build_room_mesh()      — floor + ceiling + 4 thick walls per room
      → pack_glb_multi_mesh()  — one GLB node per room
"""

import json
import logging
import math
import struct
from typing import Any, Dict, List, Set, Tuple

logger = logging.getLogger(__name__)

# ── Constants ─────────────────────────────────────────────────────────────────
WALL_T = 0.25  # wall thickness in metres (visible at normal scale)
DOOR_W = 0.9  # door opening width in metres
DOOR_H = 2.1  # door opening height in metres
GAP = 0.0  # rooms share walls — no gap between room origins

Vertex = Tuple[float, float, float]
Triangle = Tuple[int, int, int]


# ── Room dimension defaults (w, l, h) in metres ──────────────────────────────
_ROOM_DEFAULTS: Dict[str, Tuple[float, float, float]] = {
    "master_bedroom": (4.2, 4.8, 2.8),
    "bedroom": (3.6, 4.2, 2.7),
    "bedroom_2": (3.2, 3.8, 2.7),
    "bedroom_3": (3.0, 3.5, 2.7),
    "bedroom_4": (3.0, 3.5, 2.7),
    "bedroom_5": (3.0, 3.5, 2.7),
    "hall": (5.0, 6.0, 3.0),
    "living": (5.0, 6.0, 3.0),
    "living_room": (5.0, 6.0, 3.0),
    "kitchen": (3.0, 4.0, 2.7),
    "dining": (3.6, 4.2, 2.7),
    "dining_room": (3.6, 4.2, 2.7),
    "bathroom": (2.0, 2.5, 2.4),
    "bathroom_2": (1.8, 2.2, 2.4),
    "bathroom_3": (1.8, 2.2, 2.4),
    "bathroom_4": (1.8, 2.2, 2.4),
    "master_bathroom": (2.5, 3.0, 2.4),
    "common_bathroom": (1.8, 2.2, 2.4),
    "toilet": (1.5, 2.0, 2.4),
    "balcony": (1.5, 3.5, 2.4),
    "balcony_1": (1.5, 4.0, 2.4),
    "balcony_2": (1.2, 3.0, 2.4),
    "balcony_3": (1.2, 3.0, 2.4),
    "study": (3.0, 3.5, 2.7),
    "pooja_room": (2.0, 2.5, 2.7),
    "garage": (6.0, 6.0, 2.5),
    "terrace": (8.0, 10.0, 0.3),
    "home_theatre": (5.0, 6.0, 2.8),
    "jacuzzi_deck": (5.0, 6.0, 2.4),
    "passage": (1.5, 3.5, 2.7),
    "corridor": (1.5, 4.5, 2.7),
    "store": (2.0, 2.0, 2.4),
    "utility": (2.0, 2.5, 2.4),
    "garden": (8.0, 10.0, 0.3),
}


def _resolve_room_dims(
    room_name: str,
    spec_room_dimensions: Dict[str, Any],
    floor_height: float,
) -> Tuple[float, float, float]:
    """Resolve (w, l, h) for a room: spec overrides > defaults > fallback."""
    # Build lookup candidates: exact name, then strip trailing _N suffix, then base type
    parts = room_name.rsplit("_", 1)
    numeric_suffix = len(parts) == 2 and parts[1].isdigit()
    base_no_num = parts[0] if numeric_suffix else room_name
    # Also try stripping the number to get generic base (e.g. balcony_1 -> balcony)
    base_type = base_no_num.rsplit("_", 1)[0] if "_" in base_no_num else base_no_num

    candidates = [room_name, base_no_num, base_type]

    # 1. Try spec room_dimensions (exact match or suffix-stripped)
    for key in candidates:
        rd = spec_room_dimensions.get(key)
        if rd and isinstance(rd, dict):
            w = float(rd.get("width_m", rd.get("width", 0)) or 0)
            l = float(rd.get("length_m", rd.get("length", 0)) or 0)
            h = float(rd.get("height_m", rd.get("height", floor_height)) or floor_height)
            if w > 0 and l > 0:
                return w, l, max(h, 2.2)

    # 2. Fall back to hardcoded defaults
    for key in candidates:
        if key in _ROOM_DEFAULTS:
            dw, dl, dh = _ROOM_DEFAULTS[key]
            return dw, dl, floor_height if floor_height != 2.7 else dh

    return 3.5, 4.0, floor_height


# ── Layout engine ─────────────────────────────────────────────────────────────────────────────────────────────────────────


def _layout_rooms(
    rooms: List[str],
    spec_room_dimensions: Dict[str, Any],
    total_width: float,
    floor_height: float,
    adjacency: Dict[str, Any] = None,
) -> List[Tuple[str, float, float, float, float, float]]:
    """
    Adjacency-driven grid layout:
    1. Resolve each room's (w, l, h).
    2. Place rooms in rows using the adjacency graph to ensure
       adjacent rooms always share an exact edge — zero gap.
    3. Row boundary is snapped to the tallest room in that row
       so the next row always starts flush.

    Key fix over old approach: cursor_y advances by the ACTUAL max
    length of placed rooms in the current row, not by the max_l of
    rooms yet to be assigned — so no row creates a vertical gap.
    """
    if not rooms:
        return []

    adj = adjacency or {}

    # Per-room dimensions
    dims: Dict[str, Tuple[float, float, float]] = {
        r: _resolve_room_dims(r, spec_room_dimensions, floor_height) for r in rooms
    }

    def _base(name: str) -> str:
        parts = name.rsplit("_", 1)
        return parts[0] if len(parts) == 2 and parts[1].isdigit() else name

    # Build bidirectional adjacency
    adj_map: Dict[str, List[str]] = {r: [] for r in rooms}
    for ra, neighbours in adj.items():
        if not isinstance(neighbours, list) or ra not in adj_map:
            continue
        for rb in neighbours:
            if rb not in adj_map:
                continue
            if rb not in adj_map[ra]:
                adj_map[ra].append(rb)
            if ra not in adj_map[rb]:
                adj_map[rb].append(ra)

    # --- classify rooms into layout bands ---
    # band 0 (south): bedrooms
    # band 1 (middle): hall, living, dining, kitchen
    # band 2 (north): bathrooms, balconies, small service rooms
    _SOUTH = {"master_bedroom", "bedroom", "bedroom_2", "bedroom_3", "bedroom_4", "bedroom_5", "study", "garage"}
    _NORTH = {
        "master_bathroom",
        "bathroom",
        "bathroom_2",
        "bathroom_3",
        "bathroom_4",
        "common_bathroom",
        "toilet",
        "balcony",
        "balcony_1",
        "balcony_2",
        "balcony_3",
        "store",
        "utility",
        "passage",
        "corridor",
        "pooja_room",
    }

    def _band(name: str) -> int:
        b = _base(name)
        if b in _SOUTH:
            return 0
        if b in _NORTH:
            return 2
        return 1  # hall, kitchen, dining, living etc.

    band0 = [r for r in rooms if _band(r) == 0]
    band1 = [r for r in rooms if _band(r) == 1]
    band2 = [r for r in rooms if _band(r) == 2]

    # order: south band left-to-right, middle band, north band
    ordered = band0 + band1 + band2
    # add any rooms not classified
    ordered += [r for r in rooms if r not in ordered]

    placed: Dict[str, Tuple[float, float, float, float, float]] = {}

    def _place_row(row_rooms: List[str], start_y: float) -> float:
        """Place a list of rooms left-to-right at start_y.
        All rooms are stretched to the same length (max l in row)
        so the next row starts flush with no gaps.
        Returns y of next row."""
        if not row_rooms:
            return start_y
        # Find max length in this row
        max_l = max(dims[r][1] for r in row_rooms if r not in placed)
        if max_l == 0:
            return start_y
        cx = 0.0
        for r in row_rooms:
            if r in placed:
                continue
            w, l, h = dims[r]
            # Stretch l to max_l so all rooms in row share the same south/north edge
            placed[r] = (cx, start_y, w, max_l, h)
            cx += w
        return start_y + max_l

    # Place south band at y=0
    y = _place_row(band0, 0.0)
    # Place middle band flush at y = max_l of south band
    y = _place_row(band1, y)
    # Place north band flush at y = max_l of middle band
    _place_row(band2, y)

    # Any leftover rooms
    remaining = [r for r in rooms if r not in placed]
    if remaining:
        max_y = max(py + pl for _, px, py, pw, pl, ph in [(r, *placed[r]) for r in placed]) if placed else 0.0
        _place_row(remaining, max_y)

    return [(r, *placed[r]) for r in rooms if r in placed]


# ── Door placement ────────────────────────────────────────────────────────────


def _compute_doors(
    layout: List[Tuple[str, float, float, float, float, float]],
    adjacency_spec: Dict[str, Any],
) -> Dict[int, Dict[str, bool]]:
    """
    Determine which walls get a door gap.

    Two sources:
      1. spec_json["adjacency"] — explicit adjacency pairs from BHK definition
      2. Spatial proximity — rooms that are physically touching

    Returns {room_idx: {south, north, west, east}} booleans.
    """
    n = len(layout)
    doors: Dict[int, Dict[str, bool]] = {
        i: {"south": False, "north": False, "west": False, "east": False} for i in range(n)
    }

    # Build name → index map
    name_to_idx: Dict[str, int] = {}
    for i, (name, *_) in enumerate(layout):
        base = name.rsplit("_", 1)[0] if name.rsplit("_", 1)[-1].isdigit() else name
        name_to_idx[name] = i
        name_to_idx[base] = i

    # 1. Spatial adjacency — rooms sharing an edge (touching within 0.05 m)
    tol = 0.05
    for i, (_, xi, yi, wi, li, _hi) in enumerate(layout):
        for j, (_, xj, yj, wj, lj, _hj) in enumerate(layout):
            if i >= j:
                continue
            # j is east of i?
            if abs((xi + wi) - xj) < tol and yi < yj + lj - tol and yi + li > yj + tol:
                doors[i]["east"] = True
                doors[j]["west"] = True
            # j is north of i?
            if abs((yi + li) - yj) < tol and xi < xj + wj - tol and xi + wi > xj + tol:
                doors[i]["north"] = True
                doors[j]["south"] = True

    # 2. Explicit adjacency from spec — add doors even if not spatially touching
    # adjacency_spec can be {"bedroom": ["hall"], "kitchen": ["dining"]} etc.
    if isinstance(adjacency_spec, dict):
        for room_a, neighbours in adjacency_spec.items():
            if not isinstance(neighbours, list):
                continue
            idx_a = name_to_idx.get(room_a)
            if idx_a is None:
                continue
            for room_b in neighbours:
                idx_b = name_to_idx.get(room_b)
                if idx_b is None:
                    continue
                # Determine relative direction and add door on the closer wall
                _, xa, ya, wa, la, _ = layout[idx_a]
                _, xb, yb, wb, lb, _ = layout[idx_b]
                cx_a, cy_a = xa + wa / 2, ya + la / 2
                cx_b, cy_b = xb + wb / 2, yb + lb / 2
                dx, dy = cx_b - cx_a, cy_b - cy_a
                if abs(dx) >= abs(dy):
                    if dx > 0:
                        doors[idx_a]["east"] = True
                        doors[idx_b]["west"] = True
                    else:
                        doors[idx_a]["west"] = True
                        doors[idx_b]["east"] = True
                else:
                    if dy > 0:
                        doors[idx_a]["north"] = True
                        doors[idx_b]["south"] = True
                    else:
                        doors[idx_a]["south"] = True
                        doors[idx_b]["north"] = True

    return doors


# ── Mesh container ────────────────────────────────────────────────────────────


class Mesh:
    def __init__(self, name: str):
        self.name = name
        self.verts: List[Vertex] = []
        self.tris: List[Triangle] = []

    def add_quad(self, a: Vertex, b: Vertex, c: Vertex, d: Vertex) -> None:
        base = len(self.verts)
        self.verts += [a, b, c, d]
        self.tris += [(base, base + 1, base + 2), (base, base + 2, base + 3)]

    def add_thick_wall(
        self,
        x0: float,
        y0: float,
        x1: float,
        y1: float,
        z_bot: float,
        z_top: float,
        normal_out: Tuple[float, float],
        door: bool = False,
    ) -> None:
        """
        Build a wall panel (x0,y0)→(x1,y1) with thickness WALL_T.
        normal_out points away from the room interior.
        door=True cuts a centred door gap.
        """
        nx, ny = normal_out
        tx, ty = WALL_T * nx, WALL_T * ny

        ix0, iy0 = x0, y0
        ix1, iy1 = x1, y1
        ox0, oy0 = x0 + tx, y0 + ty
        ox1, oy1 = x1 + tx, y1 + ty

        if not door:
            self._wall_segment(ix0, iy0, ix1, iy1, ox0, oy0, ox1, oy1, z_bot, z_top)
        else:
            length = math.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2)
            if length < 1e-6:
                return
            ux = (x1 - x0) / length
            uy = (y1 - y0) / length

            door_start = max(0.0, (length - DOOR_W) / 2)
            door_end = door_start + DOOR_W

            # Left segment
            if door_start > 0.01:
                ax0, ay0 = x0, y0
                ax1, ay1 = x0 + ux * door_start, y0 + uy * door_start
                self._wall_segment(ax0, ay0, ax1, ay1, ax0 + tx, ay0 + ty, ax1 + tx, ay1 + ty, z_bot, z_top)

            # Above-door segment
            if DOOR_H < z_top - z_bot:
                bx0 = x0 + ux * door_start
                by0 = y0 + uy * door_start
                bx1 = x0 + ux * door_end
                by1 = y0 + uy * door_end
                self._wall_segment(bx0, by0, bx1, by1, bx0 + tx, by0 + ty, bx1 + tx, by1 + ty, z_bot + DOOR_H, z_top)

            # Right segment
            if door_end < length - 0.01:
                cx0 = x0 + ux * door_end
                cy0 = y0 + uy * door_end
                self._wall_segment(cx0, cy0, x1, y1, cx0 + tx, cy0 + ty, ox1, oy1, z_bot, z_top)

    def _wall_segment(
        self,
        ix0: float,
        iy0: float,
        ix1: float,
        iy1: float,
        ox0: float,
        oy0: float,
        ox1: float,
        oy1: float,
        z_bot: float,
        z_top: float,
    ) -> None:
        # inner face
        self.add_quad((ix0, iy0, z_bot), (ix1, iy1, z_bot), (ix1, iy1, z_top), (ix0, iy0, z_top))
        # outer face (reversed winding)
        self.add_quad((ox1, oy1, z_bot), (ox0, oy0, z_bot), (ox0, oy0, z_top), (ox1, oy1, z_top))
        # top cap
        self.add_quad((ix0, iy0, z_top), (ix1, iy1, z_top), (ox1, oy1, z_top), (ox0, oy0, z_top))
        # left cap
        self.add_quad((ox0, oy0, z_bot), (ix0, iy0, z_bot), (ix0, iy0, z_top), (ox0, oy0, z_top))
        # right cap
        self.add_quad((ix1, iy1, z_bot), (ox1, oy1, z_bot), (ox1, oy1, z_top), (ix1, iy1, z_top))


# ── Furniture helpers ────────────────────────────────────────────────────────


def _add_box(m: Mesh, x: float, y: float, z: float, bw: float, bl: float, bh: float) -> None:
    x1, y1, z1 = x + bw, y + bl, z + bh
    m.add_quad((x, y, z), (x1, y, z), (x1, y1, z), (x, y1, z))
    m.add_quad((x, y1, z1), (x1, y1, z1), (x1, y, z1), (x, y, z1))
    m.add_quad((x, y, z), (x, y, z1), (x1, y, z1), (x1, y, z))
    m.add_quad((x1, y1, z), (x1, y1, z1), (x, y1, z1), (x, y1, z))
    m.add_quad((x, y1, z), (x, y1, z1), (x, y, z1), (x, y, z))
    m.add_quad((x1, y, z), (x1, y, z1), (x1, y1, z1), (x1, y1, z))


def _room_base_type(name: str) -> str:
    key = name.split("_s")[0]
    parts = key.rsplit("_", 1)
    return parts[0] if len(parts) == 2 and parts[1].isdigit() else key


def _add_furniture(m: Mesh, rt: str, x: float, y: float, w: float, l: float, z: float) -> None:
    p = WALL_T + 0.1  # inner padding from wall face

    # ── Bedrooms ──────────────────────────────────────────────────────────────
    if rt in ("master_bedroom", "bedroom", "bedroom_2", "bedroom_3", "bedroom_4", "bedroom_5"):
        # Bed against north wall, centred
        bw, bl = min(1.6, w - 2 * p), min(2.0, l * 0.5)
        bx, by = x + (w - bw) / 2, y + l - p - bl
        _add_box(m, bx, by, z, bw, bl, 0.5)  # mattress
        _add_box(m, bx, by + bl - 0.15, z + 0.5, bw, 0.1, 0.55)  # headboard
        _add_box(m, bx + 0.1, by + bl - 0.35, z + 0.5, 0.5, 0.3, 0.12)  # pillow
        # Bedside table
        if bx - x - p > 0.4:
            _add_box(m, bx - p - 0.45, by + bl - 0.5, z, 0.45, 0.45, 0.55)
        # Wardrobe against west wall
        _add_box(m, x + p, y + p, z, min(1.2, w * 0.3), 0.6, 2.0)

    # ── Living / Hall ─────────────────────────────────────────────────────────
    elif rt in ("hall", "living", "living_room"):
        sw = min(2.2, w - 2 * p)
        # 3-seater sofa against south wall
        _add_box(m, x + (w - sw) / 2, y + p, z, sw, 0.9, 0.85)
        # Coffee table in centre
        _add_box(m, x + (w - 1.0) / 2, y + l * 0.38, z, 1.0, 0.55, 0.42)
        # TV unit against north wall
        tw = min(1.6, w - 2 * p)
        _add_box(m, x + (w - tw) / 2, y + l - p - 0.45, z, tw, 0.45, 0.5)
        # TV panel on top
        _add_box(m, x + (w - tw * 0.7) / 2, y + l - p - 0.42, z + 0.5, tw * 0.7, 0.08, 0.55)
        # Side chair
        _add_box(m, x + p, y + l * 0.35, z, 0.55, 0.55, 0.9)

    # ── Kitchen ───────────────────────────────────────────────────────────────
    elif rt == "kitchen":
        # Base counter along south wall
        _add_box(m, x + p, y + p, z, w - 2 * p, 0.6, 0.9)
        # Side counter along west wall
        _add_box(m, x + p, y + p + 0.6, z, 0.6, min(l * 0.4, l - 2 * p - 0.6), 0.9)
        # Overhead cabinet above base counter
        _add_box(m, x + p, y + p, z + 1.4, w - 2 * p, 0.35, 0.65)
        # Refrigerator box in corner
        _add_box(m, x + w - p - 0.7, y + p, z, 0.7, 0.7, 1.8)

    # ── Dining ────────────────────────────────────────────────────────────────
    elif rt in ("dining", "dining_room"):
        tw, tl = min(1.4, w - 2 * p), min(0.85, l * 0.4)
        tx, ty = x + (w - tw) / 2, y + (l - tl) / 2
        _add_box(m, tx, ty, z, tw, tl, 0.75)  # table
        # 4 chairs around table
        for cx, cy in [
            (tx - 0.55, ty + (tl - 0.45) / 2),
            (tx + tw + 0.1, ty + (tl - 0.45) / 2),
            (tx + (tw - 0.45) / 2, ty - 0.55),
            (tx + (tw - 0.45) / 2, ty + tl + 0.1),
        ]:
            _add_box(m, cx, cy, z, 0.45, 0.45, 0.9)

    # ── Bathrooms ─────────────────────────────────────────────────────────────
    elif rt in ("bathroom", "bathroom_2", "bathroom_3", "bathroom_4", "master_bathroom", "common_bathroom", "toilet"):
        # Toilet in near corner
        _add_box(m, x + p, y + p, z, 0.38, 0.65, 0.42)  # bowl
        _add_box(m, x + p, y + p + 0.45, z + 0.3, 0.38, 0.2, 0.12)  # cistern
        # Sink/vanity
        _add_box(m, x + p, y + l - p - 0.45, z, 0.5, 0.45, 0.85)
        # Shower tray in far corner (only if room wide enough)
        if w > 1.5 and l > 2.0:
            _add_box(m, x + w - p - 0.9, y + p, z, 0.9, 0.9, 0.05)

    # ── Study / Home Office ───────────────────────────────────────────────────
    elif rt == "study":
        dw = min(1.4, w - 2 * p)
        # Desk against north wall
        _add_box(m, x + (w - dw) / 2, y + l - p - 0.65, z, dw, 0.65, 0.75)
        # Monitor on desk
        _add_box(m, x + (w - 0.5) / 2, y + l - p - 0.6, z + 0.75, 0.5, 0.08, 0.4)
        # Chair in front of desk
        _add_box(m, x + (w - 0.55) / 2, y + l - p - 1.3, z, 0.55, 0.55, 0.9)
        # Bookshelf against east wall
        _add_box(m, x + w - p - 0.3, y + p, z, 0.3, min(1.2, l - 2 * p), 1.9)

    # ── Pooja Room ────────────────────────────────────────────────────────────
    elif rt == "pooja_room":
        pw = min(0.9, w - 2 * p)
        # Altar shelf against north wall
        _add_box(m, x + (w - pw) / 2, y + l - p - 0.4, z + 0.8, pw, 0.3, 0.05)
        # Platform/mandir base
        _add_box(m, x + (w - pw) / 2, y + l - p - 0.4, z, pw, 0.4, 0.8)
        # Prayer mat (flat)
        mw = min(0.6, w - 2 * p)
        _add_box(m, x + (w - mw) / 2, y + p, z, mw, 0.9, 0.03)

    # ── Balconies ─────────────────────────────────────────────────────────────
    elif rt in ("balcony", "balcony_1", "balcony_2", "balcony_3"):
        # Small bistro table
        _add_box(m, x + (w - 0.6) / 2, y + (l - 0.6) / 2, z, 0.6, 0.6, 0.72)
        # Two chairs on either side
        if w > 1.0:
            _add_box(m, x + p, y + (l - 0.45) / 2, z, 0.45, 0.45, 0.85)
            _add_box(m, x + w - p - 0.45, y + (l - 0.45) / 2, z, 0.45, 0.45, 0.85)
        # Planter box along railing
        _add_box(m, x + p, y + l - p - 0.25, z, w - 2 * p, 0.25, 0.35)

    # ── Garage ────────────────────────────────────────────────────────────────
    elif rt == "garage":
        # Car silhouette
        cw, cl = min(2.0, w - 2 * p), min(4.5, l - 2 * p)
        _add_box(m, x + (w - cw) / 2, y + p, z, cw, cl, 1.5)
        # Workbench along side wall
        _add_box(m, x + p, y + p, z, 0.6, min(1.5, l * 0.3), 0.9)

    # ── Home Theatre ─────────────────────────────────────────────────────────
    elif rt == "home_theatre":
        # Screen wall
        sw = min(w - 2 * p, 3.0)
        _add_box(m, x + (w - sw) / 2, y + l - p - 0.15, z + 0.6, sw, 0.1, 1.4)
        # Rows of seats (2 rows × 3 seats)
        seat_w = min((w - 2 * p) / 3, 0.6)
        for row, ry in enumerate([y + l * 0.35, y + l * 0.6]):
            for col in range(3):
                sx = x + p + col * (seat_w + 0.1)
                _add_box(m, sx, ry, z, seat_w, 0.55, 0.9)

    # ── Jacuzzi Deck ─────────────────────────────────────────────────────────
    elif rt == "jacuzzi_deck":
        # Jacuzzi tub centred
        jw, jl = min(1.8, w - 2 * p), min(1.8, l * 0.45)
        _add_box(m, x + (w - jw) / 2, y + (l - jl) / 2, z, jw, jl, 0.65)
        # Deck lounger
        _add_box(m, x + p, y + p, z, 0.7, min(1.9, l - 2 * p), 0.35)

    # ── Terrace ───────────────────────────────────────────────────────────────
    elif rt == "terrace":
        # Outdoor seating set
        _add_box(m, x + p, y + p, z, min(2.0, w * 0.35), 0.9, 0.85)  # sofa
        _add_box(m, x + p + 0.5, y + p + 1.1, z, 1.0, 0.6, 0.42)  # table
        # Planter boxes along perimeter
        _add_box(m, x + p, y + l - p - 0.3, z, w - 2 * p, 0.3, 0.4)
        _add_box(m, x + w - p - 0.3, y + p, z, 0.3, l - 2 * p, 0.4)

    # ── Garden ────────────────────────────────────────────────────────────────
    elif rt == "garden":
        # Lawn area (flat green slab)
        lw, ll = max(w - 2 * p - 1.0, 1.0), max(l - 2 * p - 1.0, 1.0)
        _add_box(m, x + (w - lw) / 2, y + (l - ll) / 2, z, lw, ll, 0.05)
        # Garden bench
        _add_box(m, x + p, y + l - p - 0.5, z, min(1.4, w * 0.3), 0.5, 0.45)
        # Tree stumps (2 planters)
        _add_box(m, x + p + 0.5, y + p + 0.5, z, 0.5, 0.5, 0.4)
        _add_box(m, x + w - p - 1.0, y + p + 0.5, z, 0.5, 0.5, 0.4)

    # ── Store / Utility ───────────────────────────────────────────────────────
    elif rt in ("store", "utility"):
        # Shelving units along walls
        _add_box(m, x + p, y + p, z, 0.4, min(l - 2 * p, 1.5), 1.8)
        _add_box(m, x + w - p - 0.4, y + p, z, 0.4, min(l - 2 * p, 1.5), 1.8)

    # ── Passage / Corridor ────────────────────────────────────────────────────
    elif rt in ("passage", "corridor"):
        # Slim console table against wall
        _add_box(m, x + p, y + (l - 0.8) / 2, z, min(0.3, w * 0.25), 0.8, 0.85)


def _compute_shared_walls(
    layout: List[Tuple[str, float, float, float, float, float]],
) -> Dict[int, Dict[str, bool]]:
    """
    When two rooms share an edge, only ONE of them should build that wall
    to avoid double-wall gaps. Rule: the room with the higher index suppresses
    its shared wall (the lower-index room already built it).
    """
    n = len(layout)
    shared: Dict[int, Dict[str, bool]] = {
        i: {"south": False, "north": False, "west": False, "east": False} for i in range(n)
    }
    tol = 0.05
    for i, (_, xi, yi, wi, li, _hi) in enumerate(layout):
        for j, (_, xj, yj, wj, lj, _hj) in enumerate(layout):
            if i >= j:
                continue
            # j is directly east of i → j suppresses its west wall
            if abs((xi + wi) - xj) < tol and yi < yj + lj - tol and yi + li > yj + tol:
                shared[j]["west"] = True
            # j is directly north of i → j suppresses its south wall
            if abs((yi + li) - yj) < tol and xi < xj + wj - tol and xi + wi > xj + tol:
                shared[j]["south"] = True
    return shared


# ── Build one room ────────────────────────────────────────────────────────────


def build_room_mesh(
    name: str,
    x: float,
    y: float,
    w: float,
    l: float,
    h: float,
    z: float = 0.0,
    door_south: bool = False,
    door_north: bool = False,
    door_west: bool = False,
    door_east: bool = False,
    shared_south: bool = False,
    shared_north: bool = False,
    shared_west: bool = False,
    shared_east: bool = False,
) -> Mesh:
    """
    Build one room: floor + ceiling + 4 thick walls with optional door gaps.
    shared_* flags suppress a wall entirely when the neighbour already built it.
    """
    m = Mesh(name)
    z0, z1 = z, z + h

    # Floor
    m.add_quad((x, y, z0), (x + w, y, z0), (x + w, y + l, z0), (x, y + l, z0))
    # Ceiling
    m.add_quad((x, y + l, z1), (x + w, y + l, z1), (x + w, y, z1), (x, y, z1))

    # South wall (y=y, normal=-Y) — skip if shared (neighbour to south built it)
    if not shared_south:
        m.add_thick_wall(x, y, x + w, y, z0, z1, (0.0, -1.0), door=door_south)
    # North wall (y=y+l, normal=+Y) — always build (neighbour to north will skip theirs)
    if not shared_north:
        m.add_thick_wall(x + w, y + l, x, y + l, z0, z1, (0.0, 1.0), door=door_north)
    # West wall (x=x, normal=-X) — skip if shared
    if not shared_west:
        m.add_thick_wall(x, y + l, x, y, z0, z1, (-1.0, 0.0), door=door_west)
    # East wall (x=x+w, normal=+X) — always build
    if not shared_east:
        m.add_thick_wall(x + w, y, x + w, y + l, z0, z1, (1.0, 0.0), door=door_east)

    # Furniture
    _add_furniture(m, _room_base_type(name), x, y, w, l, z0)

    return m


# ── GLB packer ────────────────────────────────────────────────────────────────

# Per-room-type base colors [R, G, B] in linear space (approx)
_ROOM_COLORS: Dict[str, List[float]] = {
    "master_bedroom": [0.85, 0.70, 0.70],
    "bedroom": [0.80, 0.75, 0.90],
    "bedroom_2": [0.75, 0.80, 0.90],
    "bedroom_3": [0.70, 0.85, 0.90],
    "bedroom_4": [0.70, 0.85, 0.85],
    "bedroom_5": [0.70, 0.80, 0.85],
    "hall": [0.95, 0.90, 0.75],
    "living": [0.95, 0.90, 0.75],
    "living_room": [0.95, 0.90, 0.75],
    "kitchen": [0.80, 0.95, 0.80],
    "dining": [0.95, 0.85, 0.70],
    "dining_room": [0.95, 0.85, 0.70],
    "bathroom": [0.70, 0.85, 0.95],
    "master_bathroom": [0.65, 0.80, 0.95],
    "common_bathroom": [0.70, 0.85, 0.95],
    "toilet": [0.75, 0.88, 0.95],
    "balcony": [0.75, 0.95, 0.80],
    "study": [0.90, 0.85, 0.70],
    "pooja_room": [0.95, 0.88, 0.65],
    "garage": [0.80, 0.80, 0.80],
    "passage": [0.90, 0.90, 0.85],
    "corridor": [0.90, 0.90, 0.85],
    "store": [0.85, 0.82, 0.78],
    "utility": [0.82, 0.85, 0.78],
}
_DEFAULT_COLOR = [0.88, 0.88, 0.88]


def _room_color(name: str) -> List[float]:
    """Return RGBA color for a room by matching its base type."""
    key = name.split("_s")[0]  # strip story suffix
    parts = key.rsplit("_", 1)
    candidates = [key, parts[0] if len(parts) == 2 and parts[1].isdigit() else key]
    for c in candidates:
        if c in _ROOM_COLORS:
            return _ROOM_COLORS[c] + [1.0]
    # try prefix match
    for k, v in _ROOM_COLORS.items():
        if key.startswith(k):
            return v + [1.0]
    return _DEFAULT_COLOR + [1.0]


def _swap_yz(v: Vertex) -> Vertex:
    """Convert from Z-up (XYZ) to Y-up (XZY) for glTF standard orientation.
    Rooms are built in XY plane with Z as height.
    glTF Y-up: X stays, Y=height(Z), Z=-depth(-Y) so floor sits at Y=0.
    """
    x, y, z = v
    return (x, z, y)


def _normals_for_mesh(m: Mesh) -> List[Vertex]:
    # compute normals in original space then swap
    normals = [[0.0, 0.0, 0.0] for _ in m.verts]
    for tri in m.tris:
        v0, v1, v2 = m.verts[tri[0]], m.verts[tri[1]], m.verts[tri[2]]
        e1 = (v1[0] - v0[0], v1[1] - v0[1], v1[2] - v0[2])
        e2 = (v2[0] - v0[0], v2[1] - v0[1], v2[2] - v0[2])
        nx = e1[1] * e2[2] - e1[2] * e2[1]
        ny = e1[2] * e2[0] - e1[0] * e2[2]
        nz = e1[0] * e2[1] - e1[1] * e2[0]
        for idx in tri:
            normals[idx][0] += nx
            normals[idx][1] += ny
            normals[idx][2] += nz
    result: List[Vertex] = []
    for n in normals:
        mag = math.sqrt(n[0] ** 2 + n[1] ** 2 + n[2] ** 2)
        raw = (n[0] / mag, n[1] / mag, n[2] / mag) if mag > 0 else (0.0, 0.0, 1.0)
        result.append(_swap_yz(raw))
    return result


def _pad4(b: bytes) -> bytes:
    r = len(b) % 4
    return b + b"\x00" * ((4 - r) % 4)


def pack_glb_multi_mesh(meshes: List[Mesh]) -> bytes:
    """
    Pack named Mesh objects into a single GLB 2.0 file.
    - Y-up orientation (swap Y↔Z so floor lies on XZ plane)
    - Per-room colored PBR materials
    """
    if not meshes:
        raise ValueError("No meshes to pack")

    bin_chunks: List[bytes] = []
    buffer_views = []
    accessors = []
    gltf_meshes = []
    gltf_materials = []
    nodes = []
    offset = 0

    for m in meshes:
        if not m.verts or not m.tris:
            continue

        # Apply Y-up swap to all vertices
        verts_yup = [_swap_yz(v) for v in m.verts]
        norms = _normals_for_mesh(m)

        pos_buf = _pad4(b"".join(struct.pack("<fff", *v) for v in verts_yup))
        nor_buf = _pad4(b"".join(struct.pack("<fff", *n) for n in norms))
        idx_buf = _pad4(b"".join(struct.pack("<I", i) for tri in m.tris for i in tri))

        bv_pos = len(buffer_views)
        buffer_views.append({"buffer": 0, "byteOffset": offset, "byteLength": len(pos_buf)})
        offset += len(pos_buf)
        bin_chunks.append(pos_buf)

        bv_nor = len(buffer_views)
        buffer_views.append({"buffer": 0, "byteOffset": offset, "byteLength": len(nor_buf)})
        offset += len(nor_buf)
        bin_chunks.append(nor_buf)

        bv_idx = len(buffer_views)
        buffer_views.append({"buffer": 0, "byteOffset": offset, "byteLength": len(idx_buf)})
        offset += len(idx_buf)
        bin_chunks.append(idx_buf)

        # Compute POSITION min/max for accessor (required by spec)
        xs = [v[0] for v in verts_yup]
        ys = [v[1] for v in verts_yup]
        zs = [v[2] for v in verts_yup]

        acc_pos = len(accessors)
        accessors.append(
            {
                "bufferView": bv_pos,
                "componentType": 5126,
                "count": len(verts_yup),
                "type": "VEC3",
                "min": [min(xs), min(ys), min(zs)],
                "max": [max(xs), max(ys), max(zs)],
            }
        )
        acc_nor = len(accessors)
        accessors.append({"bufferView": bv_nor, "componentType": 5126, "count": len(verts_yup), "type": "VEC3"})
        acc_idx = len(accessors)
        accessors.append({"bufferView": bv_idx, "componentType": 5125, "count": len(m.tris) * 3, "type": "SCALAR"})

        # Material
        mat_idx = len(gltf_materials)
        rgba = _room_color(m.name)
        gltf_materials.append(
            {
                "name": f"{m.name}_mat",
                "pbrMetallicRoughness": {
                    "baseColorFactor": rgba,
                    "metallicFactor": 0.0,
                    "roughnessFactor": 0.8,
                },
                "doubleSided": True,
            }
        )

        mesh_idx = len(gltf_meshes)
        gltf_meshes.append(
            {
                "name": m.name,
                "primitives": [
                    {
                        "attributes": {"POSITION": acc_pos, "NORMAL": acc_nor},
                        "indices": acc_idx,
                        "mode": 4,
                        "material": mat_idx,
                    }
                ],
            }
        )
        nodes.append({"mesh": mesh_idx, "name": m.name})

    if not gltf_meshes:
        raise ValueError("All meshes were empty")

    bin_data = b"".join(bin_chunks)

    gltf = {
        "asset": {"version": "2.0", "generator": "BHIV-RoomGeometry-v4"},
        "scene": 0,
        "scenes": [{"nodes": list(range(len(nodes)))}],
        "nodes": nodes,
        "meshes": gltf_meshes,
        "materials": gltf_materials,
        "accessors": accessors,
        "bufferViews": buffer_views,
        "buffers": [{"byteLength": len(bin_data)}],
    }

    json_bytes = json.dumps(gltf, separators=(",", ":")).encode("utf-8")
    json_pad = (4 - len(json_bytes) % 4) % 4
    json_bytes += b" " * json_pad

    bin_pad = (4 - len(bin_data) % 4) % 4
    bin_data += b"\x00" * bin_pad

    total = 12 + 8 + len(json_bytes) + 8 + len(bin_data)
    return (
        b"glTF"
        + struct.pack("<II", 2, total)
        + struct.pack("<I", len(json_bytes))
        + b"JSON"
        + json_bytes
        + struct.pack("<I", len(bin_data))
        + b"BIN\x00"
        + bin_data
    )


# ── Domain-specific mesh builders ────────────────────────────────────────────


def _build_vehicles_meshes(spec_json: Dict[str, Any]) -> List[Mesh]:
    design_type = (spec_json.get("design_type") or "drone").lower()
    dims = spec_json.get("dimensions") or {}
    W = float(dims.get("width", 1.0))
    L = float(dims.get("length", 1.5))
    H = float(dims.get("height", 0.5))
    meshes: List[Mesh] = []

    if design_type in ("drone", "quadcopter", "uav"):
        # All parts built relative to origin (0,0,0) = drone center
        # W=1.0, L=1.5, H=0.5 are the overall bounding dimensions
        bw = W * 0.28  # body width  (X)
        bl = W * 0.28  # body length (Y) — square body
        bh = H * 0.5  # body height (Z)
        arm_thick = W * 0.05  # arm cross-section
        arm_len = W * 0.35  # arm length from body edge to rotor center
        rotor_r = W * 0.18  # rotor blade half-length
        rotor_h = H * 0.04  # rotor blade thickness
        leg_h = H * 0.35  # landing leg height below body

        # ── Central body ──────────────────────────────────────────────────────
        body = Mesh("drone_body")
        _add_box(body, -bw / 2, -bl / 2, 0.0, bw, bl, bh)
        meshes.append(body)

        # ── 4 arms: +X, -X, +Y, -Y (axis-aligned, not diagonal) ──────────────
        # Each arm is a thin rod starting at the body edge, going outward
        arm_tip_positions = [
            (bw / 2 + arm_len, 0.0),  # +X arm tip
            (-bw / 2 - arm_len, 0.0),  # -X arm tip
            (0.0, bl / 2 + arm_len),  # +Y arm tip
            (0.0, -bl / 2 - arm_len),  # -Y arm tip
        ]
        arm_starts = [
            (bw / 2, -arm_thick / 2),  # +X arm start
            (-bw / 2 - arm_len, -arm_thick / 2),  # -X arm start
            (-arm_thick / 2, bl / 2),  # +Y arm start
            (-arm_thick / 2, -bl / 2 - arm_len),  # -Y arm start
        ]
        arm_sizes = [
            (arm_len, arm_thick, arm_thick),  # +X: long in X
            (arm_len, arm_thick, arm_thick),  # -X: long in X
            (arm_thick, arm_len, arm_thick),  # +Y: long in Y
            (arm_thick, arm_len, arm_thick),  # -Y: long in Y
        ]
        arm_z = bh * 0.35  # arms attach at mid-height of body

        for i in range(4):
            arm = Mesh(f"arm_{i}")
            ax, ay = arm_starts[i]
            aw, al, ah = arm_sizes[i]
            _add_box(arm, ax, ay, arm_z, aw, al, ah)
            meshes.append(arm)

            # Rotor disc centered at arm tip
            tx, ty = arm_tip_positions[i]
            rotor = Mesh(f"rotor_{i}")
            _add_box(rotor, tx - rotor_r, ty - arm_thick / 2, arm_z + arm_thick, rotor_r * 2, arm_thick, rotor_h)
            meshes.append(rotor)

        # ── 4 landing legs under body corners ─────────────────────────────────
        leg_thick = W * 0.03
        for i, (lx, ly) in enumerate(
            [
                (bw / 2 - leg_thick, bl / 2 - leg_thick),
                (-bw / 2, bl / 2 - leg_thick),
                (bw / 2 - leg_thick, -bl / 2),
                (-bw / 2, -bl / 2),
            ]
        ):
            leg = Mesh(f"leg_{i}")
            _add_box(leg, lx, ly, -leg_h, leg_thick, leg_thick, leg_h)
            meshes.append(leg)

    elif design_type in ("spacecraft", "rocket", "starship"):
        # Use fixed proportions — ignore tiny H default, build vertically (Z = up)
        # Spacecraft stands upright: narrow body, tall, with nose at top
        FW = W * 0.38  # fuselage width  (X)
        FL = W * 0.38  # fuselage depth  (Y) — square cross-section
        FH = W * 2.8  # fuselage height (Z) — tall rocket body
        base_z = 0.0

        # ── Main fuselage (tall cylinder approximated as box) ──────────────
        fuselage = Mesh("fuselage")
        _add_box(fuselage, -FW / 2, -FL / 2, base_z, FW, FL, FH)
        meshes.append(fuselage)

        # ── Nose cone: 4 stacked shrinking boxes tapering to a point ──────
        nose_sections = 5
        nose_h = W * 0.12
        for ni in range(nose_sections):
            t = 1.0 - (ni + 1) / nose_sections  # 0.8 → 0.6 → 0.4 → 0.2 → 0.0
            nw = FW * (t + 0.15)
            nl = FL * (t + 0.15)
            nose_sec = Mesh(f"nose_{ni}")
            _add_box(nose_sec, -nw / 2, -nl / 2, base_z + FH + ni * nose_h, nw, nl, nose_h)
            meshes.append(nose_sec)

        # ── Swept delta wings — large, visible, at lower fuselage ─────────
        wing_z = base_z + FH * 0.12  # attach low on fuselage
        wing_h = W * 0.06  # visible thickness
        wing_span = W * 1.1  # extends well beyond fuselage
        wing_len = W * 0.9  # front-to-back chord
        for side in (-1, 1):
            wing = Mesh(f"wing_{'L' if side < 0 else 'R'}")
            wx = side * FW / 2 if side > 0 else side * FW / 2 - wing_span
            _add_box(wing, wx, -wing_len / 2, wing_z, wing_span, wing_len, wing_h)
            meshes.append(wing)

        # ── Solar panels — flat wide panels mid-fuselage ──────────────────
        panel_z = base_z + FH * 0.55
        panel_span = W * 1.4
        panel_depth = W * 0.5
        panel_thick = W * 0.04
        for side in (-1, 1):
            panel = Mesh(f"solar_panel_{'L' if side < 0 else 'R'}")
            px = side * FW / 2 if side > 0 else side * FW / 2 - panel_span
            _add_box(panel, px, -panel_depth / 2, panel_z, panel_span, panel_depth, panel_thick)
            meshes.append(panel)

        # ── Engine nozzles — 3 bell-shaped boxes at base ──────────────────
        nozzle_w = FW * 0.28
        nozzle_h = W * 0.32
        nozzle_positions = [-FW * 0.3, 0.0, FW * 0.3]
        for i, nx in enumerate(nozzle_positions):
            # Bell: wider at bottom, narrower at top — 2 stacked boxes
            bell_outer = Mesh(f"nozzle_bell_{i}")
            _add_box(
                bell_outer, nx - nozzle_w * 0.7, -FL * 0.3, base_z - nozzle_h, nozzle_w * 1.4, FL * 0.6, nozzle_h * 0.6
            )
            meshes.append(bell_outer)
            bell_inner = Mesh(f"nozzle_throat_{i}")
            _add_box(
                bell_inner,
                nx - nozzle_w * 0.45,
                -FL * 0.2,
                base_z - nozzle_h * 0.4,
                nozzle_w * 0.9,
                FL * 0.4,
                nozzle_h * 0.4,
            )
            meshes.append(bell_inner)

        # ── Docking port — cylinder stub at nose ──────────────────────────
        port_w = FW * 0.35
        port = Mesh("docking_port")
        _add_box(port, -port_w / 2, -port_w / 2, base_z + FH + nose_sections * nose_h, port_w, port_w, W * 0.18)
        meshes.append(port)

        # ── Booster fins — 4 small triangular fins at very base ───────────
        fin_h = W * 0.55
        fin_d = W * 0.22
        fin_t = W * 0.05
        for i, (fx, fy) in enumerate(
            [
                (FW / 2, -fin_t / 2),
                (-FW / 2 - fin_d, -fin_t / 2),
                (-fin_t / 2, FL / 2),
                (-fin_t / 2, -FL / 2 - fin_d),
            ]
        ):
            fin = Mesh(f"fin_{i}")
            _add_box(fin, fx, fy, base_z, fin_d, fin_t, fin_h)
            meshes.append(fin)

    elif design_type in ("rover", "truck", "lorry"):
        # All parts built from origin (0,0,0) = front-left-bottom of truck
        # Truck layout along Y axis: cab at front (low Y), cargo at rear (high Y)
        # Tyre: thin in X (axle width), square Y/Z cross-section (diameter)
        # Use W*0.20 as tyre diameter so it's clearly visible
        TD = W * 0.20  # tyre diameter — both height (Z) and drive-length (Y)
        TW = W * 0.06  # tyre axle width — thin like a real tyre
        chassis_h = H * 0.10

        # ── Chassis — full-length base slab ───────────────────────────────────
        chassis = Mesh("chassis")
        _add_box(chassis, W * 0.08, 0.0, TD, W * 0.84, L, chassis_h)
        meshes.append(chassis)

        # ── Cab — front section, taller than cargo ─────────────────────────────
        cab_l = L * 0.30
        cab_h = H * 0.72
        cab = Mesh("cab")
        _add_box(cab, W * 0.06, 0.0, TD + chassis_h, W * 0.88, cab_l, cab_h)
        meshes.append(cab)

        # Windshield recess — thin slab on front face of cab
        ws_w = W * 0.60
        ws_h = cab_h * 0.42
        windshield = Mesh("windshield")
        _add_box(windshield, (W - ws_w) / 2, -W * 0.01, TD + chassis_h + cab_h * 0.35, ws_w, W * 0.02, ws_h)
        meshes.append(windshield)

        # Cab roof visor
        visor = Mesh("roof_visor")
        _add_box(visor, W * 0.06, 0.0, TD + chassis_h + cab_h, W * 0.88, cab_l * 0.4, H * 0.06)
        meshes.append(visor)

        # ── Cargo box — rear section, lower than cab ───────────────────────────
        cargo_l = L * 0.65
        cargo_h = H * 0.58
        cargo = Mesh("cargo_box")
        _add_box(cargo, W * 0.04, cab_l, TD + chassis_h, W * 0.92, cargo_l, cargo_h)
        meshes.append(cargo)

        # Cargo rear door
        door_slab = Mesh("cargo_door")
        _add_box(
            door_slab, W * 0.10, cab_l + cargo_l, TD + chassis_h + cargo_h * 0.05, W * 0.80, W * 0.015, cargo_h * 0.88
        )
        meshes.append(door_slab)

        # ── Exhaust stack ──────────────────────────────────────────────────────
        exhaust = Mesh("exhaust")
        _add_box(exhaust, W * 0.88, cab_l * 0.1, TD + chassis_h, W * 0.04, W * 0.04, cab_h * 1.15)
        meshes.append(exhaust)

        # ── Front bumper ───────────────────────────────────────────────────────
        bumper = Mesh("bumper")
        _add_box(bumper, W * 0.06, -W * 0.04, TD, W * 0.88, W * 0.04, H * 0.22)
        meshes.append(bumper)

        # ── Wheels: flat disc — thin TW in X, square TD×TD in Y/Z ─────────────
        # Left tyres at x=0, right tyres at x=W-TW
        # Front axle: single tyre each side (wider tyre TW*1.8)
        # Rear axles: dual tyres each side (two TW-wide tyres side by side)
        cab_l_val = cab_l
        cargo_l_val = cargo_l
        axle_configs = [
            (cab_l_val * 0.55, False),
            (cab_l_val + cargo_l_val * 0.28, True),
            (cab_l_val + cargo_l_val * 0.72, True),
        ]
        wi = 0
        gap = TW * 0.5  # gap between dual tyres
        for axle_y, dual in axle_configs:
            ty = axle_y - TD / 2
            if not dual:
                ftw = TW * 1.8  # front single tyre — wider
                for x_pos in [0.0, W - ftw]:
                    w_mesh = Mesh(f"wheel_{wi}")
                    _add_box(w_mesh, x_pos, ty, 0.0, ftw, TD, TD)
                    meshes.append(w_mesh)
                    wi += 1
            else:
                # Left side: two thin tyres side by side from x=0
                for x_pos in [0.0, TW + gap]:
                    w_mesh = Mesh(f"wheel_{wi}")
                    _add_box(w_mesh, x_pos, ty, 0.0, TW, TD, TD)
                    meshes.append(w_mesh)
                    wi += 1
                # Right side: two thin tyres side by side ending at x=W
                for x_pos in [W - 2 * TW - gap, W - TW]:
                    w_mesh = Mesh(f"wheel_{wi}")
                    _add_box(w_mesh, x_pos, ty, 0.0, TW, TD, TD)
                    meshes.append(w_mesh)
                    wi += 1

    elif design_type in ("ship", "vessel", "boat", "yacht"):
        # All parts from origin (0,0,0). Ship runs along Y axis: bow at Y=0, stern at Y=L
        # Use W-relative proportions so it scales correctly regardless of input dims
        HULL_H = W * 0.18  # hull side wall height — tall, visible
        DECK_H = W * 0.03  # deck slab thickness
        base_z = 0.0

        # ── Hull — main body box ─────────────────────────────────────────────────────
        hull = Mesh("hull")
        _add_box(hull, 0.0, 0.0, base_z, W, L, HULL_H)
        meshes.append(hull)

        # ── Bow wedge — narrowing front section (2 stepped boxes tapering inward) ──
        bow_l = L * 0.12
        for bi, (bx_off, bw_frac) in enumerate([(W * 0.08, 0.84), (W * 0.18, 0.64)]):
            bow = Mesh(f"bow_{bi}")
            _add_box(bow, bx_off, -bow_l * (bi + 1) * 0.5, base_z, W * bw_frac, bow_l * 0.55, HULL_H * 0.85)
            meshes.append(bow)

        # ── Deck — full-length flat slab on top of hull ──────────────────────────
        deck_z = base_z + HULL_H
        deck = Mesh("deck")
        _add_box(deck, 0.0, 0.0, deck_z, W, L, DECK_H)
        meshes.append(deck)

        # ── Superstructure — multi-level block at rear 40% of ship ────────────────
        sup_z = deck_z + DECK_H
        sup_y = L * 0.55  # starts at 55% along ship
        sup_l = L * 0.32  # spans 32% of ship length
        sup_w = W * 0.70
        sup_h = W * 0.28
        sup_x = (W - sup_w) / 2

        # Level 1 — widest base
        sup1 = Mesh("superstructure_l1")
        _add_box(sup1, sup_x, sup_y, sup_z, sup_w, sup_l, sup_h)
        meshes.append(sup1)
        # Level 2 — narrower, shorter
        sup2 = Mesh("superstructure_l2")
        _add_box(
            sup2, sup_x + sup_w * 0.1, sup_y + sup_l * 0.1, sup_z + sup_h, sup_w * 0.80, sup_l * 0.80, sup_h * 0.65
        )
        meshes.append(sup2)
        # Bridge windows strip — thin slab on front face of level 2
        win = Mesh("bridge_windows")
        _add_box(
            win,
            sup_x + sup_w * 0.12,
            sup_y + sup_l * 0.08,
            sup_z + sup_h + sup_h * 0.25,
            sup_w * 0.76,
            W * 0.02,
            sup_h * 0.35,
        )
        meshes.append(win)

        # ── Funnel / smokestack — tall box behind superstructure ────────────────
        fn_w = W * 0.12
        fn_h = W * 0.45
        fn_x = (W - fn_w) / 2
        fn_y = sup_y + sup_l * 0.55
        funnel = Mesh("funnel")
        _add_box(funnel, fn_x, fn_y, sup_z + sup_h * 1.6, fn_w, fn_w, fn_h)
        meshes.append(funnel)
        # Funnel cap
        funnel_cap = Mesh("funnel_cap")
        _add_box(
            funnel_cap,
            fn_x - fn_w * 0.15,
            fn_y - fn_w * 0.15,
            sup_z + sup_h * 1.6 + fn_h,
            fn_w * 1.3,
            fn_w * 1.3,
            fn_h * 0.12,
        )
        meshes.append(funnel_cap)

        # ── Mast — tall thin pole at bow area ──────────────────────────────────
        mast_w = W * 0.018
        mast_h = W * 0.75
        mast = Mesh("mast")
        _add_box(mast, (W - mast_w) / 2, L * 0.18, sup_z + DECK_H, mast_w, mast_w, mast_h)
        meshes.append(mast)
        # Crow's nest box on mast
        nest_w = mast_w * 4
        nest = Mesh("crows_nest")
        _add_box(
            nest, (W - nest_w) / 2, L * 0.18 - nest_w, sup_z + DECK_H + mast_h * 0.65, nest_w, nest_w * 2, mast_w * 2
        )
        meshes.append(nest)

        # ── Anchor chain box — small block at bow deck ─────────────────────────
        anchor = Mesh("anchor_winch")
        _add_box(anchor, W * 0.38, L * 0.06, sup_z + DECK_H, W * 0.24, L * 0.05, W * 0.06)
        meshes.append(anchor)

        # ── Side railings — thin strips along both sides of deck ────────────────
        rail_h = W * 0.04
        rail_t = W * 0.012
        for rx, rl_len in [(0.0, L), (W - rail_t, L)]:
            rail = Mesh(f"railing_{int(rx)}")
            _add_box(rail, rx, 0.0, sup_z + DECK_H, rail_t, rl_len, rail_h)
            meshes.append(rail)

        # ── Cargo hatches — 3 recessed boxes on forward deck ───────────────────
        hatch_w = W * 0.30
        hatch_l = L * 0.10
        hatch_h = W * 0.025
        for hi, hy in enumerate([L * 0.22, L * 0.36, L * 0.50]):
            hatch = Mesh(f"hatch_{hi}")
            _add_box(hatch, (W - hatch_w) / 2, hy, sup_z + DECK_H, hatch_w, hatch_l, hatch_h)
            meshes.append(hatch)

    else:
        generic = Mesh(design_type)
        _add_box(generic, -W / 2, -L / 2, 0.0, W, L, H)
        meshes.append(generic)

    return meshes


def _build_objects_meshes(spec_json: Dict[str, Any]) -> List[Mesh]:
    design_type = (spec_json.get("design_type") or "box").lower()
    dims = spec_json.get("dimensions") or {}
    W = float(dims.get("width", 1.0))
    L = float(dims.get("length", 1.0))
    H = float(dims.get("height", 1.0))
    meshes: List[Mesh] = []

    if design_type in ("box", "crate"):
        body = Mesh("crate_body")
        _add_box(body, 0.0, 0.0, 0.0, W, L, H)
        meshes.append(body)
        lid = Mesh("crate_lid")
        _add_box(lid, 0.02, 0.02, H, W - 0.04, L - 0.04, H * 0.06)
        meshes.append(lid)
        cr = H * 0.08
        for ci, (cx, cy) in enumerate([(0.0, 0.0), (W - cr, 0.0), (0.0, L - cr), (W - cr, L - cr)]):
            corner = Mesh(f"corner_{ci}")
            _add_box(corner, cx, cy, 0.0, cr, cr, H)
            meshes.append(corner)

    elif design_type == "barrel":
        # Barrel shape: 5 stacked sections, widest at middle, narrowest at top/bottom
        # Each section is slightly inset from the one below/above it
        # Hoops sit ON the body surface (same width), not protruding outside
        cx, cy = W / 2, L / 2  # barrel centre in XY

        # Section profiles: (width_frac, length_frac, height_frac)
        # Bottom to top: narrow -> wide -> widest -> wide -> narrow
        sections = [
            (0.72, 0.72, 0.14),  # bottom cap section
            (0.88, 0.88, 0.20),  # lower body
            (0.96, 0.96, 0.22),  # widest middle
            (0.88, 0.88, 0.20),  # upper body
            (0.72, 0.72, 0.14),  # top cap section
        ]
        z_cursor = 0.0
        for si, (wf, lf, hf) in enumerate(sections):
            sw, sl, sh = W * wf, L * lf, H * hf
            sx, sy = cx - sw / 2, cy - sl / 2
            sec = Mesh(f"barrel_section_{si}")
            _add_box(sec, sx, sy, z_cursor, sw, sl, sh)
            meshes.append(sec)
            z_cursor += sh

        # Metal hoops: thin flat rings at 4 heights, same width as local section
        # Place at bottom, lower-mid, upper-mid, top
        hoop_h = H * 0.028
        hoop_t = W * 0.018  # how much hoop protrudes beyond section surface
        hoop_positions = [
            (H * 0.08, 0.74),  # near bottom
            (H * 0.30, 0.90),  # lower body
            (H * 0.68, 0.90),  # upper body
            (H * 0.90, 0.74),  # near top
        ]
        for hz, wf in hoop_positions:
            hw = W * wf + hoop_t * 2
            hl = L * wf + hoop_t * 2
            hoop = Mesh(f"hoop_{hz:.2f}")
            _add_box(hoop, cx - hw / 2, cy - hl / 2, hz, hw, hl, hoop_h)
            meshes.append(hoop)

        # Vertical stave lines: thin tall slabs on the barrel surface
        # 8 staves evenly around the barrel (4 on front face, 4 on back)
        stave_w = W * 0.022
        stave_h = H * 0.82
        stave_z = H * 0.09
        stave_t = W * 0.012
        n_staves = 6
        for si in range(n_staves):
            frac = si / n_staves
            # Front face staves (along Y=cy-W*0.48)
            sx = cx - W * 0.46 + frac * W * 0.92
            stave = Mesh(f"stave_front_{si}")
            _add_box(stave, sx, cy - W * 0.48 - stave_t, stave_z, stave_w, stave_t, stave_h)
            meshes.append(stave)

        # Bottom disc
        bot = Mesh("barrel_bottom")
        bw, bl = W * 0.68, L * 0.68
        _add_box(bot, cx - bw / 2, cy - bl / 2, 0.0, bw, bl, H * 0.025)
        meshes.append(bot)

        # Top disc
        top_cap = Mesh("barrel_top")
        _add_box(top_cap, cx - bw / 2, cy - bl / 2, z_cursor, bw, bl, H * 0.025)
        meshes.append(top_cap)

    elif design_type in ("wall", "partition"):
        wall_m = Mesh("wall_panel")
        _add_box(wall_m, 0.0, 0.0, 0.0, W, L, H)
        meshes.append(wall_m)

    elif design_type in ("door", "gate"):
        frame = Mesh("door_frame")
        t = max(W * 0.08, 0.05)
        _add_box(frame, 0.0, 0.0, 0.0, t, L, H)
        _add_box(frame, W - t, 0.0, 0.0, t, L, H)
        _add_box(frame, 0.0, 0.0, H - t, W, L, t)
        meshes.append(frame)
        panel = Mesh("door_panel")
        _add_box(panel, t, L * 0.05, 0.0, W - 2 * t, L * 0.05, H - t)
        meshes.append(panel)

    elif design_type in ("staircase", "stair", "stairway"):
        n_steps = max(int(H / 0.18), 4)
        riser = H / n_steps
        run = L / n_steps
        for i in range(n_steps):
            step = Mesh(f"step_{i:02d}")
            _add_box(step, 0.0, i * run, 0.0, W, run, riser * (i + 1))
            meshes.append(step)
        for si, sx in enumerate([0.0, W - 0.05]):
            stringer = Mesh(f"stringer_{si}")
            _add_box(stringer, sx, 0.0, 0.0, 0.05, L, H * 0.15)
            meshes.append(stringer)

    else:
        generic = Mesh(design_type)
        _add_box(generic, 0.0, 0.0, 0.0, W, L, H)
        meshes.append(generic)

    return meshes


def _build_gameplay_meshes(spec_json: Dict[str, Any]) -> List[Mesh]:
    design_type = (spec_json.get("design_type") or "obstacle").lower()
    dims = spec_json.get("dimensions") or {}
    W = float(dims.get("width", 1.0))
    L = float(dims.get("length", 1.0))
    H = float(dims.get("height", 1.5))
    meshes: List[Mesh] = []

    if design_type in ("checkpoint", "finish_line", "waypoint"):
        pw = W * 0.07  # post width
        pd = L * 0.55  # post depth
        bar_h = H * 0.09  # crossbar height

        # Left post
        left = Mesh("post_left")
        _add_box(left, 0.0, 0.0, 0.0, pw, pd, H)
        meshes.append(left)
        # Right post
        right = Mesh("post_right")
        _add_box(right, W - pw, 0.0, 0.0, pw, pd, H)
        meshes.append(right)

        # Top crossbar — thin, spanning full width
        bar = Mesh("crossbar")
        _add_box(bar, 0.0, 0.0, H - bar_h, W, pd, bar_h)
        meshes.append(bar)

        # Mid crossbar — second bar at mid-height for racing gate look
        mid_bar = Mesh("mid_crossbar")
        _add_box(mid_bar, 0.0, 0.0, H * 0.52, W, pd * 0.5, bar_h * 0.7)
        meshes.append(mid_bar)

        # Sensor beam boxes — 3 thin horizontal rods spanning the gate opening
        beam_w = W - 2 * pw
        beam_d = pd * 0.12
        beam_h = bar_h * 0.35
        for bi, bz in enumerate([H * 0.20, H * 0.50, H * 0.78]):
            beam = Mesh(f"sensor_beam_{bi}")
            _add_box(beam, pw, pd * 0.22, bz, beam_w, beam_d, beam_h)
            meshes.append(beam)

        # Sensor nodes — small boxes on each post at beam heights
        node_w = pw * 1.6
        node_h = bar_h * 0.8
        for bi, bz in enumerate([H * 0.20, H * 0.50, H * 0.78]):
            for side_x in [0.0 - node_w * 0.3, W - pw - node_w * 0.7]:
                node = Mesh(f"sensor_node_{bi}_{int(side_x)}_")
                _add_box(node, side_x, pd * 0.15, bz - node_h * 0.1, node_w, pd * 0.3, node_h)
                meshes.append(node)

        # Ground stripe — flat slab under the gate marking the line
        stripe = Mesh("ground_stripe")
        _add_box(stripe, -W * 0.05, pd * 0.1, 0.0, W * 1.1, pd * 0.25, H * 0.012)
        meshes.append(stripe)

        # Number board on top crossbar — flat panel centred
        board_w = W * 0.28
        board_h = H * 0.22
        board = Mesh("number_board")
        _add_box(board, (W - board_w) / 2, -pd * 0.05, H - bar_h - board_h, board_w, pd * 0.08, board_h)
        meshes.append(board)

        # Flag poles — thin vertical rods at top of each post
        flag_pole_h = H * 0.35
        flag_pole_w = pw * 0.3
        for fx in [pw * 0.35, W - pw * 0.65]:
            pole = Mesh(f"flag_pole_{int(fx)}")
            _add_box(pole, fx, pd * 0.2, H, flag_pole_w, flag_pole_w, flag_pole_h)
            meshes.append(pole)
            # Flag panel hanging from pole
            flag = Mesh(f"flag_{int(fx)}")
            _add_box(flag, fx, pd * 0.2, H + flag_pole_h * 0.5, flag_pole_w * 5, pd * 0.05, flag_pole_h * 0.4)
            meshes.append(flag)

    elif design_type in ("obstacle", "barrier", "hurdle"):
        base = Mesh("obstacle_base")
        _add_box(base, 0.0, 0.0, 0.0, W, L, H * 0.15)
        meshes.append(base)
        body = Mesh("obstacle_body")
        _add_box(body, W * 0.1, L * 0.1, H * 0.15, W * 0.8, L * 0.8, H * 0.75)
        meshes.append(body)
        for i in range(3):
            stripe = Mesh(f"stripe_{i}")
            sz = H * 0.15 + i * H * 0.2
            _add_box(stripe, -0.01, -0.01, sz, W + 0.02, L + 0.02, H * 0.06)
            meshes.append(stripe)

    elif design_type in ("collectible", "coin", "gem", "pickup", "powerup"):
        gem = Mesh("collectible_body")
        _add_box(gem, 0.0, 0.0, 0.0, W, L, H)
        meshes.append(gem)
        glow = Mesh("collectible_glow")
        pad = W * 0.1
        _add_box(glow, -pad, -pad, -pad, W + 2 * pad, L + 2 * pad, H + 2 * pad)
        meshes.append(glow)

    elif design_type in ("spawn_point", "spawn", "spawn_zone"):
        PH = H * 0.06  # platform slab height
        # Raised platform base
        platform = Mesh("spawn_platform")
        _add_box(platform, 0.0, 0.0, 0.0, W, L, PH)
        meshes.append(platform)

        # Arrow body: vertical slab pointing forward (+Y direction)
        arrow_w = W * 0.18
        arrow_l = L * 0.38
        arrow_h = H * 0.55  # tall, clearly visible
        ax = (W - arrow_w) / 2
        ay = L * 0.12
        arrow = Mesh("spawn_arrow_body")
        _add_box(arrow, ax, ay, PH, arrow_w, arrow_l, arrow_h)
        meshes.append(arrow)

        # Arrow head: wider box in front of the body
        head_w = W * 0.42
        head_l = L * 0.18
        head_h = arrow_h * 0.55
        hx = (W - head_w) / 2
        hy = ay + arrow_l
        head = Mesh("spawn_arrow_head")
        _add_box(head, hx, hy, PH + (arrow_h - head_h) / 2, head_w, head_l, head_h)
        meshes.append(head)

        # 4 corner beacon pillars — tall, thin, at platform corners
        pillar_w = W * 0.055
        pillar_h = H * 1.1
        for i, (px, py) in enumerate(
            [
                (W * 0.04, L * 0.04),
                (W - W * 0.04 - pillar_w, L * 0.04),
                (W * 0.04, L - L * 0.04 - pillar_w),
                (W - W * 0.04 - pillar_w, L - L * 0.04 - pillar_w),
            ]
        ):
            pillar = Mesh(f"spawn_pillar_{i}")
            _add_box(pillar, px, py, PH, pillar_w, pillar_w, pillar_h)
            meshes.append(pillar)

        # Beacon top caps on each pillar
        cap_w = pillar_w * 2.2
        for i, (px, py) in enumerate(
            [
                (W * 0.04, L * 0.04),
                (W - W * 0.04 - pillar_w, L * 0.04),
                (W * 0.04, L - L * 0.04 - pillar_w),
                (W - W * 0.04 - pillar_w, L - L * 0.04 - pillar_w),
            ]
        ):
            cap = Mesh(f"spawn_cap_{i}")
            cx = px - (cap_w - pillar_w) / 2
            cy = py - (cap_w - pillar_w) / 2
            _add_box(cap, cx, cy, PH + pillar_h, cap_w, cap_w, H * 0.12)
            meshes.append(cap)

        # Central beacon beam — tall glowing column in the middle
        beam_w = W * 0.07
        beam = Mesh("spawn_beacon")
        _add_box(beam, (W - beam_w) / 2, (L - beam_w) / 2, PH, beam_w, beam_w, H * 1.6)
        meshes.append(beam)

        # Horizontal ring bands around beacon at 3 heights
        ring_w = W * 0.32
        ring_t = W * 0.04
        ring_h = H * 0.06
        for rz in [PH + H * 0.4, PH + H * 0.8, PH + H * 1.2]:
            for side in range(4):
                ring = Mesh(f"spawn_ring_{rz:.2f}_{side}")
                if side == 0:  # south
                    _add_box(ring, (W - ring_w) / 2, (L - ring_w) / 2 - ring_t, rz, ring_w, ring_t, ring_h)
                elif side == 1:  # north
                    _add_box(ring, (W - ring_w) / 2, (L + ring_w) / 2, rz, ring_w, ring_t, ring_h)
                elif side == 2:  # west
                    _add_box(ring, (W - ring_w) / 2 - ring_t, (L - ring_w) / 2, rz, ring_t, ring_w, ring_h)
                else:  # east
                    _add_box(ring, (W + ring_w) / 2, (L - ring_w) / 2, rz, ring_t, ring_w, ring_h)
                meshes.append(ring)

    elif design_type in ("interactable", "interactive", "trigger"):
        pedestal = Mesh("interactable_pedestal")
        _add_box(pedestal, W * 0.3, L * 0.3, 0.0, W * 0.4, L * 0.4, H * 0.5)
        meshes.append(pedestal)
        top = Mesh("interactable_top")
        _add_box(top, W * 0.2, L * 0.2, H * 0.5, W * 0.6, L * 0.6, H * 0.15)
        meshes.append(top)
        button = Mesh("interactable_button")
        _add_box(button, W * 0.38, L * 0.38, H * 0.65, W * 0.24, L * 0.24, H * 0.08)
        meshes.append(button)

    else:
        generic = Mesh(design_type)
        _add_box(generic, 0.0, 0.0, 0.0, W, L, H)
        meshes.append(generic)

    return meshes


def _build_environment_meshes(spec_json: Dict[str, Any]) -> List[Mesh]:
    design_type = (spec_json.get("design_type") or "forest").lower().replace(" ", "_")
    dims = spec_json.get("dimensions") or {}
    W = float(dims.get("width", 50.0))
    L = float(dims.get("length", 50.0))
    H = float(dims.get("height", 20.0))
    meshes: List[Mesh] = []

    if design_type == "forest":
        GZ = W * 0.012  # ground surface z
        ground = Mesh("forest_ground")
        _add_box(ground, 0.0, 0.0, 0.0, W, L, GZ)
        meshes.append(ground)

        # 20 trees: (x_frac, y_frac, trunk_radius_frac, height_frac)
        tree_configs = [
            (0.10, 0.12, 0.022, 0.85),
            (0.25, 0.08, 0.018, 0.70),
            (0.42, 0.15, 0.025, 0.95),
            (0.60, 0.10, 0.020, 0.80),
            (0.78, 0.18, 0.023, 0.90),
            (0.88, 0.08, 0.017, 0.65),
            (0.05, 0.35, 0.021, 0.75),
            (0.20, 0.42, 0.026, 1.00),
            (0.38, 0.38, 0.019, 0.72),
            (0.55, 0.45, 0.024, 0.88),
            (0.72, 0.40, 0.022, 0.82),
            (0.90, 0.35, 0.020, 0.78),
            (0.12, 0.65, 0.023, 0.92),
            (0.30, 0.70, 0.018, 0.68),
            (0.48, 0.62, 0.025, 0.96),
            (0.65, 0.68, 0.021, 0.84),
            (0.82, 0.60, 0.024, 0.90),
            (0.92, 0.72, 0.019, 0.74),
            (0.22, 0.88, 0.022, 0.86),
            (0.58, 0.85, 0.020, 0.76),
        ]
        for i, (xf, yf, rf, hf) in enumerate(tree_configs):
            tx, ty = W * xf, L * yf
            tr = W * rf  # trunk half-width
            th = H * hf  # total tree height
            trunk_h = th * 0.48  # trunk = lower 48%
            canopy_r = W * rf * 5.5  # canopy radius — wide and visible
            canopy_h = th * 0.60  # canopy spans upper 60%

            trunk = Mesh(f"trunk_{i}")
            _add_box(trunk, tx - tr, ty - tr, GZ, tr * 2, tr * 2, trunk_h)
            meshes.append(trunk)

            # 3-layer conical canopy: bottom wide → top narrow
            for layer, (lr, lh_frac, lz_frac) in enumerate(
                [
                    (1.00, 0.38, 0.38),
                    (0.72, 0.32, 0.55),
                    (0.45, 0.28, 0.70),
                ]
            ):
                cr = canopy_r * lr
                lh = canopy_h * lh_frac
                lz = GZ + th * lz_frac
                layer_mesh = Mesh(f"canopy_{i}_l{layer}")
                _add_box(layer_mesh, tx - cr, ty - cr, lz, cr * 2, cr * 2, lh)
                meshes.append(layer_mesh)

        # Undergrowth bushes — small, low, scattered
        bush_configs = [
            (0.15, 0.28, 0.055, 0.040),
            (0.35, 0.22, 0.045, 0.035),
            (0.50, 0.32, 0.060, 0.042),
            (0.70, 0.25, 0.050, 0.038),
            (0.08, 0.55, 0.048, 0.036),
            (0.45, 0.55, 0.055, 0.040),
            (0.80, 0.50, 0.052, 0.038),
            (0.25, 0.78, 0.058, 0.042),
            (0.62, 0.75, 0.046, 0.035),
            (0.85, 0.82, 0.050, 0.038),
        ]
        for i, (xf, yf, wr, hr) in enumerate(bush_configs):
            bw = W * wr
            bush = Mesh(f"bush_{i}")
            _add_box(bush, W * xf - bw / 2, L * yf - bw / 2, GZ, bw, bw, H * hr)
            meshes.append(bush)

        # Fallen logs — horizontal elongated boxes on ground
        for i, (xf, yf, lf, wr, hr) in enumerate(
            [
                (0.32, 0.48, 0.18, 0.030, 0.022),
                (0.68, 0.55, 0.15, 0.025, 0.018),
                (0.15, 0.80, 0.20, 0.028, 0.020),
            ]
        ):
            log = Mesh(f"log_{i}")
            _add_box(log, W * xf, L * yf, GZ, W * lf, W * wr, H * hr)
            meshes.append(log)

    elif design_type in ("city_block", "urban_area", "street_scene"):
        road = Mesh("road")
        _add_box(road, 0.0, 0.0, 0.0, W * 0.35, L, 0.1)
        meshes.append(road)
        sidewalk = Mesh("sidewalk")
        _add_box(sidewalk, W * 0.35, 0.0, 0.0, W * 0.12, L, 0.15)
        meshes.append(sidewalk)
        bw = W * 0.12
        for i in range(4):
            bld = Mesh(f"building_{i}")
            bx = W * 0.47 + i * (W * 0.13)
            bh = H * (0.4 + i * 0.15)
            _add_box(bld, bx, L * 0.05, 0.0, bw, L * 0.9, bh)
            meshes.append(bld)
        for i in range(3):
            pole = Mesh(f"streetlight_{i}")
            px, py = W * 0.38, L * 0.15 + i * (L * 0.35)
            _add_box(pole, px, py, 0.0, 0.08, 0.08, H * 0.35)
            arm = Mesh(f"light_arm_{i}")
            _add_box(arm, px, py, H * 0.33, W * 0.05, 0.04, 0.04)
            meshes.append(pole)
            meshes.append(arm)

    elif design_type in ("industrial_zone", "factory_area", "industrial_complex"):
        ground = Mesh("industrial_ground")
        _add_box(ground, 0.0, 0.0, 0.0, W, L, 0.2)
        meshes.append(ground)
        factory = Mesh("factory_building")
        _add_box(factory, W * 0.1, L * 0.1, 0.2, W * 0.5, L * 0.6, H * 0.55)
        meshes.append(factory)
        for i, sx in enumerate([W * 0.15, W * 0.35]):
            stack = Mesh(f"smokestack_{i}")
            _add_box(stack, sx, L * 0.15, H * 0.55, W * 0.06, W * 0.06, H * 0.5)
            meshes.append(stack)
        for i in range(3):
            tank = Mesh(f"tank_{i}")
            _add_box(tank, W * 0.65 + i * W * 0.1, L * 0.2, 0.2, W * 0.08, W * 0.08, H * 0.3)
            meshes.append(tank)
        conveyor = Mesh("conveyor")
        _add_box(conveyor, W * 0.1, L * 0.72, 0.2, W * 0.6, L * 0.08, H * 0.08)
        meshes.append(conveyor)
        pipeline = Mesh("pipeline")
        _add_box(pipeline, W * 0.62, L * 0.1, H * 0.18, W * 0.04, L * 0.8, H * 0.04)
        meshes.append(pipeline)

    elif design_type in ("ocean_zone", "sea_zone", "underwater", "marine_environment", "ocean"):
        # Fixed proportions — ocean depth is W*0.4, everything sits between seabed and surface
        DEPTH = W * 0.4  # total water column height
        SEABED = 0.0  # seabed at z=0
        SURFACE = DEPTH  # water surface at z=DEPTH

        # ── Seabed — thick sandy floor ────────────────────────────────────────
        seabed = Mesh("seabed")
        _add_box(seabed, 0.0, 0.0, SEABED, W, L, W * 0.04)
        meshes.append(seabed)

        # ── Water surface — thin translucent slab directly on top ─────────────
        water_surface = Mesh("water_surface")
        _add_box(water_surface, 0.0, 0.0, SURFACE, W, L, W * 0.02)
        meshes.append(water_surface)

        # ── Underwater terrain — rolling hills on seabed ──────────────────────
        hill_h = DEPTH * 0.25
        for i, (hx, hy, hw, hl) in enumerate(
            [
                (W * 0.05, L * 0.05, W * 0.25, L * 0.20),
                (W * 0.55, L * 0.10, W * 0.30, L * 0.25),
                (W * 0.10, L * 0.60, W * 0.20, L * 0.30),
                (W * 0.65, L * 0.55, W * 0.28, L * 0.22),
            ]
        ):
            hill = Mesh(f"seabed_hill_{i}")
            _add_box(hill, hx, hy, W * 0.04, hw, hl, hill_h)
            meshes.append(hill)

        # ── Coral formations — tall, clustered, clearly visible ───────────────
        coral_configs = [
            (W * 0.15, L * 0.20, W * 0.04, W * 0.04, DEPTH * 0.55),
            (W * 0.20, L * 0.25, W * 0.03, W * 0.03, DEPTH * 0.45),
            (W * 0.18, L * 0.22, W * 0.025, W * 0.025, DEPTH * 0.65),
            (W * 0.60, L * 0.65, W * 0.04, W * 0.04, DEPTH * 0.50),
            (W * 0.65, L * 0.70, W * 0.03, W * 0.03, DEPTH * 0.60),
            (W * 0.62, L * 0.68, W * 0.025, W * 0.025, DEPTH * 0.40),
            (W * 0.35, L * 0.45, W * 0.035, W * 0.035, DEPTH * 0.55),
            (W * 0.40, L * 0.50, W * 0.03, W * 0.03, DEPTH * 0.45),
        ]
        for i, (cx, cy, cw, cl, ch) in enumerate(coral_configs):
            coral = Mesh(f"coral_{i}")
            _add_box(coral, cx, cy, W * 0.04, cw, cl, ch)
            meshes.append(coral)
            # coral branch on top
            branch = Mesh(f"coral_branch_{i}")
            _add_box(branch, cx - cw * 0.3, cy, W * 0.04 + ch, cw * 1.6, cl * 0.4, ch * 0.25)
            meshes.append(branch)

        # ── Rock formations — large boulders scattered on seabed ──────────────
        rock_configs = [
            (W * 0.30, L * 0.15, W * 0.10, L * 0.08, DEPTH * 0.30),
            (W * 0.70, L * 0.30, W * 0.12, L * 0.10, DEPTH * 0.25),
            (W * 0.10, L * 0.70, W * 0.09, L * 0.09, DEPTH * 0.28),
            (W * 0.50, L * 0.80, W * 0.11, L * 0.08, DEPTH * 0.22),
            (W * 0.80, L * 0.75, W * 0.08, L * 0.10, DEPTH * 0.32),
        ]
        for i, (rx, ry, rw, rl, rh) in enumerate(rock_configs):
            rock = Mesh(f"rock_{i}")
            _add_box(rock, rx, ry, W * 0.04, rw, rl, rh)
            meshes.append(rock)
            # rock cap (slightly smaller, rounded look)
            cap = Mesh(f"rock_cap_{i}")
            _add_box(cap, rx + rw * 0.1, ry + rl * 0.1, W * 0.04 + rh, rw * 0.8, rl * 0.8, rh * 0.3)
            meshes.append(cap)

        # ── Air bubbles column — vertical stack of small boxes rising up ───────
        for bi in range(6):
            bubble = Mesh(f"bubble_{bi}")
            bz = DEPTH * (0.1 + bi * 0.14)
            _add_box(bubble, W * 0.45, L * 0.45, bz, W * 0.015, W * 0.015, W * 0.015)
            meshes.append(bubble)

    elif design_type in ("desert", "dune", "arid"):
        ground = Mesh("desert_ground")
        _add_box(ground, 0.0, 0.0, 0.0, W, L, 0.3)
        meshes.append(ground)
        for i, (dx, dy, dh, dw, dl) in enumerate(
            [
                (W * 0.05, L * 0.1, H * 0.12, W * 0.3, L * 0.25),
                (W * 0.4, L * 0.05, H * 0.18, W * 0.25, L * 0.3),
                (W * 0.6, L * 0.5, H * 0.14, W * 0.35, L * 0.2),
                (W * 0.1, L * 0.65, H * 0.1, W * 0.2, L * 0.28),
            ]
        ):
            dune = Mesh(f"dune_{i}")
            _add_box(dune, dx, dy, 0.3, dw, dl, dh)
            meshes.append(dune)
        for i in range(3):
            ctx, cty = W * (0.2 + i * 0.3), L * (0.35 + (i % 2) * 0.2)
            trunk = Mesh(f"cactus_trunk_{i}")
            _add_box(trunk, ctx, cty, 0.3, W * 0.03, L * 0.02, H * 0.18)
            arm = Mesh(f"cactus_arm_{i}")
            _add_box(arm, ctx + W * 0.03, cty, H * 0.1, W * 0.05, L * 0.015, H * 0.08)
            meshes.append(trunk)
            meshes.append(arm)

    else:
        ground = Mesh("environment_ground")
        _add_box(ground, 0.0, 0.0, 0.0, W, L, 0.2)
        meshes.append(ground)
        feature = Mesh(design_type)
        _add_box(feature, W * 0.1, L * 0.1, 0.2, W * 0.8, L * 0.8, H * 0.5)
        meshes.append(feature)

    return meshes


# ── Main entry point ──────────────────────────────────────────────────────────


def generate_real_glb(spec_json: Dict[str, Any]) -> bytes:
    """
    Generate a GLB from spec_json["rooms"].

    Phase 2 guarantees:
      - Each room = enclosed volume (floor + ceiling + 4 thick walls)
      - Walls have real thickness (WALL_T = 0.25 m)
      - Rooms are spatially separated (GAP = WALL_T between them)
      - Adjacent rooms (from spec adjacency + spatial proximity) get door gaps
      - Bedroom ≠ Hall ≠ Kitchen — different dimensions, different positions
      - Raises ValueError if rooms list is empty (no dummy mesh)
    """
    domain = (spec_json.get("domain") or "architecture").lower()

    _DOMAIN_BUILDERS = {
        "vehicles": _build_vehicles_meshes,
        "objects": _build_objects_meshes,
        "gameplay": _build_gameplay_meshes,
        "environment": _build_environment_meshes,
    }

    if domain in _DOMAIN_BUILDERS:
        logger.info("generate_real_glb: domain=%s, type=%s", domain, spec_json.get("design_type"))
        all_meshes = _DOMAIN_BUILDERS[domain](spec_json)
        if not all_meshes:
            raise ValueError(f"Domain builder for '{domain}' produced no meshes")
        return pack_glb_multi_mesh(all_meshes)

    # Architecture (default) — room-based layout
    rooms: List[str] = spec_json.get("rooms") or []
    dimensions = spec_json.get("dimensions") or {}
    room_dims = spec_json.get("room_dimensions") or {}
    adjacency_spec = spec_json.get("adjacency") or {}
    stories = int(spec_json.get("stories") or 1)

    total_w = float(dimensions.get("width", 12.0) or 12.0)
    floor_h = float(dimensions.get("height", 2.8) or 2.8) / max(stories, 1)

    if not rooms:
        raise ValueError("Geometry generation failed: spec has no rooms defined")

    logger.info(
        "generate_real_glb: %d rooms, footprint=%.1fx%.1f, floor_h=%.1f, stories=%d",
        len(rooms),
        total_w,
        float(dimensions.get("length", 10.0) or 10.0),
        floor_h,
        stories,
    )

    layout = _layout_rooms(rooms, room_dims, total_w, floor_h, adjacency_spec)
    door_map = _compute_doors(layout, adjacency_spec)
    shared_map = _compute_shared_walls(layout)
    all_meshes: List[Mesh] = []

    for story in range(stories):
        z_offset = story * floor_h
        for idx, (room_name, rx, ry, rw, rl, rh) in enumerate(layout):
            d = door_map[idx]
            s = shared_map[idx]
            node_name = f"{room_name}_s{story}" if stories > 1 else room_name
            mesh = build_room_mesh(
                name=node_name,
                x=rx,
                y=ry,
                w=rw,
                l=rl,
                h=rh,
                z=z_offset,
                door_south=d["south"],
                door_north=d["north"],
                door_west=d["west"],
                door_east=d["east"],
                shared_south=s["south"],
                shared_north=s["north"],
                shared_west=s["west"],
                shared_east=s["east"],
            )
            all_meshes.append(mesh)

    logger.info("Geometry built: %d meshes (%d rooms x %d stories)", len(all_meshes), len(rooms), stories)
    return pack_glb_multi_mesh(all_meshes)
