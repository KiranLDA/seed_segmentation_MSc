import torch
from millenium.src.mask_rcnn_training.training_utils.ring_mask_converter import get_total_mask, get_anti_mask, remove_overlap

def test_get_total_mask():
    label_order = torch.tensor([14,11,31])
    labels = torch.tensor([11, 14, 31, 11])
    
    image = torch.zeros(size=(3, 10, 10))
    image[0,1:9,1:9] = image[0,1:9,1:9] + 1
    image[1,1:6,1:6] = image[1,1:6,1:6] + 1
    image[2,4:9,4:9] = image[2,4:9,4:9] + 1
    image[:,4:9,1:6] = image[:,4:9,1:6]*0 + 0.5

    masks = torch.zeros(size=(4,10,10))
    masks[0,1:9,1:9] = masks[0,1:9,1:9] + 1
    masks[1,1:6,1:6] = masks[1,1:6,1:6] + 1
    masks[2,4:9,4:9] = masks[2,4:9,4:9] + 1
    masks[3,4:9,1:6] = masks[3,4:9,1:6] + 1

    out_masks = get_total_mask(image, masks, labels, label_order, 0.5)
    expected_masks = torch.zeros(size=(3, 10, 10))
    expected_masks[0,:,:] = (masks[1,:,:] > 0.5).bool()
    expected_masks[1,:,:] = (masks[0,:,:] > 0.5).bool() | (masks[3,:,:] > 0.5).bool()
    expected_masks[2,:,:] = (masks[2,:,:] > 0.5).bool()

    assert all([o == e for o, e in zip(out_masks.shape, expected_masks.shape)]), f"Shape expected: {expected_masks.shape} \n Shape got: {out_masks.shape}"
    assert torch.all(out_masks == expected_masks)


def test_get_anti_mask():
    label_order = torch.tensor([14,11,31])
    labels = torch.tensor([11, 14, 31, 11])
    
    image = torch.zeros(size=(3, 10, 10))
    image[0,1:9,1:9] = image[0,1:9,1:9] + 1
    image[1,1:6,1:6] = image[1,1:6,1:6] + 1
    image[2,4:9,4:9] = image[2,4:9,4:9] + 1
    image[:,4:9,1:6] = image[:,4:9,1:6]*0 + 0.5

    masks = torch.zeros(size=(4,10,10))
    masks[0,1:9,1:9] = masks[0,1:9,1:9] + 1
    masks[1,1:6,1:6] = masks[1,1:6,1:6] + 1
    masks[2,4:9,4:9] = masks[2,4:9,4:9] + 1
    masks[3,4:9,1:6] = masks[3,4:9,1:6] + 1

    out_anti_masks = get_anti_mask(image, masks, labels, label_order, binary_threshold=0.5)

    expected_anti_masks = torch.zeros(size=(3, 10, 10))
    expected_anti_masks[0,:,:] = masks[0,:,:].bool()|masks[2,:,:].bool()|masks[3,:,:].bool()
    expected_anti_masks[1,:,:] = masks[2,:,:].bool()

    assert all([o == e for o, e in zip(out_anti_masks.shape, expected_anti_masks.shape)]), f"Shape expected: {expected_anti_masks.shape} \n Shape got: {out_anti_masks.shape}"
    assert torch.all(out_anti_masks == expected_anti_masks), f"Out Anti Masks: {out_anti_masks} \n Expected Anti Masks: {expected_anti_masks}"


def test_remove_overlap():
    label_order = torch.tensor([14,11,31])
    labels = torch.tensor([11, 14, 31, 11])
    
    image = torch.zeros(size=(3, 10, 10))
    image[0,1:9,1:9] = image[0,1:9,1:9] + 1
    image[1,1:6,1:6] = image[1,1:6,1:6] + 1
    image[2,4:9,4:9] = image[2,4:9,4:9] + 1
    image[:,4:9,1:6] = image[:,4:9,1:6]*0 + 0.5

    masks = torch.zeros(size=(4,10,10))
    masks[0,1:9,1:9] = masks[0,1:9,1:9] + 1
    masks[1,1:6,1:6] = masks[1,1:6,1:6] + 1
    masks[2,4:9,4:9] = masks[2,4:9,4:9] + 1
    masks[3,4:9,1:6] = masks[3,4:9,1:6] + 1

    out_masks = remove_overlap(image, masks, labels, label_order)
    expected_masks = torch.zeros(size=(4,10,10))
    expected_masks[0,:,:] = masks[0,:,:].bool()&~masks[2,:,:].bool()
    expected_masks[1,:,:] = masks[1,:,:].bool()&~(masks[0,:,:].bool()|masks[2,:,:].bool()|masks[3,:,:].bool())
    expected_masks[2,:,:] = masks[2,:,:].bool()
    expected_masks[3,:,:] = masks[3,:,:].bool()&~masks[2,:,:].bool()
    
    assert all([o == e for o, e in zip(out_masks.shape, expected_masks.shape)]), f"Shape expected: {expected_masks.shape} \n Shape got: {out_masks.shape}"
    assert torch.all(out_masks == expected_masks), f"Out Masks: {out_masks} \n Expected Masks: {expected_masks}"

if __name__ == "__main__":
    test_get_total_mask()
    test_get_anti_mask()
    test_remove_overlap()

    
    
    