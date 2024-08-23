from typing import Iterator
import numpy as np
from src.synth.annotated_image import AnnotatedImage
import cv2 as cv
import albumentations as A
from src.synth.compositor import Compositor
import random
import math

from src.synth.extractor import Extractor
from src.synth.transformer import Transformer


def synthesise(
    source: AnnotatedImage,
    max_seeds: int,
    num_out_images: int,
    out_image_width: int,
    max_iter: int = 100,
    overlap: float = 0,
) -> Iterator[AnnotatedImage]:
    """Synthesise seed images from the given source image

    Args:
        source: source image to use for synthesising new images
        max_seeds: number of seeds per synthesised image
        num_out_images: number of synthesised images to create
        out_image_widht: width (in pixels) of the synthesised images
        max_iter: maximum iterations to try and place an individual seed on the synthesised image canvas
        overlap: overlap allowed between seed regions

    Returns:
        Iterator over synthesised images
    """
    extractor = Extractor()
    extracted_seeds = extractor.extract(source)
    tmp = cv.bitwise_and(source.image, cv.bitwise_not(source.primary_mask))
    bg = np.percentile(tmp, 25)

    for _ in range(num_out_images):
        comp = Compositor(out_image_width, out_image_width, bg)
        num_seeds = random.randint(4, max_seeds)
        scale = math.floor(math.sqrt(num_seeds)) + 1

        transformations = [
            A.Flip(always_apply=True),
            A.SafeRotate(
                180, border_mode=cv.BORDER_CONSTANT, always_apply=True, value=bg
            ),
            A.RandomScale(scale_limit=0.2, always_apply=True),
            A.Affine(scale=0.75, always_apply=True, shear=(-15, 15), cval=bg),
            A.LongestMaxSize(out_image_width // scale, always_apply=True),
        ]

        transformer = Transformer(
            A.Compose(
                transformations,
                keypoint_params=A.KeypointParams(
                    format="xy", label_fields=["class_labels"], remove_invisible=False
                ),
            ),
        )

        final_transformations = [A.GaussNoise(always_apply=True)]
        final_transformer = Transformer(
            A.Compose(
                final_transformations,
                keypoint_params=A.KeypointParams(
                    format="xy", label_fields=["class_labels"], remove_invisible=False
                ),
            )
        )

        count = 0
        i = 0
        while count < num_seeds and i < max_iter:
            seed = extracted_seeds[random.randint(0, len(extracted_seeds) - 1)]
            image = transformer.transform(seed)
            x = np.random.randint(0, comp.width)
            y = np.random.randint(0, comp.height)
            if comp.can_place(x, y, image, allowed_overlap=overlap):
                comp.place(x, y, image)
                count += 1
            i += 1

        if np.random.rand() > 0.1:
            comp.add_petri()
            
        composite_image = comp.composite()
        final_image = final_transformer.transform(composite_image)
        
        yield final_image
