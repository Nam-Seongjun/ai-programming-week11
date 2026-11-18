import csv

import pytest


MIN_SCORE = 0
MAX_SCORE = 100


def load_scores(path):
	"""성적 CSV를 읽어 (유효한 목록, 건너뛴 줄 기록) 을 돌려준다."""
	kept = []
	skipped = []

	with open(path, "r", encoding="utf-8-sig", newline="") as f:
		reader = csv.reader(f)
		for line_no, row in enumerate(reader, start=1):
			if line_no == 1:
				continue
			if not row:
				continue

			original = ",".join(row)

			if len(row) != 2:
				skipped.append((line_no, original, "열 개수가 2가 아님"))
				continue

			name = row[0].strip()
			raw = row[1].strip()

			if name == "":
				skipped.append((line_no, original, "이름이 비어 있음"))
				continue
			if raw == "":
				skipped.append((line_no, original, "점수가 비어 있음"))
				continue

			try:
				score = int(raw)
			except ValueError:
				skipped.append((line_no, original, "점수가 정수가 아님"))
				continue

			if score < MIN_SCORE or score > MAX_SCORE:
				skipped.append((line_no, original, "점수가 0~100 밖"))
				continue

			kept.append((name, score))

	return kept, skipped


def write_csv(tmp_path, content):
	path = tmp_path / "scores.csv"
	path.write_text(content, encoding="utf-8")
	return path


def test_load_scores_keeps_valid_rows_and_skips_invalid_rows(tmp_path):
	path = write_csv(
		tmp_path,
		"이름,점수\n홍길동,95\n 김철수 , 0 \n박영희,100\n",
	)

	kept, skipped = load_scores(path)

	assert kept == [("홍길동", 95), ("김철수", 0), ("박영희", 100)]
	assert skipped == []


@pytest.mark.parametrize(
	("row", "reason"),
	[
		("a,b,c", "열 개수가 2가 아님"),
		(",50", "이름이 비어 있음"),
		("홍길동,", "점수가 비어 있음"),
		("홍길동,91.5", "점수가 정수가 아님"),
		("홍길동,-1", "점수가 0~100 밖"),
		("홍길동,101", "점수가 0~100 밖"),
	],
)
def test_load_scores_records_invalid_rows(tmp_path, row, reason):
	path = write_csv(tmp_path, f"이름,점수\n{row}\n")

	kept, skipped = load_scores(path)

	assert kept == []
	assert skipped == [(2, row, reason)]


def test_load_scores_ignores_header_and_blank_lines(tmp_path):
	path = write_csv(tmp_path, "이름,점수\n\n홍길동,50\n\n")

	kept, skipped = load_scores(path)

	assert kept == [("홍길동", 50)]
	assert skipped == []


def test_load_scores_supports_utf8_bom(tmp_path):
	path = tmp_path / "scores.csv"
	path.write_text("이름,점수\n홍길동,80\n", encoding="utf-8-sig")

	assert load_scores(path) == ([("홍길동", 80)], [])


def test_load_scores_raises_for_missing_file(tmp_path):
	with pytest.raises(FileNotFoundError):
		load_scores(tmp_path / "missing.csv")
