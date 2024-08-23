from matplotlib import pyplot as plt
import numpy as np
import cv2 as cv


class AnnotatedImage:
    """Represents a grayscale image and annotations (i.e. bounding boxes, polygons)"""

    def __init__(
        self,
        image: np.ndarray,
        polygons: dict[int, list[list[tuple[int, int]]]],
    ) -> None:
        self.image = image
        self.polygons = polygons
        self.primary_mask = self.set_primary_mask()

    def set_primary_mask(self) -> None:
        """Generate a mask of the union of all annotations"""
        mask = np.zeros_like(self.image, dtype=np.uint8)
        for polys in self.polygons.values():
            for poly in polys:
                poly_array = np.array([[x, y] for x, y in poly], dtype=np.int32)
                mask = cv.fillPoly(mask, [poly_array], 255)
        return mask

    def get_primary_mask(self) -> np.ndarray:
        """Get the image primary mask (e.g. seed outline)"""
        return self.primary_mask

    def get_height(self) -> int:
        """Get the image height"""
        return self.image.shape[0]

    def get_width(self) -> int:
        """Get the image width"""
        return self.image.shape[1]

    def display(self) -> None:
        """Display image and associated annotations"""
        fig, axs = plt.subplots(1, 2)
        axs[0].imshow(self.image, cmap="gray", vmin=0, vmax=255)
        axs[1].imshow(self.primary_mask, cmap="gray", vmin=0, vmax=255)

        for _, poly_value in self.polygons.items():
            for poly in poly_value:
                coords = poly.copy()
                coords.append(poly[0])
                xs, ys = zip(*coords)
                axs[0].plot(xs, ys)

        plt.show()
