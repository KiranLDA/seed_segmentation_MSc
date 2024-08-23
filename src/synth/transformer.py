from src.synth.annotated_image import AnnotatedImage
import albumentations as A


class Transformer:
    """Applies a (sequence) of transformations to an annotated image"""

    def __init__(self, transformations: A.Compose) -> None:
        self.transformations = transformations

    def transform(self, annotated_image: AnnotatedImage) -> AnnotatedImage:
        """Transform a provided image"""

        image = annotated_image.image
        polygons = annotated_image.polygons

        keypoints, labels = self.get_keypoints(polygons)

        transformed = self.transformations(
            image=image, keypoints=keypoints, class_labels=labels
        )
        new_polygons = self.get_polygons(
            transformed["keypoints"], transformed["class_labels"]
        )
        new_image = AnnotatedImage(transformed["image"], new_polygons)
        return new_image

    def get_polygons(self, keypoints: list[tuple[int, int]], labels: list[str]):
        """Reconstitute polygons from labelled keypoints"""
        temp_polygons = {}
        for label, keypoint in zip(labels, keypoints):
            if label not in temp_polygons:
                temp_polygons[label] = []
            temp_polygons[label].append(keypoint)

        polygons = {}
        for k, v in temp_polygons.items():
            key = int(k.split("|")[0])
            if key not in polygons:
                polygons[key] = []
            polygons[key].append(v)

        return polygons

    def get_keypoints(self, polygons: dict[int, list[list[tuple[int, int]]]]):
        """Converted polygons into labelled keypoints to transform"""
        keypoints = []
        labels = []
        for key, polys in polygons.items():
            for i, poly in enumerate(polys):
                labels.extend([f"{key}|{i}"] * len(poly))
                keypoints.extend(poly)
        return keypoints, labels
