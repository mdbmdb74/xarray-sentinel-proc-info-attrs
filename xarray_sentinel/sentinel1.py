import os.path
import typing as T
from xml.etree import ElementTree

import numpy as np
import xarray as xr

from xarray_sentinel import esa_safe

SPEED_OF_LIGHT = 299_792_458  # m / s


def open_gcp_dataset(filename):
    annotation = ElementTree.parse(filename)
    geolocation_grid_points = esa_safe.parse_geolocation_grid_points(annotation)
    time = []
    slant_range = []
    line = set()
    pixel = set()
    for ggp in geolocation_grid_points.values():
        if ggp["line"] not in line:
            time.append(np.datetime64(ggp["azimuthTime"]))
            line.add(ggp["line"])
        if ggp["pixel"] not in pixel:
            slant_range.append(ggp["slantRangeTime"] * SPEED_OF_LIGHT / 2)
            pixel.add(ggp["pixel"])
    shape = (len(time), len(slant_range))
    data_vars = {
        "latitude": (("time", "slant_range"), np.zeros(shape)),
        "longitude": (("time", "slant_range"), np.zeros(shape)),
        "height": (("time", "slant_range"), np.zeros(shape)),
        "height": (("time", "slant_range"), np.zeros(shape)),
        "height": (("time", "slant_range"), np.zeros(shape)),
        "incidenceAngle": (("time", "slant_range"), np.zeros(shape)),
        "elevationAngle": (("time", "slant_range"), np.zeros(shape)),
    }
    line = sorted(line)
    pixel = sorted(pixel)
    for ggp in geolocation_grid_points.values():
        for var in data_vars:
            j = line.index(ggp["line"])
            i = pixel.index(ggp["pixel"])
            data_vars[var][1][j, i] = ggp[var]

    ds = xr.Dataset(
        data_vars=data_vars,
        coords={
            "time": ("time", [np.datetime64(dt) for dt in sorted(time)]),
            "slant_range": ("slant_range", sorted(slant_range), {"unit": "m"}),
        },
    )
    return ds


def open_root_dataset(filename):
    manifest = esa_safe.open_manifest(filename)
    product_attrs, product_files = esa_safe.parse_manifest_sentinel1(manifest)
    product_attrs["groups"] = ["orbit"] + product_attrs["xs:instrument_mode_swaths"]
    return xr.Dataset(attrs=product_attrs)  # type: ignore


class Sentinel1Backend(xr.backends.common.BackendEntrypoint):
    def open_dataset(  # type: ignore
        self,
        filename_or_obj: str,
        drop_variables: T.Optional[T.Tuple[str]] = None,
        group: T.Optional[str] = None,
    ) -> xr.Dataset:
        if group is None:
            ds = open_root_dataset(filename_or_obj)
        elif group == "gcp":
            ds = open_gcp_dataset(filename_or_obj)
        return ds

    def guess_can_open(self, filename_or_obj: T.Any) -> bool:
        try:
            _, ext = os.path.splitext(filename_or_obj)
        except TypeError:
            return False
        return ext.lower() in {".safe"}
