import csv

import pytest


def read_scores(path):
	"""Return valid ``(name, score)`` rows and skipped ``(line, reason)`` rows."""
	valid = []
	skipped = []
	names = set()

	with open(path, "r", encoding="utf-8", newline="") as file:
		rows = csv.reader(file)
		try:
			header = next(rows)
		except StopIteration as exc:
			raise ValueError("header is missing") from exc

		if header != ["name", "score"]:
			raise ValueError("header must be name,score")

		for line_number, row in enumerate(rows, start=2):
			if len(row) != 2:
				raise ValueError("each row must contain two columns")

			name, raw_score = (value.strip() for value in row)
			if not raw_score:
				skipped.append((line_number, "score is missing"))
				continue
			try:
				score = int(raw_score)
			except ValueError:
				skipped.append((line_number, "score must be numeric"))
				continue
			if not 0 <= score <= 100:
				skipped.append((line_number, "score must be between 0 and 100"))
				continue
			if name in names:
				skipped.append((line_number, "duplicate name"))
				continue

			names.add(name)
			valid.append((name, score))

	return valid, skipped


def write_csv(tmp_path, content):
	path = tmp_path / "scores.csv"
	path.write_text(content, encoding="utf-8", newline="")
	return path


def test_read_scores_returns_valid_rows_and_skipped_rows(tmp_path):
	path = write_csv(tmp_path, "name,score\nAlice,90\nBob,0\nCara,100\nBad,101\n")

	assert read_scores(path) == (
		[("Alice", 90), ("Bob", 0), ("Cara", 100)],
		[(5, "score must be between 0 and 100")],
	)


@pytest.mark.parametrize("content", ["", "name\nAlice,90\n", "student,score\nAlice,90\n"])
def test_read_scores_rejects_missing_or_invalid_header(tmp_path, content):
	with pytest.raises(ValueError):
		read_scores(write_csv(tmp_path, content))


def test_read_scores_rejects_wrong_column_count(tmp_path):
	with pytest.raises(ValueError):
		read_scores(write_csv(tmp_path, "name,score\nAlice,90,extra\n"))


def test_read_scores_reports_invalid_scores_and_includes_boundaries(tmp_path):
	path = write_csv(
		tmp_path,
		"name,score\nMissing,\nText,abc\nLow,-1\nHigh,101\nEdge,0\nTop,100\n",
	)

	valid, skipped = read_scores(path)

	assert valid == [("Edge", 0), ("Top", 100)]
	assert skipped == [
		(2, "score is missing"),
		(3, "score must be numeric"),
		(4, "score must be between 0 and 100"),
		(5, "score must be between 0 and 100"),
	]


def test_read_scores_skips_duplicate_names(tmp_path):
	path = write_csv(tmp_path, "name,score\nAlice,90\nBob,80\nAlice,70\n")

	assert read_scores(path) == (
		[("Alice", 90), ("Bob", 80)],
		[(4, "duplicate name")],
	)


def test_read_scores_reports_missing_file(tmp_path):
	with pytest.raises(FileNotFoundError):
		read_scores(tmp_path / "missing.csv")


def test_read_scores_reports_unreadable_file(monkeypatch, tmp_path):
	path = tmp_path / "scores.csv"
	path.touch()
	monkeypatch.setattr("builtins.open", lambda *args, **kwargs: (_ for _ in ()).throw(PermissionError()))

	with pytest.raises(PermissionError):
		read_scores(path)


def test_read_scores_does_not_modify_source_file(tmp_path):
	path = write_csv(tmp_path, "name,score\nAlice,90\n")
	before = path.read_bytes()

	read_scores(path)

	assert path.read_bytes() == before
