from PIL import Image
import numpy as np
from flask_server.app.models.rcnn import RCNN

# Replace 'PATH' with the actual path to your image file
image_path = '/vol/bitbucket/cdr23/dataset_final/images/2426e558-1008368_XRAY_1.jpg'
image = Image.open(image_path)
image = image.convert('L')
numpy_array = np.array(image)

model = RCNN()
print("Training Configs")
for key, value in model.training_configs.items():
    key = key + " "*(20 - len(key))
    print(f"\t{key}: \t\t {value}")
print("\n")
print("Inference Configs")
for key, value in model.inference_configs.items():
    key = key + " "*(20 - len(key))
    print(f"\t{key}: \t\t {value}")

response = model.predict(numpy_array)