# TODO: fix module imports

""" import os
from src.dicom.dicom import read_dicom_file, get_pixel_spacing, save_as_jpeg
import pytest

@pytest.mark.skip("Rewrite so we're not testing external library")
def test_get_pixel_spacing():
    ds = read_dicom_file('test_xray.dcm')
    y_spacing, x_spacing = get_pixel_spacing(ds)
    assert((y_spacing, x_spacing) == (0.023597, 0.023597))

@pytest.mark.skip("Rewrite so we don't save a file")
def test_save_as_jpeg():
    ds = read_dicom_file('test_xray.dcm')
    output_path = 'test_output.jpg'
    save_as_jpeg(ds, output_path)
    assert(os.path.exists(output_path))
    os.remove(output_path) """