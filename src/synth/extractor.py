from src.synth.annotated_image import AnnotatedImage
import cv2 as cv


class Extractor:
    """Extracts seeds from annotated image"""

    def __init__(self) -> None:
        pass

    def extract(self, annotated_image: AnnotatedImage) -> list[AnnotatedImage]:
        """Extracts individual seeds from a given image

        Args:
            annotated_image: the image to extract seeds from

        Returns:
            A list of extracted seed images
        """
        primary_mask = annotated_image.primary_mask
        contours, _ = cv.findContours(
            primary_mask, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE
        )
        new_annotated_images = []
        for contour in contours:
            x, y, width, height = cv.boundingRect(contour)
            # Add 1 pixel padding
            x -= 1
            y -= 1
            width += 2
            height += 2
            new_image = annotated_image.image[y : y + height, x : x + width]
            new_polygons = self.get_contained_polygons(
                annotated_image.polygons, x, y, width, height
            )
            new_annotated_image = AnnotatedImage(new_image, new_polygons)
            new_annotated_images.append(new_annotated_image)
        return new_annotated_images

    def get_contained_polygons(
        self,
        polygons: dict[int, list[list[tuple[int, int]]]],
        bbox_x: int,
        bbox_y: int,
        bbox_width: int,
        bbox_height: int,
    ):
        """Get all the polygons within a given bounding box

        Args:
            polygons: list of polygons
            bbox_x: x-coordinate of bounding box top left corner
            bbox_y: y-coordinate of bounding box top left corner
            bbox_widht: bounding box width
            bbox_height: bounding box height

        Returns:
            Dictionary of all contained polygons, keyed by label
        """
        contained_polygons = {}
        for key, polys in polygons.items():
            for poly in polys:
                if self.in_bbox(poly, bbox_x, bbox_y, bbox_width, bbox_height):
                    if key not in contained_polygons:
                        contained_polygons[key] = []
                    new_poly = self.translate_polygon(poly, bbox_x, bbox_y)
                    contained_polygons[key].append(new_poly)
        return contained_polygons

    def translate_polygon(self, polygon: list[tuple[int, int]], x: int, y: int):
        """Returns a translated polygon"""
        new_poly = []
        for point in polygon:
            new_poly.append((point[0] - x, point[1] - y))
        return new_poly

    def in_bbox(self, polygon, bbox_x, bbox_y, bbox_width, bbox_height, eps=1e-9):
        """Test if a polygon is contained in a bounding box"""
        for point in polygon:
            if point[0] <= bbox_x - eps or point[0] >= bbox_x + bbox_width + eps:
                return False
            if point[1] <= bbox_y - eps or point[1] >= bbox_y + bbox_height + eps:
                return False
        return True
