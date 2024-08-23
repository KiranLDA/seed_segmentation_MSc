from matplotlib import pyplot as plt
import matplotlib.patches as patches
import torch
import numpy as np

class NestedTensorHandler:
    @staticmethod
    def to_device(item, device):
        """Recursively send tensors to the specified device in the nested structure."""
        if isinstance(item, torch.Tensor):
            # Move tensor to the specified device
            return item.to(device)
        elif isinstance(item, dict):
            # Recursively process dictionary items
            return {k: NestedTensorHandler.to_device(v, device) for k, v in item.items()}
        elif isinstance(item, list):
            # Recursively process list items
            return [NestedTensorHandler.to_device(i, device) for i in item]
        elif isinstance(item, tuple):
            # Recursively process tuple items and convert it back to tuple
            return tuple(NestedTensorHandler.to_device(i, device) for i in item)
        else:
            # Return the item as is if it's not a tensor, list, dict, or tuple
            return item
    @staticmethod
    def get_structure_on_device(nested_structure, device='cpu'):
        """Return the nested structure with tensors moved to the specified device."""
        return NestedTensorHandler.to_device(nested_structure, device)

def compare_maps(train_maps, val_maps, save_path):
    iters = np.arange(len(train_maps))
    plt.figure(figsize=(5,5), dpi=100)
    plt.plot(iters, train_maps, 'x', label='Train')
    plt.plot(iters, val_maps, 'x', label='Val')
    plt.xlim(0, max(len(iters)-1, 1))
    plt.ylim(0, 1)
    plt.xlabel('Iteration')
    plt.ylabel('Mean Average Precision')
    plt.legend()
    plt.savefig(save_path)
    plt.close('all')

def get_total_masks(masks, labels, label_order):
    num_classes = len(label_order) + 1
    device = masks.device
    total_masks = torch.zeros(size=(num_classes, masks.shape[1], masks.shape[2])).to(device)

    for i in range(len(labels)):
        j = labels[i]
        total_masks[j,:,:] = total_masks[j,:,:].bool() | masks[i,:,:].bool()
    return total_masks

def show_image(image, path):
    im = image.detach().cpu().numpy().transpose(1, 2, 0)
    plt.imshow(im, cmap=None)
    plt.savefig(path)

def show_progress(image, target, pred, path, label_order, label2name):
    
    image = image.cpu()
    target = NestedTensorHandler.get_structure_on_device(target,'cpu')
    pred = NestedTensorHandler.get_structure_on_device(pred,'cpu')
    num_masks = len(label_order)
    total_masks_target = get_total_masks(target['masks'], target['labels'], label_order)
    total_masks_pred = get_total_masks(pred['masks'].squeeze(1), pred['labels'], label_order)

    fig, ax = plt.subplots(2,1+num_masks,sharex=True, sharey=True, dpi=500, figsize=(3*(1+num_masks),6))
    
    cmap_im = None
    cmap_mask = 'jet'

    # display original image
    im = image.detach().cpu().numpy().transpose(1, 2, 0)
    im = (im - im.min()) / (im.max() - im.min())

    ax[0,0].imshow(im,cmap=cmap_im)
    ax[1,0].set_title('BBoxes - Orig')
    
    ax[1,0].imshow(im,cmap=cmap_im)
    ax[0,0].set_title('BBoxes - Pred')

    for j in range(1, num_masks + 1):
        maps = total_masks_pred[j,:,:].numpy()
        ax[0,j].imshow(im,cmap=cmap_im)
        ax[0,j].imshow(maps,cmap=cmap_mask, alpha=0.5)
        
        class_ = label2name[j]
        ax[0,j].set_title(f"Pred: {class_}")

    for j in range(1, num_masks + 1):
        maps = total_masks_target[j,:,:].numpy()
        ax[1,j].imshow(im,cmap=cmap_im)
        ax[1,j].imshow(maps,cmap=cmap_mask, alpha=0.5)
        
        class_ = label2name[j]
        ax[1,j].set_title(f"Target: {class_}")

    for j in range(len(pred['boxes'])):
        x1, y1, x2, y2 = pred['boxes'][j].cpu().numpy()
        rect = patches.Rectangle((x1, y1), x2-x1, y2-y1, linewidth=1, edgecolor='r', facecolor='none')
        ax[0,0].add_patch(rect)

    for j in range(len(target['boxes'])):
        x1, y1, x2, y2 = target['boxes'][j].cpu().numpy()
        rect = patches.Rectangle((x1, y1), x2-x1, y2-y1, linewidth=1, edgecolor='w', facecolor='none')
        ax[1,0].add_patch(rect) 
    
    for i in range(2):
        for j in range(1+num_masks):
            ax[i,j].axis('off')

    cbar_ax = fig.add_axes([0.92, 0.15, 0.015, 0.75])  # [left, bottom, width, height]
    norm = plt.Normalize(vmin=0, vmax=1)
    plt.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap_mask), cax=cbar_ax)

    plt.savefig(path, bbox_inches='tight')
    plt.show()