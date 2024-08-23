from src.evaluation.evaluation import full_evaluation
import pytest

@pytest.mark.skip("Can't run remotely without datasets")
def test():
    test_folder = "/vol/bitbucket/cdr23/dataset_final/"
    test_json = "/vol/bitbucket/cdr23/dataset_final/full_test.json"
    performance = full_evaluation(test_folder, test_json, return_mean_per_class=False)
    print(performance)
    performance = full_evaluation(test_folder, test_json, return_mean_per_class=True)
    print(performance)

if __name__ == "__main__":
    test()