from flask_server.app.routes.responses import (
    AnnotationLabel,
    ModelAnnotation,
    ModelResponse,
)
import numpy as np
import pytest


class TestModelResponse:
    def test_get_composite_masks(self, get_response):
        expected_seed_mask = np.zeros((10, 10), dtype=np.uint8)
        expected_seed_mask[0:5, 0:5] = 255
        expected_seed_mask[4:9, 4:9] = 255
        expected_seed_mask[0:1, 9:] = 255

        expected_void_mask = np.zeros_like(expected_seed_mask)
        expected_void_mask[0:2, 0:2] = 255

        expected_endosperm_mask = np.zeros_like(expected_seed_mask)
        expected_endosperm_mask[4:, 4:5] = 255

        response = get_response
        actual_masks = response.get_composite_masks()

        assert (actual_masks[1] == expected_seed_mask).all()
        assert (actual_masks[3] == expected_endosperm_mask).all()
        assert (actual_masks[5] == expected_void_mask).all()

    def test_flatten_seed_indices(self, get_response):
        expected_seed_indices = [[0, 4], [1, 3], [2]]
        actual_seed_indices = get_response.flatten_seed_indices()

        assert expected_seed_indices == actual_seed_indices

    def test_to_json(self, get_response):
        expected_json = {
            "annotations": [
                {
                    "area": 25,
                    "bbox": [0, 0, 5, 5],
                    "confidence": 0.9,
                    "label": 1,
                    "mask": ("iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCA"
                             "QAAAAnOwc2AAAAGElEQVR4nGP838AABYxw"
                             "FhMDFkChIN0AAKKVAgoaXuLXAAAAAElFTk"
                             "SuQmCC"),
                    "mean_intensity": 255,
                    "seed_id": 0,
                },
                {
                    "area": 25,
                    "bbox": [4, 4, 5, 5],
                    "confidence": 0.9,
                    "label": 1,
                    "mask": ("iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCA"
                             "QAAAAnOwc2AAAAG0lEQVR4nGNgoD5ghDH+"
                             "N8CFGpiwqaRQECsAAOeSAgpfxj6uAAAAAE"
                             "lFTkSuQmCC"),
                    "mean_intensity": 255,
                    "seed_id": 1,
                },
                {
                    "area": 25,
                    "bbox": [9, 0, 1, 1],
                    "confidence": 0.9,
                    "label": 1,
                    "mask": ("iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCA"
                             "QAAAAnOwc2AAAAEklEQVR4nGNgwAD/GzDF"
                             "hhAAAB4iAYAXY1o9AAAAAElFTkSuQmCC"),
                    "mean_intensity": 255,
                    "seed_id": 2,
                },
                {
                    "area": 25,
                    "bbox": [4, 4, 1, 5],
                    "confidence": 0.9,
                    "label": 3,
                    "mask": ("iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCA"
                             "QAAAAnOwc2AAAAFUlEQVR4nGNgoCH434Bg"
                             "M2FTQAtBALHTAYqKUy/8AAAAAElFTkSuQm"
                             "CC"),
                    "mean_intensity": 255,
                    "seed_id": 1,
                },
                {
                    "area": 25,
                    "bbox": [0, 0, 2, 2],
                    "confidence": 0.9,
                    "label": 5,
                    "mask": ("iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCA"
                             "QAAAAnOwc2AAAAFUlEQVR4nGP43/C/gQEN"
                             "MKELDCUAAG/KAwFjGKDbAAAAAElFTkSuQm"
                             "CC"),
                    "mean_intensity": 255,
                    "seed_id": 0,
                },
            ],
            "composite_masks": {
                1: ("iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAQAAAAnOwc"
                    "2AAAALklEQVR4nGP838AABYxQ1v8GJgYMwIhNkIEBqy"
                    "AjwkyEdkYYE9lC4s3EKogVAADAdggQOEGCsQAAAABJR"
                    "U5ErkJggg=="),
                3: ("iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAQAAAAnOwc"
                    "2AAAAFUlEQVR4nGNgoCH434BgM2FTQAtBALHTAYqKUy"
                    "/8AAAAAElFTkSuQmCC"),
                5: ("iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAQAAAAnOwc"
                    "2AAAAFUlEQVR4nGP43/C/gQENMKELDCUAAG/KAwFjGK"
                    "DbAAAAAElFTkSuQmCC"),
            },
            "height": 10,
            "seed_indices": [[0, 4], [1, 3], [2]],
            "width": 10,
        }

        actual_json = get_response.to_json()
        assert expected_json == actual_json


@pytest.fixture
def get_response():
    seed1_mask = np.zeros((10, 10), dtype=np.uint8)
    seed1_mask[0:5, 0:5] = 255

    seed2_mask = np.zeros_like(seed1_mask)
    seed2_mask[4:9, 4:9] = 255

    seed3_mask = np.zeros_like(seed1_mask)
    seed3_mask[0:1, 9:] = 255

    void_mask = np.zeros_like(seed1_mask)
    void_mask[0:2, 0:2] = 255

    endosperm_mask = np.zeros_like(seed1_mask)
    endosperm_mask[4:, 4:5] = 255

    annotations = [
        ModelAnnotation(
            bbox=[0, 0, 5, 5],
            mask=seed1_mask,
            label=AnnotationLabel.SEED,
            confidence=0.9,
            area=25,
            mean_intensity=255,
            seed_id=None,
        ),
        ModelAnnotation(
            bbox=[4, 4, 5, 5],
            mask=seed2_mask,
            label=AnnotationLabel.SEED,
            confidence=0.9,
            area=25,
            mean_intensity=255,
            seed_id=None,
        ),
        ModelAnnotation(
            bbox=[9, 0, 1, 1],
            mask=seed3_mask,
            label=AnnotationLabel.SEED,
            confidence=0.9,
            area=25,
            mean_intensity=255,
            seed_id=None,
        ),
        ModelAnnotation(
            bbox=[4, 4, 1, 5],
            mask=endosperm_mask,
            label=AnnotationLabel.ENDOSPERM,
            confidence=0.9,
            area=25,
            mean_intensity=255,
            seed_id=None,
        ),
        ModelAnnotation(
            bbox=[0, 0, 2, 2],
            mask=void_mask,
            label=AnnotationLabel.VOID,
            confidence=0.9,
            area=25,
            mean_intensity=255,
            seed_id=None,
        ),
    ]
    response = ModelResponse(annotations, 10, 10)
    return response
