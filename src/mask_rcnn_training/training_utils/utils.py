import torch
import subprocess
#import typing

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

def get_nvidia_gpu_memory():
    try:
        result = subprocess.run(['nvidia-smi', '--query-gpu=memory.total,memory.used,memory.free', '--format=csv,noheader,nounits'], capture_output=True, text=True)
        if result.returncode == 0:
            memory_info = result.stdout.strip().split('\n')
            memory_info = [x.split(', ') for x in memory_info]
            return [{"total": int(info[0]), "used": int(info[1]), "free": int(info[2])} for info in memory_info]
        else:
            return None
    except Exception as e:
        print(f"Error accessing GPU memory info: {e}")
        return None

def convert_labels(list_of_dicts: list[dict[str, torch.tensor]], class2label: dict[int, int]) -> list[dict[str, torch.tensor]]:
    """
    Converts 'labels' tensors in a list of dictionaries using a mapping dictionary.

    Parameters:
    - list_of_dicts: A list of dictionaries, each containing a 'labels' key with a torch tensor of integers.
    - class2label: A dictionary mapping integers from the 'labels' tensors to new integers.

    Returns:
    - The modified list_of_dicts with converted 'labels' tensors.
    """
    for i in range(len(list_of_dicts)):
        list_of_dicts[i]['labels'] = torch.tensor([class2label[int(label)] for label in list_of_dicts[i]['labels']])
    return list_of_dicts

def print_structure(obj):
    if isinstance(obj, list):
        item = obj[0]
        return f"list[{print_structure(item)}]"
    elif isinstance(obj, tuple):
        item = obj[0]
        return f"tuple[{print_structure(item)}]"
    elif isinstance(obj, dict):
        internal_structure = "\n"
        for key, value in obj.items():
            internal_structure += f"({print_structure(key)}: {key},{print_structure(value)})\n"
        return f"dict[{internal_structure}]"
    elif isinstance(obj, torch.Tensor):
        return f"torch.tensor[dtype:{obj.dtype}, shape:{obj.shape}]"
    elif isinstance(obj, str):
        return "str"
    elif isinstance(obj, float):
        return "float"
    elif isinstance(obj, int):
        return "int"
    else:
        raise TypeError(f"Object is of type {type(obj)} but should be one of [list, tuple, dict, torch.Tensor, str]")

def cuda_memory_helper(device=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except RuntimeError as e:
                if 'CUDA out of memory' in str(e):
                    print(f"CUDA out of memory occurred on device {device}.")
                    print(torch.cuda.memory_summary(device=device, abbreviated=False))
                else:
                    raise e
        return wrapper
    return decorator




    