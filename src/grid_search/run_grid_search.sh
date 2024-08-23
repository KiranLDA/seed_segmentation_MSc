#!/bin/bash

post_process=(0 1)
dataset=(0 1)

python_script="src/mask_rcnn_training/train.py"

output_dir="src/grid_search/outputs"
error_dir="src/grid_search/errors"
graph_dir="src/grid_search/graphs"

mkdir -p "$output_dir"
mkdir -p "$error_dir"
mkdir -p "$graph_dir"

email="or623@ic.ac.uk"

source /vol/bitbucket/or623/venvs/seed/bin/activate
python_exe="$(which python)"

for post in "${post_process[@]}"; do
    for data in "${dataset[@]}"; do
        job_name="data${data}_post${post}"
        ~if [ -f "${output_dir}/${job_name}.out" ]; then
            echo "Skipping job ${job_name} as it has already been run."
        else
            sbatch --job-name="$job_name" \
                       --output="${output_dir}/${job_name}.out" \
                       --error="${error_dir}/${job_name}.err" \
                       --gres=gpu:1 \
                       --mem=12G \
                       --mail-type=END,FAIL \
                       --mail-user="$email" \
                       --time=2-12:00:00 \
                       --wrap="$python_exe $python_script $post $data"
        fi
    done
done
