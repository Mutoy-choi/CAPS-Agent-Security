from caps_verify.scoring import composition_metrics, wilson_interval


def test_wilson_interval_contains_observed_proportion() -> None:
    low, high = wilson_interval(5, 10)
    assert low < 0.5 < high


def test_wilson_zero_trials() -> None:
    assert wilson_interval(0, 0) == (0.0, 0.0)


def test_composition_metrics() -> None:
    result = composition_metrics([0.1, 0.2], 0.5)
    assert result["composition_delta"] == 0.3
    assert result["composition_ratio"] == 2.5
