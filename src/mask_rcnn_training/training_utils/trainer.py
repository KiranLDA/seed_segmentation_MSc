import torch
import torch.utils.data
from torchvision import datasets
from torchvision.transforms import v2
from src.mask_rcnn_training.training_utils.ring_mask_converter import process
from src.mask_rcnn_training.training_utils.utils import get_nvidia_gpu_memory, NestedTensorHandler, convert_labels#, print_structure
from src.mask_rcnn_training.training_utils.model_builder import get_model
from src.mask_rcnn_training.training_utils.plotting import compare_maps#, show_progress
import json
import gc
import time
import numpy as np
from torchmetrics.detection.mean_ap import MeanAveragePrecision as mAP
from matplotlib import pyplot as plt


class Trainer:
    def __init__(self, configs_path, full_init=True):
        if full_init:
            self.configs_path = configs_path
            self.configs = self.load_configs()
            self.hyper_params = self.load_hyper_params()
            self.check_configs()
            self.device = torch.device('cuda:0' if self.configs['use_gpu'] and torch.cuda.is_available() else 'cpu')
            self.train_loader = self.load_data(
                self.configs['train_images_path'],
                self.configs['train_annotations_name'],
                self.hyper_params['train_batch_size'],
            )
            self.val_loader = self.load_data(
                self.configs['val_images_path'],
                self.configs['val_annotations_name'],
                self.hyper_params['val_batch_size'],
            )
            self.model = self.load_model()
            self.training_log = dict([(key, []) for key in ['losses', 'train_maps', 'val_maps']])
            self.label_order, self.id2label, self.label2id, self.id2name, self.name2id, self.label2name, self.name2label = self.get_conversions()
            self.metric = mAP(
                class_metrics=True, 
                iou_type='segm', 
            ).to(self.device)
            self.write_configs_for_inference()
            self.metric.warn_on_many_detections = False


    def write_configs_for_inference(self):
        """ This function should write the minimal info that must be the same for inference and training into a single location."""
        inference_configs = dict()
        inference_configs['id2label'] = self.id2label
        inference_configs['label2id'] = self.label2id
        inference_configs['name2id'] = self.name2id
        inference_configs['id2name'] = self.id2name
        inference_configs['label2name'] = self.label2name
        inference_configs['name2label'] = self.name2label
        inference_configs['label_order'] = self.label_order.tolist()
        inference_configs['hyper_params'] = self.hyper_params
        inference_configs['num_classes'] = self.configs['num_classes']
        inference_configs['model_path'] = self.configs['model_path']
        inference_configs['class_order'] = self.configs['class_order']
        
        with open(self.configs['inference_configs_save_path'], 'w') as file:
            json.dump(inference_configs, file)
        print(f"Inference configs written to: {self.configs['inference_configs_save_path']}", flush=True)
        
    def check_keys(self):
        """ This function is only for testing! Some of the train loaders have an error which means they have no annotations and so no keys. This I am trying to catch."""
        for j, (images, targets) in enumerate(self.train_loader):
            for i in range(len(targets)):
                assert 'boxes' in targets[i].keys(), f"j: {j} i:{i} | keys:{targets[i].keys()} | values: {targets[i]['image_id']}"
                assert 'labels' in targets[i].keys(), f"j: {j} i:{i} | keys:{targets[i].keys()} | values: {targets[i]['image_id']}"
                assert 'masks' in targets[i].keys(), f"j: {j} i:{i} | keys:{targets[i].keys()} | values: {targets[i]['image_id']}"
        print("KEYS ARE CHILL")
        
    def load_configs(self):
        with open(self.configs_path, 'r') as file:
            configs = json.load(file)
        return configs

    def load_hyper_params(self):
        with open(self.configs['hyper_params_path'], 'r') as file:
            hyper_params = json.load(file)
        return hyper_params
    
    def check_configs(self):
        assert self.configs['train_print_every'] % self.configs['log_every'] == 0, f"Check configs file to make sure the printing frequency lines up with logging frequency. print_every: {self.configs['train_print_every']}. log_every: {self.configs['log_every']}"
        
    def load_data(self, folder_path, file_path, batch_size, shuffle=True):
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

    def load_model(self):
        if self.configs['load_from_checkpoint']:
            model = get_model(
                self.configs['num_classes'] + 1,
                max_detections=self.hyper_params['max_detections'],
                model_path=self.configs['model_path'],
            ).to(self.device)
        else:
            model = get_model(
                self.configs['num_classes'] + 1,
                max_detections=self.hyper_params['max_detections'],
                model_path=None
            ).to(self.device)
        return model

    def get_conversions(self):
        with open(self.configs['train_annotations_name'],'r') as file:
            categories = json.load(file)['categories']
        name2id = dict([(row['name'],row['id']) for row in categories])
        id2name = dict([(value, key) for key, value in name2id.items()])
        id_order = torch.tensor([name2id[name] for name in self.configs['class_order']]).to(self.device)
        id2label = dict([(int(key), i+1) for i, key in enumerate(id_order)])
        label_order = torch.tensor(sorted(list(id2label.values())))
        label2id = dict([(int(value),int(key)) for key, value in id2label.items()])
        label2name = dict([(int(label),id2name[label2id[int(label)]]) for label in label_order])
        name2label = dict([(val,key) for key, val in label2name.items()])
        return label_order, id2label, label2id, id2name, name2id, label2name, name2label

    def preprocess(self, images, targets):
        targets = convert_labels(targets, self.id2label)
        if self.hyper_params['pre-process']:
            images, targets = process(images, targets, self.label_order)
        images = NestedTensorHandler.get_structure_on_device(images, self.device)
        targets = NestedTensorHandler.get_structure_on_device(targets, self.device)
        return images, targets

    def postprocess(self, images, preds):
        if self.hyper_params['post-process']:
            images, preds = process(images, preds, self.label_order)
            return list(images), list(preds)
        else:
            return images, preds

    def plot_outputs(self, epoch, image=None):
        if image is None:
            images, targets = next(iter(self.val_loader))
            images, targets = self.preprocess(images, targets)
            preds = self.predict_internal(images[0:1])
            image = images[0]
            if len(image.shape) == 3:
                image = image.mean(dim=0)
            elif len(image.shape) == 4:
                image = image.mean(dims=(0,1))
            image = image.cpu()
        else:
            preds = self.predict_internal([image.to(self.device)])
            image = image.cpu()
        unique_labels = torch.unique(preds[0]['labels'])
    
        fig, ax = plt.subplots(len(unique_labels), figsize=(4, 4*len(unique_labels)), squeeze=False)
            
        for i, label in enumerate(unique_labels):
            im = preds[0]['masks'][preds[0]['labels'] == label].sum(dim=0).cpu().numpy()
            alpha = np.where(im == 0, 0, 0.5).astype(np.float64)
            ax[i, 0].imshow(image, cmap='gray')
            ax[i, 0].imshow(im, cmap='spring', alpha=alpha)
            ax[i, 0].axis('off')
            ax[i, 0].set_title(f"{self.id2name[self.label2id[int(label.item())]]}")
        plt.savefig(f"{self.configs['vis_plot_path']}{epoch}.png", dpi=300, format='png')

    def log_training_info(self, logging_info):
        images_train = logging_info['images_train']
        targets_train = logging_info['targets_train']
        loss  = logging_info['loss']
        
        images_val, targets_val = next(iter(self.val_loader))
        images_val, targets_val = self.preprocess(images_val, targets_val)
        
        preds_val = self.predict_internal(images_val)
        preds_train = self.predict_internal(images_train)

        train_map = self.evaluate_map(preds_train, targets_train)
        val_map = self.evaluate_map(preds_val, targets_val)

        iter_info = dict([
            ('losses',loss),
            ('train_maps',train_map),
            ('val_maps',val_map),
        ])

        for key, value in iter_info.items():
            self.training_log[key].append(value)
        
    def evaluate_map(self, preds, targets):
        targets = self.format_for_metric(list(targets))
        preds = self.format_for_metric(preds)
        #print(f"Preds Shapes: {[preds[0][key].shape for key in preds[0].keys()]}")
        #print(f"Preds: {print_structure(preds)}")
        #print(f"Targs: {print_structure(targets)}")
        return self.metric(preds, targets)

    def format_for_metric(self, preds: list[dict[str, torch.Tensor]]) -> list[dict[str, torch.Tensor]]:
        for i in range(len(preds)):
            preds[i]['masks'] = (preds[i]['masks'] > self.hyper_params['binary_threshold']).to(self.device).to(torch.uint8).view(-1, preds[i]['masks'].shape[-2], preds[i]['masks'].shape[-1])
            preds[i]['boxes'] = preds[i]['boxes'].to(torch.int64)
        return preds

    def print_training_info(self):
        train_map = self.training_log['train_maps'][-1]
        val_map = self.training_log['val_maps'][-1]
        print("Training Performance")
        for map_, label in zip(train_map['map_per_class'], train_map['classes']):
            name = self.label2name[int(label)]
            name = name + (12-len(name))*" "
            print(f"\t{name}:\t{map_:1.4f}")
        print("Validation Performance")
        for map_, label in zip(val_map['map_per_class'], val_map['classes']):
            name = self.label2name[int(label)]
            name = name + (12-len(name))*" "
            print(f"\t{name}:\t{map_:1.4f}")
        print("\n", flush=True)
        
    def plot_training_vs_validation(self):
        compare_maps(
            [value['map'].item() for value in self.training_log['train_maps']], 
            [value['map'].item() for value in self.training_log['val_maps']], 
            self.configs['map_plot_path'],
        )

    def save_model(self, epoch=None):
        if self.configs['save_progress']:
            if 'model_folder' not in self.configs.keys():
                torch.save(self.model.state_dict(), self.configs['model_path'])
            else:
                torch.save(self.model.state_dict(), self.configs['model_folder'] + f"epoch{epoch}.pt")

    def offload_memory(self):
        gc.collect()
        torch.cuda.empty_cache()

    def predict_internal(self, images):
        was_training = self.model.training
        self.model.eval()
        with torch.no_grad():
            preds = self.model(images)
        if was_training:
            self.model.train()
        #print(print_structure(preds))
        images, preds = self.postprocess(images, preds)
        #print(print_structure(preds))
        preds = self.format_for_metric(preds)
        return preds

    def full_evaluation(self):
        stores = dict([(key, []) for key in self.configs['class_order']])
        stores['Average'] = []
        for i, (images, targets) in enumerate(self.val_loader):
            if i % self.configs['val_print_every'] == 0:
                print(f"Val Iter: {i}/{len(self.val_loader)} ")
            images, targets = self.preprocess(images, targets)
            preds = self.predict_internal(images)
            maps = self.evaluate_map(preds, targets)
            for key, map_ in zip(maps['classes'].tolist(), maps['map_per_class'].tolist()):
                stores[self.label2name[int(key)]].append(map_)
            stores['Average'].append(maps['map'].item())
        output = dict([(key, float(np.mean(value))) for key, value in stores.items()])
        return output

    def print_end_of_epoch_info(self):
        print("#####\tEND OF EPOCH\t#####")
        performance_dict = self.full_evaluation()
        for key, value in performance_dict.items():
            print(f"\t{key}:\t{value:1.4f}")
        print(" ", flush=True)
    
    def train(self):
        optimizer = torch.optim.Adamax(self.model.parameters(), lr=self.hyper_params['learning_rate'])
        logging_info = dict()
        start_time = time.time()
        for epoch in range(self.hyper_params['num_epochs']):
            for i, (images, targets) in enumerate(self.train_loader):
                self.model.train()

                images, targets = self.preprocess(images, targets)
                loss_dict = self.model(images, targets)
                loss = sum(tuple([loss for loss in loss_dict.values()]))
                loss.backward()
                if (i+1) % self.hyper_params['step_every'] == 0 or (i+1) == len(self.train_loader):
                    optimizer.step()
                    optimizer.zero_grad()
                mem = get_nvidia_gpu_memory()[0]['used']

                if i % self.configs['log_every'] == 0 or (i+1) == len(self.train_loader):
                    logging_info['iter'] = i
                    logging_info['images_train'] = images
                    logging_info['targets_train'] = targets
                    logging_info['loss'] = loss.item()
                    self.offload_memory()
                    self.log_training_info(logging_info)
                    
                    delta_t = time.time() - start_time
                    start_time = time.time()
                    mins = int(delta_t // 60)
                    secs = int(delta_t - 60 * mins)
                    print(f"Epoch: {epoch} | Iter: {i} | Loss: {loss.item():1.3f} | Peak Memory: {mem}MiB | Iter Duration: {mins} mins {secs} secs", flush=True)

                if i % self.configs['train_print_every'] == 0 or (i+1) == len(self.train_loader):
                    self.print_training_info()
                self.offload_memory()
                
                    
            # Evaluate performance at end of epoch
            self.plot_outputs(epoch)
            self.save_model(epoch)
            self.plot_training_vs_validation()
            self.print_end_of_epoch_info()







