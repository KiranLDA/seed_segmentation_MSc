from flask_server.app.routes.responses import get_base64_encoding, add_transparency
import numpy as np


def test_get_base64_encoding():
    image = np.zeros((50, 50), dtype=np.uint8)
    image[0:25, 0:25] = 255
    image[25:, 25:] = 255
    expected_encoding = (
        "iVBORw0KGgoAAAANSUhEUgAAAD"
        "IAAAAyCAAAAAA7VNdtAAAANElE"
        "QVR4nGP8z4ADMOKSYMIlgRuMah"
        "nVMqplVMug0oKzgGPAWSYOWr+M"
        "ahnVMqplVAuRAADI/QJiYhtRnw"
        "AAAABJRU5ErkJggg=="
    )  # implicitly concatenated into a single string
    actual_encoding = get_base64_encoding(image)

    assert actual_encoding == expected_encoding


def test_add_transparency():
    image = np.zeros((2, 2), dtype=np.uint8)
    image[0, 1] = 255 // 4
    image[1, 0] = 255 // 2
    image[1, 1] = 255

    expected_alpha = np.full_like(image, 128)
    expected_alpha[0, 0] = 0
    expected_image = np.dstack((image, expected_alpha))
    actual_image = add_transparency(image)

    assert (actual_image == expected_image).all()
