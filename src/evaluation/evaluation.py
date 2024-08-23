from torchmetrics.detection.mean_ap import MeanAveragePrecision as mAP
from src.mask_rcnn_training.training_utils.ring_mask_converter import process
from src.mask_rcnn_training.training_utils.utils import NestedTensorHandler, convert_labels#, print_structure

from flask_server.app.routes.responses import ModelResponse
from torchvision.transforms import v2
from torchvision import datasets
import torch
import numpy as np
import gc

def format_response_for_eval(
    response: ModelResponse, 
    device: torch.device,
):
    annotlabel2label = dict([
        (0, 4), # Pod
        (1, 1), # Seed
        (2, 2), # Interior
        (3, 3), # Endosperm
        (4, 5), # Infestation
        (5, 4), # Void
        (6, 0), # Embryo
    ])
    #{1: 'Seed', 2: 'Interior', 3: 'Endosperm', 4: 'Void', 5: 'Infestation'}
    length = len(response.annotations)
    masks = torch.zeros(size=(length, response.height, response.width))
    boxes = torch.zeros(size=(length, 4))
    labels = torch.zeros(size=(length,))
    scores = torch.zeros(size=(length,))
    for i, annot in enumerate(response.annotations):
        masks[i] = torch.tensor(annot.mask)
        boxes[i] = torch.FloatTensor(annot.bbox)
        labels[i] = annotlabel2label[int(annot.label.value)]
        scores[i] = annot.confidence
    output = dict()
    output['masks'] = (masks > 0).to(device).to(torch.uint8)
    output['boxes'] = boxes.to(device).to(torch.int64)
    output['labels'] = labels.to(device).to(torch.int64)
    output['scores'] = scores.to(device)

    return output

def load_data(
    folder_path: str,
    file_path: str,
    batch_size: int,
    shuffle: bool=True
) -> torch.utils.data.DataLoader:
    transforms = v2.Compose([
        v2.ToImage(),
        v2.Grayscale(),
        v2.ToDtype(torch.float32, 
        scale=True),
    ])
    dataset = datasets.CocoDetection(
        folder_path, 
        file_path, 
        transforms=transforms
    )
    dataset = datasets.wrap_dataset_for_transforms_v2(
        dataset, 
        target_keys=["boxes", "labels", "masks"]
    )
    loader = torch.utils.data.DataLoader(
        dataset, 
        batch_size=batch_size, 
        collate_fn=lambda batch: tuple(zip(*batch)), 
        shuffle=shuffle,
        num_workers=4,
    )
    return loader

def preprocess(images, targets, label_order, device):
    id2label = {3: 1, 2: 2, 0: 3, 4: 4, 1: 5}
    targets = convert_labels(targets, id2label)
    images, targets = process(images, targets, label_order)
    images = NestedTensorHandler.get_structure_on_device(images, device)
    targets = NestedTensorHandler.get_structure_on_device(targets, device)
    return images, targets

def full_evaluation(
    model,
    test_folder: str,
    test_json: str,
    device: torch.device=torch.device('cuda:0' if torch.cuda.is_available() else 'cpu'),
    pred_func=lambda image, response: None,
    targ_func=lambda image, target, threshold, label2name: None,
) -> dict[str, float]:
    # this code is not efficient - keep the number of images small!
    device = torch.device('cpu')
    loader = load_data(
        folder_path=test_folder, 
        file_path=test_json, 
        batch_size=1, 
        shuffle=True
    )
    metric = mAP(
        class_metrics=True, 
        iou_type='segm', 
    ).to(device)
    
    mean_maps_list = []
    mean_maps_per_class_list = dict([(key, []) for key in range(7)])
    #label_order = torch.tensor([4, 5, 3, 1, 0, 2, 6])
    label_order = torch.tensor([0, 1, 2, 3, 4, 5, 6, 7])
    #label_order = torch.tensor([1, 2, 3, 4, 5])
    
    for i, (images, targets) in enumerate(loader):
        if i % 5 == 0:
            if i > 100:
                break
            print(i)
        images, targets = preprocess(images, targets, label_order, device)
        gc.collect()
        image = (images[0]*255).to(torch.uint8).cpu().numpy().squeeze()
        response = model.predict(image)
        pred = format_response_for_eval(response, device)
        pred = NestedTensorHandler.get_structure_on_device(pred, device)
        map_ = metric([pred], list(targets))
        mean_maps_list.append(map_['map'].item())
        for key, value in zip(map_['classes'].tolist(), map_['map_per_class'].tolist()):
            mean_maps_per_class_list[key].append(value)
        pred_func(image, response)
        targ_func(image, targets[0], 0.5, label2name={1: 'Seed', 2: 'Interior', 3: 'Endosperm', 4: 'Void', 5: 'Infestation'})
        #print(map_)
    return (dict([(key, np.mean(value)) for key, value in mean_maps_per_class_list.items() if len(value) > 0]) , np.mean(mean_maps_list))
    

if __name__ == "__main__":
    test_folder = "/vol/bitbucket/cdr23/dataset_final/"
    test_json = "/vol/bitbucket/cdr23/dataset_final/full_test.json"
    performance = full_evaluation(test_folder, test_json)
    print(performance)