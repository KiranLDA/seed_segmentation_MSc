import argparse
import requests
import zipfile
from tqdm import tqdm
from pathlib import Path
import json
import numpy as np
import math
import cv2 as cv

from src.synth.annotated_image import AnnotatedImage
from src.synth.synthesiser import synthesise

# Utility script to download labelled images and generate training datasets


def download_data(ip: str, auth_token: str, path: str, chunk_size: int = 8192) -> None:
    print("Connecting to label studio server\n")
    request = requests.get(
        f"http://{ip}/api/projects/9/export?exportType=COCO",  # TODO update URL for new label studio project
        headers={"Authorization": f"Token {auth_token}"},
        stream=True,
    )

    parent_dir = Path(f"{path}")
    file_dir = parent_dir / "data.zip"
    parent_dir.mkdir(parents=True, exist_ok=True)

    content_length = int(request.headers["Content-Length"])
    with open(file_dir, "wb") as file:
        print(f"Downloading data to {file_dir}")
        pbar = tqdm(unit="B", total=content_length)
        for chunk in request.iter_content(chunk_size=chunk_size):
            file.write(chunk)
            pbar.update(len(chunk))
        pbar.close()

    with zipfile.ZipFile(file_dir, "r") as zip_ref:
        print("Unzipping contents\n")
        zip_ref.extractall(path)


def clean_annotations(source, keep_ids: set):
    new_json = {}
    new_json["images"] = source["images"]

    new_json["categories"] = []
    category_map = {}
    category_counter = 0
    for category in source["categories"]:
        if category["id"] in keep_ids:
            category_map[category["id"]] = category_counter
            new_json["categories"].append(
                {"id": category_counter, "name": category["name"]}
            )
            category_counter += 1

    new_json["annotations"] = []
    for annotation in source["annotations"]:
        if annotation["category_id"] in keep_ids:
            annotation["category_id"] = category_map[annotation["category_id"]]
            new_json["annotations"].append(annotation)

    return new_json


def split_dataset(
    annotations,
    path,
    full_test_names: list[str],
    splits=[0.8, 0.1, 0.1],
    random_seed=42,
):
    np.random.seed(random_seed)
    ids = []
    full_test_ids = []
    for image in annotations["images"]:
        if image["file_name"] in full_test_names:
            full_test_ids.append(image["id"])
        else:
            ids.append(image["id"])
    np.random.shuffle(ids)

    N = len(ids)
    train_idx = math.floor(splits[0] * N)
    val_idx = train_idx + math.floor(splits[1] * N)
    train_ids = ids[0:train_idx]
    val_ids = ids[train_idx:val_idx]
    test_ids = ids[val_idx:]

    print(
        f"Splitting dataset\ntrain: {len(train_ids)}\nval: {len(val_ids)}\ntest: {len(test_ids)}\n"
    )

    train_annotations = get_subset(annotations, train_ids)
    val_annotations = get_subset(annotations, val_ids)
    test_annotations = get_subset(annotations, test_ids)
    full_test_annotations = get_subset(annotations, full_test_ids)

    path = Path(path)
    train_path = path / "train.json"
    val_path = path / "val.json"
    test_path = path / "test.json"
    full_test_path = path / "full_test.json"

    with open(train_path, "w") as file:
        json.dump(train_annotations, file, indent=4)

    with open(val_path, "w") as file:
        json.dump(val_annotations, file, indent=4)

    with open(test_path, "w") as file:
        json.dump(test_annotations, file, indent=4)

    with open(full_test_path, "w") as file:
        json.dump(full_test_annotations, file, indent=4)

    return train_annotations, val_annotations, test_annotations


def get_subset(annotations, image_ids):
    new_json = {}
    new_json["images"] = []
    new_json["annotations"] = []
    new_json["categories"] = annotations["categories"]

    for image_id in image_ids:
        for image in annotations["images"]:
            if image["id"] == image_id:
                new_json["images"].append(image)

        for annotation in annotations["annotations"]:
            if annotation["image_id"] == image_id:
                new_json["annotations"].append(annotation)

    return new_json


def get_annotated_images(path, annotations):
    for image_description in annotations["images"]:
        image_name = image_description["file_name"]
        image = cv.imread(f"{path}/{image_name}", cv.IMREAD_GRAYSCALE)
        image_id = image_description["id"]
        polygons = {}
        for annotation in annotations["annotations"]:
            if annotation["image_id"] == image_id:
                key = annotation["category_id"]
                if key not in polygons:
                    polygons[key] = []
                raw_poly = annotation["segmentation"][0]
                poly = [(x, y) for x, y in zip(raw_poly[0:-1:2], raw_poly[1::2])]
                polygons[key].append(poly)

        annotated_image = AnnotatedImage(image, polygons)
        yield annotated_image


