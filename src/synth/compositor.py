from src.synth.annotated_image import AnnotatedImage
import numpy as np
import cv2 as cv


class Compositor:
    """Composites annotated images into a new single image.
    Handles random placement on canvas and allowable overlaps"""

    def __init__(self, width: int, height: int, colour: np.uint8) -> None:
        self.width = width
        self.height = height
        self.background = colour
        self.canvas = np.full((height, width), colour, np.uint8)
        self.primary_mask = np.full((height, width), 0, np.uint8)
        self.polygons = {}

    def place(self, x: int, y: int, image: AnnotatedImage) -> None:
        """Place an annotated image on the canvas.

        Args:
            x: horizontal location of the placed image's top left corner on the canvas
            y: vertical location of the placed image's top left corner on the canvas
            image: The image to place

        Returns:
            None

        """
        image_width = image.get_width()
        image_height = image.get_height()

        region = self.canvas[y : y + image_height, x : x + image_width]
        primary_mask = image.get_primary_mask()
        primary_mask_inv = cv.bitwise_not(primary_mask)
        background = cv.bitwise_and(region, region, mask=primary_mask_inv)
        foreground = cv.bitwise_and(image.image, image.image, mask=primary_mask)
        self.canvas[y : y + image_height, x : x + image_width] = cv.add(
            foreground, background
        )

        self.primary_mask[y : y + image_height, x : x + image_width] = cv.add(
            self.primary_mask[y : y + image_height, x : x + image_width], primary_mask
        )

        for key, polys in image.polygons.items():
            if key not in self.polygons:
                self.polygons[key] = []
            for poly in polys:
                new_poly = [(poly_x + x, poly_y + y) for poly_x, poly_y in poly]
                self.polygons[key].append(new_poly)

    def can_place(
        self, x: int, y: int, image: AnnotatedImage, allowed_overlap=0.05
    ) -> bool:
        """Checks if an image can be placed on the canvas.

        Args:
            x: horizontal location of the placed image's top left corner on the canvas
            y: vertical location of the placed image's top left corner on the canvas
            image: the image to place
            allowed_overlap: the amount of allowed overlap between the candidate image mask
            and the existing canvas mask.

        Returns:
            Bool indicating whether the image can be placed at that location
        """
        image_width = image.get_width()
        image_height = image.get_height()

        if x + image_width > self.width or y + image_height > self.height:
            return False

        primary_mask_sum = image.primary_mask.sum()
        if primary_mask_sum > 0:
            overlap = (
                np.bitwise_and(
                    self.primary_mask[y : y + image_height, x : x + image_width],
                    image.primary_mask,
                ).sum(dtype=np.float64)
                / primary_mask_sum
            )
        else:
            overlap = 0.0
        if overlap > allowed_overlap:
            return False

        return True

    def composite(self) -> AnnotatedImage:
        """Composite all placed images into single image"""
        new = AnnotatedImage(self.canvas, self.polygons)
        return new

    def add_petri(self) -> None:
        """Add a synthesised petri dish to the composite image."""
        contours, _ = cv.findContours(
            self.primary_mask, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE
        )
        if len(contours) == 0:
            return

        hull = cv.convexHull(np.vstack(contours))
        (x, y), radius = cv.minEnclosingCircle(hull)
        centre = (
            int(x),
            int(y),
        )  # opencv uses int coords for centre and radius... bizarre
        radius = int(radius) + 1

        # Sample petri drawing values
        offset = np.random.randint(5, 100)
        thickness = np.random.randint(5, 60)
        aug_radius = radius + offset + thickness // 2
        tmp = cv.bitwise_and(self.canvas, self.primary_mask)
        colour = np.percentile(tmp, 98)
        petri_mask = cv.circle(np.zeros_like(self.canvas), centre, aug_radius, 255, -1)

        # Draw image background
        if self.canvas.min() > 0:
            background_colour = np.random.randint(0, self.canvas.min())
        else:
            background_colour = 0
        background = np.full_like(self.canvas, background_colour)
        new_background = cv.bitwise_and(
            background, background, mask=cv.bitwise_not(petri_mask)
        )
        foreground = cv.bitwise_and(self.canvas, self.canvas, mask=petri_mask)
        self.canvas = cv.add(new_background, foreground)

        # Draw petri dish border
        cv.circle(self.canvas, centre, aug_radius, colour, thickness)
        return
