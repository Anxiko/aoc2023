from day19 import Range, LessThan, GreaterThan


def test_range_less_than():
	r: Range = Range(2, 4)
	assert LessThan().split_range(r, 1) == (None, r)
	assert LessThan().split_range(r, 2) == (None, r)
	assert LessThan().split_range(r, 3) == (Range(2, 2), Range(3, 4))
	assert LessThan().split_range(r, 4) == (Range(2, 3), Range(4, 4))
	assert LessThan().split_range(r, 5) == (r, None)


def test_range_greater_than():
	r: Range = Range(2, 4)
	assert GreaterThan().split_range(r, 1) == (r, None)
	assert GreaterThan().split_range(r, 2) == (Range(3, 4), Range(2, 2))
	assert GreaterThan().split_range(r, 3) == (Range(4, 4), Range(2, 3))
	assert GreaterThan().split_range(r, 4) == (None, r)
	assert GreaterThan().split_range(r, 5) == (None, r)
