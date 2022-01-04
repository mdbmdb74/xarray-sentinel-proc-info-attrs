import pathlib

import numpy as np
import pytest
import xarray as xr

from xarray_sentinel import esa_safe

DATA_FOLDER = pathlib.Path(__file__).parent / "data"


COMMON_ATTRIBUTES = {
    "constellation": "sentinel-1",
    "platform": "sentinel-1b",
    "instrument": ["c-sar"],
    "sat_orbit_state": "descending",
    "sat_absolute_orbit": 26269,
    "sat_relative_orbit": 168,
    "sat_anx_datetime": "2021-04-01T04:49:55.637823Z",
    "sar_frequency_band": "C",
    "sar_instrument_mode": "IW",
    "sar_polarizations": ["VV", "VH"],
    "sar_product_type": "SLC",
    "xs_instrument_mode_swaths": ["IW1", "IW2", "IW3"],
}


SENTINEL1_PRODUCTS = [
    (
        DATA_FOLDER
        / "S1B_IW_SLC__1SDV_20210401T052622_20210401T052650_026269_032297_EFA4.SAFE",
        "IW1",
        "VV",
    ),
    (
        DATA_FOLDER
        / "S1A_EW_SLC__1SDH_20210403T122536_20210403T122630_037286_046484_8152.SAFE",
        "EW1",
        "HH",
    ),
    (
        DATA_FOLDER
        / "S1B_IW_GRDH_1SDV_20210401T052623_20210401T052648_026269_032297_ECC8.SAFE",
        "IW",
        "VV",
    ),
]


def test_open_dataset_root() -> None:
    product_path = (
        DATA_FOLDER
        / "S1B_IW_SLC__1SDV_20210401T052622_20210401T052650_026269_032297_EFA4.SAFE"
    )
    res = xr.open_dataset(product_path, engine="sentinel-1")  # type: ignore

    assert isinstance(res, xr.Dataset)
    for attr_name in COMMON_ATTRIBUTES:
        assert attr_name in res.attrs
        assert res.attrs[attr_name] == COMMON_ATTRIBUTES[attr_name]

    res = xr.open_dataset(product_path)  # type: ignore

    assert isinstance(res, xr.Dataset)

    product_path = product_path / "manifest.safe"

    res = xr.open_dataset(product_path, engine="sentinel-1")  # type: ignore

    assert isinstance(res, xr.Dataset)

    res = xr.open_dataset(product_path)  # type: ignore

    assert isinstance(res, xr.Dataset)


@pytest.mark.parametrize("product_path,swath,pol", SENTINEL1_PRODUCTS)
def test_open_dataset_orbit(
    product_path: esa_safe.PathType,
    swath: str,
    pol: str,
) -> None:
    res = xr.open_dataset(product_path, engine="sentinel-1", group=f"{swath}/{pol}/orbit")  # type: ignore

    assert isinstance(res, xr.Dataset)
    assert set(res.dims) == {"axis", "azimuth_time"}
    assert set(res.variables) == {"azimuth_time", "axis", "velocity", "position"}


@pytest.mark.parametrize("product_path,swath,pol", SENTINEL1_PRODUCTS)
def test_open_dataset_attitude(
    product_path: esa_safe.PathType,
    swath: str,
    pol: str,
) -> None:
    res = xr.open_dataset(product_path, engine="sentinel-1", group=f"{swath}/{pol}/attitude")  # type: ignore

    assert isinstance(res, xr.Dataset)
    assert set(res.dims) == {"azimuth_time"}
    expected = {
        "azimuth_time",
        "roll",
        "pitch",
        "yaw",
        "q0",
        "q1",
        "q2",
        "q3",
        "wx",
        "wy",
        "wz",
    }
    assert set(res.variables) == expected


@pytest.mark.parametrize("product_path,swath,pol", SENTINEL1_PRODUCTS)
def test_open_dataset_gcp(
    product_path: esa_safe.PathType,
    swath: str,
    pol: str,
) -> None:
    res = xr.open_dataset(product_path, engine="sentinel-1", group=f"{swath}/{pol}/gcp")  # type: ignore

    assert isinstance(res, xr.Dataset)
    assert set(res.dims) == {"azimuth_time", "slant_range_time"}


def test_open_pol_dataset() -> None:
    product_path = (
        DATA_FOLDER
        / "S1B_IW_SLC__1SDV_20210401T052622_20210401T052650_026269_032297_EFA4.SAFE"
    )
    res = xr.open_dataset(product_path, engine="sentinel-1", group="IW1/VV")  # type: ignore

    assert isinstance(res, xr.Dataset)
    for attr_name in COMMON_ATTRIBUTES:
        assert attr_name in res.attrs
        assert res.attrs[attr_name] == COMMON_ATTRIBUTES[attr_name]

    assert set(res.dims) == {"line", "pixel"}
    assert set(res.variables) == {"measurement", "line", "pixel"}


@pytest.mark.xfail
def test_open_burst() -> None:
    product_path = (
        DATA_FOLDER
        / "S1B_IW_SLC__1SDV_20210401T052622_20210401T052650_026269_032297_EFA4.SAFE"
    )
    res = xr.open_dataset(product_path, engine="sentinel-1", group="IW1/R168-N471-E0118")  # type: ignore

    assert isinstance(res, xr.Dataset)
    for attr_name in COMMON_ATTRIBUTES:
        assert attr_name in res.attrs
        assert res.attrs[attr_name] == COMMON_ATTRIBUTES[attr_name]
    assert res.dims == {"slant_range_time": 21632, "azimuth_time": 1501}
    assert not np.all(np.isnan(res.VH))
    assert not np.all(np.isnan(res.VH))

    expected = {
        "VH",
        "VV",
        "slant_range_time",
        "azimuth_time",
        "line",
        "pixel",
    }
    assert set(res.variables) == expected


@pytest.mark.xfail
def test_open_burst_one_pol() -> None:
    product_path = (
        DATA_FOLDER
        / "S1B_IW_SLC__1SDV_20210401T052622_20210401T052650_026269_032297_EFA4.SAFE"
    )
    res = xr.open_dataset(product_path, engine="sentinel-1", group="IW2/R168-N473-E0107")  # type: ignore

    assert isinstance(res, xr.Dataset)
    for attr_name in COMMON_ATTRIBUTES:
        assert attr_name in res.attrs
        assert res.attrs[attr_name] == COMMON_ATTRIBUTES[attr_name]
    assert res.dims == {"slant_range_time": 25508, "azimuth_time": 1513}

    expected = {
        "VH",
        "slant_range_time",
        "azimuth_time",
        "line",
        "pixel",
    }
    assert set(res.variables) == expected


def test_open_calibration_dataset() -> None:
    annotation_path = (
        DATA_FOLDER
        / "S1B_IW_SLC__1SDV_20210401T052622_20210401T052650_026269_032297_EFA4.SAFE"
    )
    res = xr.open_dataset(annotation_path, engine="sentinel-1", group="IW1/VV/calibration")  # type: ignore

    assert isinstance(res, xr.Dataset)
    assert set(res.dims) == {"line", "pixel"}