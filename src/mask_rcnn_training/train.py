from training_utils.trainer import Trainer
import torch
import sys

torch.manual_seed(0)
def main(post_process, data):
    trainer = Trainer('src/mask_rcnn_training/configs/grid_search_training_configs.json')

    if data==0:
        trainer.configs['train_images_path'] = '/vol/bitbucket/cdr23/temp_new/'
        trainer.configs['train_annotations_name'] = '/vol/bitbucket/cdr23/temp_new/synth_train.json'
    elif data==1:
        trainer.configs['train_images_path'] = '/vol/bitbucket/cdr23/dataset_50/'
        trainer.configs['train_annotations_name'] = '/vol/bitbucket/cdr23/dataset_50/synth_train.json'
        
    #trainer.configs['load_from_checkpoint'] = False
    trainer.configs['model_path'] = f"/vol/bitbucket/or623/seed_models/grid_search_models/rcnn_post{post_process}_data{data}.pt"
    trainer.configs['map_plot_path'] = f"src/grid_search/graphs/train_vs_val__post{post_process}_data{data}.png"
    trainer.configs['vis_plot_path'] = f'src/grid_search/graphs/visualisations_post{post_process}_data{data}_epoch'
    trainer.hyper_params['post-process'] = post_process
    trainer.hyper_params['num_epochs'] = 10
    
    
    print_trainer_configs(trainer)
    trainer.train()

def print_trainer_configs(trainer):
    print("\nTrainer Configs\n")
    for key, val in trainer.configs.items():
        print(f"\t{key} {val}")
    print("\nHyper Params\n")
    for key, val in trainer.hyper_params.items():
        print(f"\t{key} {val}")
    print(flush=True)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <post-process> <data>")
        sys.exit(1)
        
    post_process = bool(int(sys.argv[1]))
    data = int(sys.argv[2])
    main(post_process, data)