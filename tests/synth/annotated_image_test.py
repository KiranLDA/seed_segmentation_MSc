from src.synth.annotated_image import AnnotatedImage
import numpy as np


def test_get_primary_mask_returns_primary_mask():
    image = np.zeros((3, 3))
    polygons = {0: [[(0, 0), (0.5, 0), (0.5, 0.5), (0, 0.5)]]}
    annotated_image = AnnotatedImage(image, polygons)
    expected_mask = np.zeros_like(image)
    expected_mask[0, 0] = 255

    assert np.all(annotated_image.get_primary_mask() == expected_mask)


def test_get_height():
    image = np.zeros((3, 4))
    annotated_image = AnnotatedImage(image, {})

    assert annotated_image.get_height() == 3


def test_get_width():
    image = np.zeros((3, 4))
    annotated_image = AnnotatedImage(image, {})

    assert annotated_image.get_width() == 4
