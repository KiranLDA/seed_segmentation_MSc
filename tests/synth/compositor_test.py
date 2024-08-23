import numpy as np
from src.synth.annotated_image import AnnotatedImage
from src.synth.compositor import Compositor


def test_compositor_can_draw_image():
    image = np.array([[0, 255, 0], [255, 255, 255], [0, 255, 0]], dtype=np.uint8)
    polygons = {0: [[(1, 1), (1, 2), (1, 2.1)], [(2,1), (2.1,1.1), (2.1, 1.2)]]}
    annotated_image = AnnotatedImage(image, polygons)

    comp = Compositor(image.shape[1] + 1, image.shape[0] + 1, 128)
    comp.place(1, 1, annotated_image)

    expected_image = np.array(
        [
            [128, 128, 128, 128],
            [128, 128, 128, 128],
            [128, 128, 255, 255],
            [128, 128, 255, 128],
        ],
        dtype=np.uint8,
    )

    expected_mask = np.array([[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 255, 255], [0, 0, 255, 0]])
    composite_image = comp.composite()
    assert (composite_image.image == expected_image).all()
    assert (composite_image.get_primary_mask() == expected_mask).all()
    assert (len(composite_image.polygons[0]) == 2)


def test_empty_canvas_can_place():
    comp = Compositor(10, 10, 128)
    image = np.array([[255, 255], [255, 255]], dtype=np.uint8)
    polygons = {0: [[(0, 0), (1, 0), (1, 1), (0, 1)]]}
    annotated_image = AnnotatedImage(image, polygons)

    assert comp.can_place(3, 3, annotated_image) is True


def test_occupied_canvas_cannot_place():
    comp = Compositor(10, 10, 128)
    comp.primary_mask = np.full(comp.canvas.shape, 255, dtype=np.uint8)
    image = np.array([[255, 255], [255, 255]], dtype=np.uint8)
    polygons = {0: [[(0, 0), (1, 0), (1, 1), (0, 1)]]}
    annotated_image = AnnotatedImage(image, polygons)

    assert comp.can_place(3, 3, annotated_image) is False


def test_image_too_large_cannot_place():
    comp = Compositor(1, 2, 128)
    comp.background = 0
    image = np.array([[255, 255], [255, 255]])
    annotated_image = AnnotatedImage(image, {})

    assert comp.can_place(0, 0, annotated_image) is False