def synthesise_images(
    path,
    annotations,
    synth_dir,
    annotation_name,
    max_seeds=50,
    num_synths=100,
    synth_width=1024,
    max_iter=100,
):
    image_output_path = Path(path) / synth_dir
    annotation_output_path = Path(path) / f"{annotation_name}.json"
    image_output_path.mkdir(parents=True, exist_ok=True)

    new_json = {}
    new_json["images"] = []
    new_json["annotations"] = []
    new_json["categories"] = annotations["categories"]

    print(f"Writing synthesised images to {image_output_path}\n")
    image_index = 0
    annotation_id = 0
    for source_image in tqdm(
        get_annotated_images(path, annotations),
        total=len(annotations["images"]),
        leave=False,
    ):
        for synth_image in synthesise(
            source_image, max_seeds, num_synths, synth_width, max_iter=max_iter
        ):
            if len(synth_image.polygons) == 0:
                print(
                    f"Skipping synthesised image {image_index} with no annotations. \n"
                )
                continue

            image_name = f"synth_{image_index}.jpg"
            cv.imwrite(f"{image_output_path}/{image_name}", synth_image.image)

            new_json["images"].append(
                {
                    "width": synth_width,
                    "height": synth_width,
                    "id": image_index,
                    "file_name": f"{synth_dir}{image_name}",
                }
            )

            annotations = []
            for key, polygons in synth_image.polygons.items():
                for polygon in polygons:
                    annotation = get_coco_annotation(
                        polygon, annotation_id, image_index, key
                    )
                    annotations.append(annotation)
                    annotation_id += 1

            new_json["annotations"].extend(annotations)

            image_index += 1

    print(f"Writing synthesised annotations to {annotation_output_path}")
    with open(annotation_output_path, "w") as output_file:
        json.dump(new_json, output_file, indent=4)


def get_coco_annotation(polygon, annotation_id: int, image_id: int, category_id: int):
    bbox_x, bbox_y, bbox_width, bbox_height = get_bbox(polygon)
    flattened_poly = flatten_poly(polygon)

    annotation = {
        "id": annotation_id,
        "image_id": image_id,
        "category_id": category_id,
        "segmentation": [flattened_poly],
        "bbox": [bbox_x, bbox_y, bbox_width, bbox_height],
        "ignore": 0,
        "iscrowd": 0,
        "area": bbox_width * bbox_height,
    }

    return annotation


def flatten_poly(polygon):
    flattened_poly = []
    for point in polygon:
        flattened_poly.append(point[0])
        flattened_poly.append(point[1])
    return flattened_poly


def get_bbox(polygon):
    min_x = min_y = math.inf
    max_x = max_y = -math.inf

    for point in polygon:
        if point[0] <= min_x:
            min_x = point[0]
        if point[0] >= max_x:
            max_x = point[0]
        if point[1] <= min_y:
            min_y = point[1]
        if point[1] >= max_y:
            max_y = point[1]

    return min_x, min_y, (max_x - min_x), (max_y - min_y)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "ip",
        action="store",
        help="current ip and port of the label studio server (e.g. 92.13.168.238:53305)",
        type=str,
    )
    parser.add_argument(
        "auth_token",
        action="store",
        help="user authentication token from labelstudio (e.g. e5961e1da194fe4e093ceb5c508ef68b2fc7fd21)",
        type=str,
    )
    parser.add_argument(
        "output_path",
        action="store",
        help="absolute path to download data to",
        type=str,
    )
    parser.add_argument(
        "--no-download",
        action="store_true",
        dest="no_download",
        help="skip dataset download",
    )

    args = parser.parse_args()

    if not args.no_download:
        download_data(args.ip, args.auth_token, args.output_path)

    with open(f"{args.output_path}/result.json") as json_file:
        annotations = json.load(json_file)

    cleaned_annotations = clean_annotations(
        annotations, keep_ids={5, 9, 10, 17, 19}
    )  # TODO update ids for new labelstudio project

    fully_labelled_images = [
        "images/0169f0f1-0999179_XRAY_1.jpg",
        "images/028ea71c-1002584_XRAY_1.jpg",
        "images/095135d2-0999766_XRAY_1.jpg",
        "images/8648e0f2-1002665_XRAY_1.jpg",
        "images/d1938e63-0992376_XRAY_1.jpg",
        "images/2426e558-1008368_XRAY_1.jpg",
        "images/4dc2605d-990903_XRAY_1.jpg",
        "images/013f7dd6-1039162_XRAY_1.jpg",
        "images/cda4dad3-0983279_XRAY_1.jpg",
        "images/fb8931da-0996673_XRAY_01.jpg",
        "images/7fb0e7ec-1078893_XRAY_1.jpg",
    ]

    train_annotations, val_annotations, test_annotations = split_dataset(
        cleaned_annotations, args.output_path, fully_labelled_images
    )
    synthesise_images(
        args.output_path, train_annotations, "synth_train_images/", "synth_train"
    )
    synthesise_images(
        args.output_path, val_annotations, "synth_val_images/", "synth_val"
    )

    synthesise_images(
        args.output_path, test_annotations, "synth_test_images/", "synth_test"
    )
