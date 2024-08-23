#import numpy as np
#import torch

def group_masks_by_seed(annotations):
    """ Gives the annotation indices grouped per seed.
    Args:
    annotations (dict of lists): includes labels, boxes, masks
    Returns:
    masks_per_seed (dict): dict per seed ID containing IDs and labels for sub-seed parts
    outermost_seed_parts (list): list of indicies from outermost seed parts (should be seed labels)
    """
    hierarchy = {"Pod":0, "Seed": 1,"Interior": 2, "Endosperm": 3, "Infestation": 4, "Void":5}
    total_seeds, more_interiors = count_seeds(annotations, hierarchy)

    if not more_interiors: # seed labels are always outermost mask
        outermost_seed_parts = [] # list of indexes for seed labels
        for j, bbox in enumerate(annotations['boxes']): 
            if annotations['labels'][j] == hierarchy["Seed"]: # 2 for seed label
                outermost_seed_parts.append(j) # if label for that box is seed coat, add to list
    else: # there is not a seed label for every seed
        outermost_seed_parts = outermost_seed_part(annotations, hierarchy)

    masks_per_seed = {}
    for seed_idx, i in zip(range(len(outermost_seed_parts)), outermost_seed_parts) : # gets the index 0- n for seeds
        masks_per_seed[seed_idx] = [i]
        for j, bboxes in enumerate(annotations['boxes']): # loop over every other bbox
            if is_enclosed(bboxes, annotations['boxes'][i]):
                masks_per_seed[seed_idx].append(j)
    return masks_per_seed, outermost_seed_parts

def outermost_seed_part(annotations, hierarchy):
    """ Checks for seed label, if there isn't one, go to the next highest priority seed part
    Args:
    annotations: list of labels, masks and bounding boxes for the predicitons / target annotations
    Return:
    outermost_seed_parts (list): list of indexes for the bounding boxes of outermost seed parts"""

    # returns a list of all outermost seed parts with idx for retrieiving
    outermost_seed_parts = [] # list of bounding boxes for outermost labels
    for j, bbox in enumerate(annotations['boxes']): 
            if annotations['labels'][j] == hierarchy["Seed"]: # 2 for seed label
                outermost_seed_parts.append(j) # if label for that box is seed coat, add to list
            elif annotations['labels'][j] == hierarchy["Interior"] and not any([is_enclosed(bbox, bboxes) for bboxes in annotations['boxes']]):
                # if it is an interior bbox and not enclosed by any other bounding box, add to list
                outermost_seed_parts.append(j) 
            elif annotations['labels'][j] == hierarchy["Endosperm"] and not any([is_enclosed(bbox, bboxes) for bboxes in annotations['boxes']]):
                # if it is an endosperm bbox and not enclosed by any other bounding box, add to list
                outermost_seed_parts.append(j) 
    return outermost_seed_parts
        
    
def is_enclosed(box1, box2):
    """
    Check if a smaller bounding box (box1) is enclosed by a larger bounding box (box2).
    Args:
    box1: Tuple representing coordinates of the smaller bounding box in the format (x1, y1, w1, h1). 
    x1, y1 = upper left; w1, h1 = width and height.
    box2: Tuple representing coordinates of the smaller bounding box in the format (x2, y2, w2, h2). 
    Returns:
    True if the smaller bounding box is enclosed by the larger bounding box, False otherwise.
    """
    x1, y1, w1, h1 = box1
    x2, y2, w2, h2 = box2
    return (x1>x2 and y1>y2 and x1+w1 < x2+w2 and y1+h1 < y2+h2)

def count_seeds(annotations, hierarchy):
    """Counts number of seed annotations and check they are the same as interiors
    Args: 
    annotations: predicitons / target 
    Returns:
    total_seeds (int): maximum of seed labels and interior labels
    (num_seeds<num_interiors) (Boolean): True if there are more interiors than seed labels
    """
    num_seeds = annotations['labels'].count(hierarchy["Seed"]) # count how many seed labels there are
    num_interiors = annotations['labels'].count(hierarchy["Interior"]) # count how many interior labels there are
    total_seeds = max(num_seeds, num_interiors) # num of actual seeds = max of seed labels and interior labels
    return total_seeds, (num_seeds<num_interiors)