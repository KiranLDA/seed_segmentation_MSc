import torch
import torch.utils.data
from src.mask_rcnn_training.training_utils.ring_mask_converter import process
from src.mask_rcnn_training.training_utils.utils import NestedTensorHandler, convert_labels
from src.mask_rcnn_training.training_utils.model_builder import get_model
import json

class Inferer:
    def __init__(self, configs_path):
        self.configs_path = configs_path
        self.inference_configs, self.training_configs = self.load_configs()
        self.hyper_params = self.training_configs['hyper_params']
        self.device = torch.device('cuda:0' if self.inference_configs['use_gpu'] and torch.cuda.is_available() else 'cpu')
        self.model = self.load_model()
        self.label_order, self.id2label, self.label2id, self.name2id, self.id2name, self.name2label, self.label2name = self.get_conversions()

    def load_configs(self):
        with open(self.configs_path, 'r') as file:
            inference_configs = json.load(file)
        with open(inference_configs['fixed_inference_configs_path'], 'r') as file:
            training_configs = json.load(file)
        return inference_configs, training_configs

    def load_model(self):
        return get_model(
            self.training_configs['num_classes'] + 1,
            max_detections=self.hyper_params['max_detections'],
            model_path=self.training_configs['model_path'],
        ).to(self.device)

    def predict_internal(self, images):
        self.model.eval()
        with torch.no_grad():
            preds = self.model(images)
        return preds

    def predict(self, images):
        images = NestedTensorHandler.get_structure_on_device(images, self.device)
        preds = self.predict_internal(images)
        images, preds = self.postprocess(images, preds)
        for i in range(len(preds)):
            preds = self.binarise(preds)
            preds[i]['labels'] = self.deconvert(preds[i]['labels'])
        return preds

    def deconvert(self, labels):
        return torch.tensor([self.label2id[int(label)] for label in labels])

    def binarise(self, preds):
        for i in range(len(preds)):
            preds[i]['masks'] = (preds[i]['masks'] > self.hyper_params['binary_threshold']).to(self.device)
        return preds

    def get_conversions(self):
        label_order = torch.tensor(self.training_configs['label_order'])
        id2label = dict([(int(key), int(value)) for key, value in self.training_configs['id2label'].items()])
        label2id = dict([(int(key), int(value)) for key, value in self.training_configs['label2id'].items()])
        name2id = dict([(str(key), int(value)) for key, value in self.training_configs['name2id'].items()])
        id2name = dict([(int(key), str(value)) for key, value in self.training_configs['id2name'].items()])
        name2label = dict([(str(key), int(value)) for key, value in self.training_configs['name2label'].items()])
        label2name = dict([(int(key), str(value)) for key, value in self.training_configs['label2name'].items()])
        return label_order, id2label, label2id, name2id, id2name, name2label, label2name
        
    def preprocess(self, images, targets):
        targets = convert_labels(targets, self.id2label)
        if self.hyper_params['pre-process']:
            images, targets = process(images, targets, self.label_order)
        images = NestedTensorHandler.get_structure_on_device(images, self.device)
        targets = NestedTensorHandler.get_structure_on_device(targets, self.device)
        return images, targets

    def postprocess(self, images, preds):
        if self.hyper_params['post-process']:
            return process(images, preds, self.label_order)
        else:
            return images, preds

    def evaluate_map(self, preds, targets):
        targets = self.mask_to_uint8_mask(list(targets))
        preds = self.mask_to_uint8_mask(preds)
        return self.metric(preds, targets)

    def mask_to_uint8_mask(self, preds: list[dict[str, torch.Tensor]]) -> list[dict[str, torch.Tensor]]:
        for i in range(len(preds)):
            preds[i]['masks'] = (preds[i]['masks'] > self.hyper_params['binary_threshold']).to(self.device).bool()
        return preds

            
            
            
        
