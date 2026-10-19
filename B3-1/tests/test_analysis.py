"""가짜 소규모 자료는 단위 검사용이며 제출 관측자료와 분리한다."""

import csv
import io
from pathlib import Path
from urllib.error import URLError

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from transport_analysis.clean import clean_observations
from transport_analysis.metrics import daily_features, summarize
from transport_analysis.sources import aggregate_csv, download


@pytest.fixture
def observations():
    dates = pd.date_range("2025-01-01", "2025-12-31")
    return pd.DataFrame(
        [
            {"date": d.strftime("%Y-%m-%d"), "mode": mode, "value": 10}
            for d in dates
            for mode in ("bike", "bus", "subway")
        ]
    )


def test_complete_unsorted_data_is_sorted_without_mutating_input(observations):
    original = observations.copy(deep=True)
    result, quality = clean_observations(observations.iloc[::-1])
    assert len(result) == 1095
    assert quality["removed_rows"] == 0
    assert result.iloc[0]["date"] == pd.Timestamp("2025-01-01")
    assert_frame_equal(original, observations)


@pytest.mark.parametrize("value", [-1, 1.5, float("inf"), float("nan"), "bad"])
def test_invalid_counts_are_not_silently_replaced(observations, value):
    observations["value"] = observations["value"].astype(object)
    observations.loc[0, "value"] = value
    with pytest.raises(ValueError):
        clean_observations(observations)


def test_missing_day_does_not_become_zero(observations):
    with pytest.raises(ValueError, match="누락"):
        clean_observations(observations.iloc[1:])


@pytest.mark.parametrize("changed", [False, True])
def test_duplicate_keys_fail_even_if_values_match(observations, changed):
    row = observations.iloc[[0]].copy()
    if changed:
        row.loc[0, "value"] = 100
    with pytest.raises(ValueError, match="중복"):
        clean_observations(pd.concat([observations, row]))


def test_invalid_calendar_date_is_rejected(observations):
    observations.loc[0, "date"] = "2025-02-30"
    with pytest.raises(ValueError):
        clean_observations(observations)


def test_constant_counts_and_rolling_warmup(observations):
    data, _ = clean_observations(observations)
    stats, features = summarize(data)
    for mode in ("bike", "bus", "subway"):
        s = stats["modes"][mode]
        assert s["total"] == 3650
        assert s["weekend_change_pct"] == 0
        assert s["anomaly_count"] == 0
        part = features[features["mode"] == mode]
        assert part["rolling7"].iloc[:6].isna().all()
        assert (part["rolling7"].iloc[6:] == 10).all()


def test_moving_average_does_not_bridge_calendar_gap():
    data = pd.DataFrame(
        {
            "date": pd.to_datetime(
                [
                    "2025-01-01",
                    "2025-01-02",
                    "2025-01-04",
                    "2025-01-05",
                    "2025-01-06",
                    "2025-01-07",
                    "2025-01-08",
                ]
            ),
            "mode": "bike",
            "value": 10,
        }
    )
    assert daily_features(data)["rolling7"].isna().all()


def test_zero_baseline_produces_no_invented_percentage(observations):
    observations["value"] = 0
    data, _ = clean_observations(observations)
    stats, features = summarize(data)
    assert features["deviation_pct"].isna().all()
    assert stats["modes"]["bike"]["weekend_change_pct"] is None


def write_source(tmp_path: Path, rows: list) -> tuple[Path, dict]:
    path = tmp_path / "sample.csv"
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["사용일자", "역명", "승차총승객수", "하차총승객수"])
        w.writerows(rows)
    return path, {"encoding": "utf-8", "mode": "subway", "start": "2025-01-01", "end": "2025-01-01"}


def test_source_uses_boardings_only_and_allows_empty_extra_column(tmp_path):
    path, spec = write_source(
        tmp_path, [["20250101", "A", "10", "900", ""], ["20250101", "B", "20", "800", ""]]
    )
    rows, quality = aggregate_csv(path, spec)
    assert rows[0]["value"] == 30
    assert quality["trailing_empty_fields_removed"] == 2


@pytest.mark.parametrize(
    "rows",
    [
        [["20250101", "A", "10", "20", "unexpected"]],
        [["20250101", "A", "10", "20"], ["20250101", "A", "10", "20"]],
        [["20250101", "A", "", "20"]],
        [["20250102", "A", "10", "20"]],
    ],
)
def test_source_malformed_duplicate_missing_or_outside_period_fails(tmp_path, rows):
    path, spec = write_source(tmp_path, rows)
    with pytest.raises(ValueError):
        aggregate_csv(path, spec)


class Response(io.BytesIO):
    def __init__(self, body, length=None):
        super().__init__(body)
        self.headers = {} if length is None else {"Content-Length": str(length)}


@pytest.mark.parametrize("body,length", [(b"<html>error</html>", None), (b"abc", 100), (b"", None)])
def test_download_failure_leaves_no_partial_artifact(tmp_path, body, length):
    path = tmp_path / "data.csv"
    spec = {"inf_id": "test", "inf_seq": 1, "seq": 1, "file": "data.csv"}
    with pytest.raises(ValueError):
        download(spec, path, opener=lambda *a, **kw: Response(body, length))
    assert not path.exists()
    assert not path.with_suffix(".part").exists()


def test_network_failure_is_propagated(tmp_path):
    def unavailable(*args, **kwargs):
        raise URLError("test network failure")

    spec = {"inf_id": "test", "inf_seq": 1, "seq": 1, "file": "data.csv"}
    with pytest.raises(URLError):
        download(spec, tmp_path / "data.csv", opener=unavailable)
