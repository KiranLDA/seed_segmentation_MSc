from flask_server.app.routes.responses import (
    AnnotationLabel,
    ModelAnnotation,
)
import numpy as np
import pytest


class TestModelAnnotation:

    def test_get_hull_empty_mask(self):
        annotation = ModelAnnotation(
            bbox=[2.0, 2.0, 10.0, 10.0],
            mask=np.zeros((20, 20), dtype=np.uint8),
            label=AnnotationLabel.SEED,
            confidence=0.9,
            area=20.0,
            mean_intensity=255,
            seed_id=None,
        )

        expected_hull = np.zeros_like(annotation.mask)
        actual_hull = annotation.get_hull()

        assert (actual_hull == expected_hull).all()

    def test_get_hull_non_empty_mask(self):
        mask = np.zeros((20, 20), dtype=np.uint8)
        mask[1, 1] = 255
        mask[1, 3] = 255
        mask[3, 3] = 255
        mask[3, 1] = 255
        annotation = ModelAnnotation(
            bbox=[2.0, 2.0, 10.0, 10.0],
            mask=mask,
            label=AnnotationLabel.SEED,
            confidence=0.9,
            area=20.0,
            mean_intensity=255,
            seed_id=None,
        )

        expected_hull = np.zeros_like(annotation.mask)
        expected_hull[1:4, 1:4] = 255
        actual_hull = annotation.get_hull()

        assert (actual_hull == expected_hull).all()

    def test_overlap_self(self, get_single_annotation):
        annotation = get_single_annotation
        assert annotation.overlap(annotation) == pytest.approx(1.0)

    def test_overlap_disjoint_annotations(self, get_disjoint_annotations):
        annotation1, annotation2 = get_disjoint_annotations

        assert annotation1.overlap(annotation2) == pytest.approx(0.0)
        assert annotation2.overlap(annotation1) == pytest.approx(0.0)

    def test_bbox_overlap_self(self, get_single_annotation):
        annotation = get_single_annotation
        assert annotation.bbox_overlap(annotation) is True

    def test_bbox_overlap_disjoint(self, get_disjoint_annotations):
        annotation1, annotation2 = get_disjoint_annotations
        assert annotation1.bbox_overlap(annotation2) is False
        assert annotation2.bbox_overlap(annotation1) is False

    def test_to_json(self, get_single_annotation):
        annotation = get_single_annotation
        expected_json = {
            "bbox": [0.0, 0.0, 2.0, 2.0],
            "mask": ("iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAQAAAAnOwc2"
                     "AAAAHElEQVR4nGP838DAwMDA2MCABJgYsACsgoMQAACi"
                     "dwIGOFwavwAAAABJRU5ErkJggg=="),
            "label": 1,
            "confidence": 0.9,
            "area": 20.0,
            "mean_intensity": 255,
            "seed_id": None,
        }
        actual_json = annotation.to_json()

        assert actual_json == expected_json


@pytest.fixture
def get_single_annotation() -> ModelAnnotation:
    mask = np.zeros((10, 10), dtype=np.uint8)
    mask[0:3, 0:3] = 255
    annotation = ModelAnnotation(
        bbox=[0.0, 0.0, 2.0, 2.0],
        mask=mask,
        label=AnnotationLabel.SEED,
        confidence=0.9,
        area=20.0,
        mean_intensity=255,
        seed_id=0,
    )
    return annotation


@pytest.fixture
def get_disjoint_annotations() -> tuple[ModelAnnotation, ModelAnnotation]:
    mask1 = np.zeros((10, 10), dtype=np.uint8)
    mask1[0:3, 0:3] = 255
    mask2 = np.zeros_like(mask1)
    mask2[5:7, 5:7] = 255
    annotation1 = ModelAnnotation(
        bbox=[0.0, 0.0, 2.0, 2.0],
        mask=mask1,
        label=AnnotationLabel.SEED,
        confidence=0.9,
        area=20.0,
        mean_intensity=255,
        seed_id=0,
    )
    annotation2 = ModelAnnotation(
        bbox=[5.0, 5.0, 1.0, 1.0],
        mask=mask2,
        label=AnnotationLabel.SEED,
        confidence=0.9,
        area=20.0,
        mean_intensity=255,
        seed_id=1,
    )

    return annotation1, annotation2
