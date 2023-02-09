from grading.evaluate import Evaluate


def test_evaluate_an():
    result = Evaluate.grading([[1, 2, 3, 4]], 'an')
    assert result == 1


def test_evaluate_an():
    result = Evaluate.grading([[1, 2, 3, 4]], 'an')
    assert result == 'an'
