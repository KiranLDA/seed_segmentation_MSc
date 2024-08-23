from inference_utils.inference import Inferer
inferer = Inferer('src/mask_rcnn_training/configs/inference_configs.json')
#print(f"Training Configs: {inferer.training_configs}")
#print(f"Inference Configs: {inferer.inference_configs}")
print(inferer.evaluate())