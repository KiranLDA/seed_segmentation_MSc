import pydicom
from PIL import Image

def read_dicom_file(filepath):
    """Read a DICOM file."""
    return pydicom.dcmread(filepath)

def get_pixel_spacing(ds):
    """Extract pixel spacing from DICOM metadata."""
    pixel_spacing = ds.PixelSpacing
    return pixel_spacing[0], pixel_spacing[1]  # y_spacing, x_spacing

def save_as_jpeg(ds, output_path):
    """Convert DICOM to JPEG format."""
    pixel_array = ds.pixel_array

    # Normalize pixel array to 8-bit if necessary
    if pixel_array.max() > 255:
        pixel_array = (255 * (pixel_array / pixel_array.max())).astype('uint8')

    image = Image.fromarray(pixel_array)
    image.save(output_path)