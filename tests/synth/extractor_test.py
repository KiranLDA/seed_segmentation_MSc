import numpy as np

from src.synth.annotated_image import AnnotatedImage
from src.synth.extractor import Extractor


def test_extractor_can_extract_regions():
    image = np.array(
        [
            [0, 0, 0, 0, 0, 0],
            [0, 13, 13, 0, 0, 0],
            [0, 13, 13, 0, 0, 0],
            [0, 0, 0, 0, 13, 13],
        ],
        dtype=np.uint8,
    )
    polygons = {
        0: [[(1, 1), (2, 1), (2, 2), (1, 2)], [(4, 3), (5, 3), (5, 3.1)]],
    }

    annotated_image = AnnotatedImage(image, polygons)
    extractor = Extractor()
    extracted_images = extractor.extract(annotated_image)

    expected_image = np.array(
        [[0, 0, 0, 0], [0, 13, 13, 0], [0, 13, 13, 0], [0, 0, 0, 0]], dtype=np.uint8
    )
    expected_primary_mask = np.array(
        [[0, 0, 0, 0], [0, 255, 255, 0], [0, 255, 255, 0], [0, 0, 0, 0]], dtype=np.uint8
    )

    assert len(extracted_images) == 2
    assert (extracted_images[1].image == expected_image).all()
    assert (extracted_images[1].primary_mask == expected_primary_mask).all()
