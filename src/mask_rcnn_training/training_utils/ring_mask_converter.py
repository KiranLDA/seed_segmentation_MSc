import torch
from torchvision.tv_tensors._image import Image
#from matplotlib import pyplot as plt

def get_total_mask(image: torch.tensor, masks: torch.tensor, labels: torch.tensor, label_order: torch.tensor, binary_threshold: float=0.5) -> torch.tensor:
    """
    Combine all the masks of the same label into one aggregated mask, for each unique label.
    Args:
        image: image tensor of shape (3, height, width)
        masks: a tensor of masks representing objects in the image of shape (num_masks, height, width)
        labels: a tensor of integers each representing a mask label of shape (num_masks, )
        label_order: an ordering (does not work with partial ordering) of integer label precedence from lowest to highest (i.e. outside to inside)
        binary_threshold: the number above which the mask should be considered 1 when binarised to a bool (otherwise any region with value > 0 will become a 1)

    Returns:
        total_masks: a tensor of shape (classes, height, width), where the [0,:,:] represents the lowest priority total mask
    """
    device = masks.device
    label2id = dict([(int(label), i) for i, label in enumerate(label_order)])
    total_masks = torch.zeros(size=(len(label_order), image.shape[1], image.shape[2])).to(device)
    for i in range(len(masks)):
        j = label2id[int(labels[i])]
        total_masks[j,:,:] = total_masks[j,:,:].bool() | (masks[i,:,:] > binary_threshold)
    return total_masks
    
def get_anti_mask(image: torch.tensor, masks: torch.tensor, labels: torch.tensor, label_order: torch.tensor, binary_threshold: float=0.5) -> torch.tensor:
    """
    Create an anti-mask for each label which determines where an object is NOT 
    i.e. for each mask with a particular label, remove from the mask any pixels contained in the anti-mask.

    Args:
        image: image tensor of shape (3, height, width)
        masks: a tensor of masks representing objects in the image of shape (num_masks, height, width)
        labels: a tensor of integers each representing a mask label of shape (num_masks, )
        label_order: an ordering (does not work with partial ordering) of integer label precedence from lowest to highest (i.e. outside to inside)
        binary_threshold: a float. when a mask pixel is above this value, the pixel is classified as a positive example, else the pixel is assumed to be of a different or background class

    Returns:
        out_masks: a tensor of shape (classes, height, width) where classes is the number of unique labels, and the [0,:,:] mask corresponds to the [0] element of label_order
    """
    total_masks = get_total_mask(image, masks, labels, label_order) # sorted in first dimension from lest precedence to most precedence
        
    out_masks = torch.zeros_like(total_masks)
    for i in range(len(label_order)):
        out_masks[i,:,:] = torch.any(total_masks[i+1:,:,:].view(-1, image.shape[1], image.shape[2]).bool(),dim=0)
    return out_masks

def remove_overlap(image: torch.tensor, masks: torch.tensor, labels: torch.tensor, label_order: torch.tensor, binary_threshold: float=0.5) -> torch.tensor:
    """ Remove the relevant anti-mask pixels from each mask in an image """
    anti_masks = get_anti_mask(image, masks, labels, label_order, binary_threshold)
    masks_out = torch.zeros_like(masks)
    label2id = dict([(int(key), i) for i, key in enumerate(label_order)])
    
    for i in range(len(masks)):
        # logical operation: where output mask pixels are those that are in the original mask and not the corresponding anti-mask
        j = label2id[int(labels[i])]
        masks_out[i,:,:] = (masks[i,:,:]>binary_threshold).bool() & ~anti_masks[j,:,:].bool()
        """
        if True: # displaying outputs for debugging purposes
            print(["Seed Coat", "Interior", "Endosperm", "Void"][labels[i]])
            fig, ax = plt.subplots(1, 4, sharex=True, sharey=True, dpi=200)
            
            ax[0].imshow(masks[i,:,:])
            ax[0].set_title("Mask")
            ax[0].axis('off')
            
            ax[1].imshow(anti_masks[j,:,:])
            ax[1].set_title("Anti-Mask")
            ax[1].axis('off')
            
            ax[2].imshow(masks_out[i,:,:])
            ax[2].set_title("Output")
            ax[2].axis('off')

            ax[3].imshow(image[2,:,:])
            ax[3].set_title("Image")
            ax[3].axis('off')
            
            plt.show()
        """
    return masks_out
    
def process(images: tuple[Image], targets: tuple[dict[str, torch.tensor]], label_order: torch.tensor):
    """ 
    Convert nested array of images and targets to correct format. Process targets to remove overlap.

    Args:
        images (tuple[torchvision.tv_tensors._image.Image]): a tuple containing many images
        targets (tuple[dict['boxes', 'masks', 'labels']]): all values are tensors

    Returns:
        images (tuple[torchvision.tv_tensors._image.Image]): a tuple containing many images
        targets (tuple[dict['boxes', 'masks', 'labels']]): all masks have overlap removed
    """
    out_images, out_targets = [], []
    for i in range(len(images)):
        out_images.append(images[i])
        if "scores" in targets[0].keys():
            out_targets.append({
                'boxes':targets[i]['boxes'],
                'masks':remove_overlap(images[i], targets[i]['masks'], targets[i]['labels'], label_order),
                'labels':targets[i]['labels'],
                'scores':targets[i]['scores']
                })
        else:
            out_targets.append({
                'boxes':targets[i]['boxes'],
                'masks':remove_overlap(images[i], targets[i]['masks'], targets[i]['labels'], label_order),
                'labels':targets[i]['labels']
                })
    return tuple(out_images), tuple(out_targets)