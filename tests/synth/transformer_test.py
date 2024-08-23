import numpy as np
from src.synth.annotated_image import AnnotatedImage
from src.synth.transformer import Transformer
import albumentations as A


def test_transformer_can_flip_image():
    transformations = A.Compose([
        A.HorizontalFlip(always_apply=True)
    ], 
    keypoint_params=A.KeypointParams(
                    format="xy", label_fields=["class_labels"], remove_invisible=False
                ))
    transformer = Transformer(transformations)
    image = np.array([
        [0, 128, 0],
        [0, 128, 128],
        [0, 128, 0]
    ], dtype=np.uint8)
    polygons = {
        0:[[(1,0), (1,2), (1,1), (2,1), (1,1)]]
    }
    annotated_image = AnnotatedImage(image, polygons)

    transformed_image = transformer.transform(annotated_image)
    expected_image = image = np.array([
        [0, 128, 0],
        [128, 128, 0],
        [0, 128, 0]
    ], dtype=np.uint8)
    expected_primary_mask = np.array([
        [0, 255, 0],
        [255, 255, 0],
        [0, 255, 0]
    ], dtype=np.uint8)

    assert (transformed_image.image == expected_image).all()
    assert (transformed_image.get_primary_mask() == expected_primary_mask).all()
