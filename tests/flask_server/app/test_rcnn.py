from flask_server.app.models.rcnn import RCNN
from flask_server.app.routes.responses import AnnotationLabel, ModelAnnotation, ModelResponse
import numpy as np
from torch import manual_seed
import pytest

@pytest.mark.skip("Disabled until RCNN binarises masks")
def test_rcnn():
    manual_seed(7) # this seed must be used, so that the random elements of the initialisation of the model are set such that the model predicts something given the image input below. In case of error relating to prediction of no masks / annot.mask.max() is not 255, you will need to adjust the seed value againt.
    image = np.zeros(shape=(199, 201), dtype=np.uint8)
    image[10:20, 10:20] = image[10:20, 10:20] * 0 + 1
    image[40:80, 40:80] = image[40:80, 40:80] * 0 + 1
    image[40:80, 120:160] = image[40:80, 40:80] * 0 + 1
    image[120:160, 40:80] = image[40:80, 40:80] * 0 + 1
    image[120:160, 120:160] = image[40:80, 40:80] * 0 + 1
    
    model = RCNN('tests/flask_server/app/test_rcnn_inference_configs.json')
    #print(model.inferer.configs)
    response = model.predict(image)
    assert isinstance(response, ModelResponse), f"Expected {ModelResponse} Got {type(response)}"
    assert response.width == image.shape[1], f"Expected {image.shape[1]} Got {response.width}"
    assert response.height == image.shape[0], f"Expected {image.shape[0]} Got {response.height}"
    assert isinstance(response.annotations, list), f"Expected {list} Got {type(response.annotations)}"
    for i, annot in enumerate(response.annotations):
        assert isinstance(annot, ModelAnnotation), f"Expected {ModelAnnotation} Got {type(response.annotations)}"
        assert isinstance(annot.bbox, list), f"Expected {list} Got {type(annot.bbox)}"
        assert len(annot.bbox) == 4, f"Expected {4} Got {len(annot.bbox)}"
        assert isinstance(annot.mask, np.ndarray), f"Expected {np.ndarray} Got {type(annot.mask)}"
        assert annot.mask.max() == 255, f"Expected {255} Got {annot.mask.max()}"
        assert annot.mask.min() == 0, f"Expected {0} Got {annot.mask.min()}"
        assert len(np.unique(annot.mask)) == 2, f"Expected {2} Got {len(np.unique(annot.mask))}"
        assert annot.mask.shape == image.shape, f"Expected {image.shape} Got {annot.mask.shape}"
        assert isinstance(annot.label, AnnotationLabel), f"Expected {AnnotationLabel} Got {type(annot.label)}"
    
