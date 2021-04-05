
Data groups:

- SLC complex measurements by swath and burst
  - azimuth / time, slant_range as dimensions, polarisation as variables
  - azimuth / slant_range coordinates as distances instead of times for
    easier interpretation? (slant_range == two-ways-time * speed-of-light,
    azimuth as linear distance from ascending node?)
  - keep time coordinates as UTC, TAI, UT1 and elapsed time from ascending node (NOT PRESENT??)
- calibration information (azimuth / slant_range dimensions on a reduced grid)
- ground control points (azimuth / slant_range dimensions on one more reduced grid)
- de-ramping parameters
- kinematic description:
  - state vectors
  - quaternions
- antenna pattern
- Doppler centroid / Doppler rate
- incidence angle & Co. 

Not loaded:
- noise

Attributes:

- mission, acquisition, processing, etc

Conformance:

- CF conventions for the coordinates (with special attentions to time)
- STAC metadata for attributes with SAT and SAR extensions

High level requirements:

- support opening a swath when other swaths are missing (especially the tifs)


User experience
---------------

```python
>>> ds = xr.open_dataset("S1B_IW_SLC__1SDV_20210401T052622_20210401T052650_026269_032297_EFA4.SAFE/manifest.safe")
>>> ds = xr.open_dataset("S1B_IW_SLC__1SDV_20210401T052622_20210401T052650_026269_032297_EFA4.SAFE")
>>> ds
... instruction on what to do ...

>>> ds_gpc = xr.open_dataset("S1B_IW_SLC__1SDV_20210401T052622_20210401T052650_026269_032297_EFA4.SAFE", group="gpc")
```



```python
>>> ds = xr.open_dataset("S1B_IW_SLC__1SDV_20210401T052622_20210401T052650_026269_032297_EFA4.SAFE/annotations/s1b-iw1-slc-vv-20210401t052624-20210401t052649-026269-032297-004.xml")
```