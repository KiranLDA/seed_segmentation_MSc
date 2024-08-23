import torch
from torchvision.models.detection import maskrcnn_resnet50_fpn_v2
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from torchvision.models.detection.mask_rcnn import MaskRCNNPredictor

def get_model(num_classes, max_detections=200, model_path=None):
    # Load a pre-trained model for classification and return only the features
    model = maskrcnn_resnet50_fpn_v2(weights='DEFAULT')
    
    # Get the number of input features for the classifier
    in_features = model.roi_heads.box_predictor.cls_score.in_features
    
    # Replace the pre-trained head with a new one
    model.roi_heads.box_predictor = FastRCNNPredictor(in_features, num_classes)

    # Now get the number of input features for the mask classifier
    in_features_mask = model.roi_heads.mask_predictor.conv5_mask.in_channels
    hidden_layer = 256
    # And replace the mask predictor with a new one with new max_detections
    model.roi_heads.mask_predictor = MaskRCNNPredictor(in_features_mask, hidden_layer, num_classes)
    model.roi_heads.detections_per_img = max_detections
    
    # if a path is provided to load different model weights, use it
    if model_path is not None:
        model.load_state_dict(
            torch.load(
                model_path,
                map_location=torch.device('cpu'),
            )
        )
    return model