import pytest


def find_max(scores):
	biggest = scores[0]
	for i in range(1, len(scores) - 1):
		if scores[i] > biggest:
			biggest = scores[i]
	return biggest


def test_find_max_returns_largest_score():
	assert find_max([72, 91, 85, 88]) == 91


def test_find_max_handles_negative_scores():
	assert find_max([-8, -3, -12]) == -3


def test_find_max_raises_index_error_for_empty_scores():
	with pytest.raises(IndexError):
		find_max([])


def test_find_max_handles_single_score():
	assert find_max([42]) == 42


def test_find_max_includes_last_score():
	assert find_max([1, 2, 10]) == 10
