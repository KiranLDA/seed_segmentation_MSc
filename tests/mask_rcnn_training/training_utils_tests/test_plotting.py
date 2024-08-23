import torch
from millenium.src.mask_rcnn_training.training_utils.plotting import get_total_masks

def test_get_total_masks():
    mask1a = torch.tensor([[0,0,1],[0,0,1],[0,0,1]])
    mask1b = torch.tensor([[1,1,1],[0,0,0],[0,0,0]])
    mask2a = torch.tensor([[0,0,1],[0,0,1],[0,0,1]])
    mask2b = torch.tensor([[0,0,1],[1,1,1],[0,0,1]])
    masks = torch.zeros(size=(4, 3, 3))
    for i, mask in enumerate([mask1a,mask1b,mask2a,mask2b]):
        masks[i,:,:] = mask

    labels = torch.tensor([2,2,1,1])
    label_order = torch.tensor([1,2])

    out_masks = get_total_masks(masks, labels, label_order)
    expected_masks = torch.zeros(size=(3, 3, 3))
    expected_masks[2,:,:] = torch.tensor([[1,1,1],[0,0,1],[0,0,1]])
    expected_masks[1,:,:] = torch.tensor([[0,0,1],[1,1,1],[0,0,1]])
    
    assert torch.all(out_masks == expected_masks), f"Out: {out_masks} \n Expected: {expected_masks}"

if __name__ == "__main__":
    test_get_total_masks()
    
    

