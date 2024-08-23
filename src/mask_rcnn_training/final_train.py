from training_utils.trainer import Trainer
import torch

torch.manual_seed(0)
def main():
    trainer = Trainer('src/mask_rcnn_training/configs/training_configs.json')
    trainer.configs['model_folder'] = "/vol/bitbucket/or623/seed_models/final_models/"
    trainer.hyper_params['num_epochs'] = 20
    print_trainer_configs(trainer)
    trainer.train()

def print_trainer_configs(trainer):
    print("\nTrainer Configs\n")
    for key, val in trainer.configs.items():
        print(f"\t{key}\t{val}")
    print("\nHyper Params\n")
    for key, val in trainer.hyper_params.items():
        print(f"\t{key}\t{val}")
    print(flush=True)

if __name__ == "__main__":
    main()