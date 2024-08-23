import numpy as np
import PIL.Image
from matplotlib import pyplot as plt


label_png, img_png = 'label.png', 'img.png'
lbl = np.asarray(PIL.Image.open(label_png))
img = np.asarray(PIL.Image.open(img_png))

def get_sub_regions(img,lbl):
    labels = np.unique(lbl)
    output = []
    for label in labels:
        output.append((lbl==label)*img)
    return output

def show_all():
    classes = ['background','seed_coat','endosperm']
    for i, region in enumerate(get_sub_regions(img,lbl)):
        _ = plt.figure(figsize=(5,3),dpi=300)
        plt.imshow(region,'gray')
        plt.savefig(f'{classes[i]}.png')
        plt.show()
    plt.close('all')

if __name__ == "__main__":
    show_all()


