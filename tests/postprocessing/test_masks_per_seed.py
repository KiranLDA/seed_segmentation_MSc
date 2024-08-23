from src.postprocessing.masks_per_seed import is_enclosed, count_seeds, outermost_seed_part, group_masks_by_seed
import torch
import pytest

@pytest.fixture
def get_sut():
    mask1 = torch.zeros(size=(4,10,10))
    mask1[0,1:9,1:9] = mask1[0,1:9,1:9] + 1
    mask1[1,1:6,1:6] = mask1[1,1:6,1:6] + 1
    mask1[2,4:9,4:9] = mask1[2,4:9,4:9] + 1
    mask1[3,4:9,1:6] = mask1[3,4:9,1:6] + 1

    mask2 = torch.zeros(size=(4,10,10))
    mask2[2,1:9,1:9] = mask2[2,1:9,1:9] + 1
    mask2[3,1:6,1:6] = mask2[3,1:6,1:6] + 1
    mask2[0,4:9,4:9] = mask2[0,4:9,4:9] + 1
    mask2[1,4:9,1:6] = mask2[1,4:9,1:6] + 1

    masks = [mask1, mask2, mask1, mask2]
    bbox1 = [98, 345, 240, 240]
    bbox2 = [88, 335, 300, 300]
    bbox3 = [700, 700, 240, 240]
    bbox4 = [108, 354, 220, 220]

    boxes = [bbox1, bbox2, bbox3, bbox4]

    annotations = {"masks": masks, "boxes": boxes, "labels": [2, 1, 2, 3] }
    hierarchy = {"Pod":0, "Seed": 1,"Interior": 2, "Endosperm": 3, "Infestation": 4, "Void":5}

    return (annotations, hierarchy)

def test_is_enclosed():
    bbox1 = [98, 345, 240, 240]
    bbox2 = [88, 335, 300, 300]
    bbox3 = [700, 700, 240, 240]
    assert is_enclosed(bbox1, bbox2)
    assert not is_enclosed(bbox2, bbox3)
    assert not is_enclosed(bbox2, bbox1)
    assert not is_enclosed(bbox3, bbox2)
    assert not is_enclosed(bbox3, bbox1)
    assert not is_enclosed(bbox1, bbox3)


def test_seed_count(get_sut):
    annotations, hierarchy = get_sut
    total_seeds, tf = count_seeds(annotations, hierarchy)
    assert(total_seeds == 2)
    assert(tf is True)

def test_outermost_seed_parts(get_sut):
    annotations, hierarchy = get_sut
    outermost_seed_parts = outermost_seed_part(annotations, hierarchy)
    expected_parts = [1,2]
    assert(expected_parts == outermost_seed_parts)

def test_group_masks_by_seed(get_sut):
    annotations, _ = get_sut
    masks_per_seed, _ = group_masks_by_seed(annotations)
    expected_masks_per_seed = {
        0: [1, 0, 3],
        1: [2],
    }
    assert(masks_per_seed == expected_masks_per_seed), f"masks_per_seed: {masks_per_seed} | expected: {expected_masks_per_seed}"