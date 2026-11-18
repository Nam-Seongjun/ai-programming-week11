import pytest
from load_scores import load_scores

def 쓰기(파일이름, 점수):
    with open(파일이름, "w", encoding="utf-8-sig", newline="") as f:
        f.write("name,score\n")
        f.write(f"테스트,{점수}\n")
        

def test_정상_파일을_읽는다():
    kept, skipped = load_scores("week11/scores.csv")
    assert len(kept) == 5
    
    
    
def test_없는_파일이면_오류가_난다():
    with pytest.raises(FileNotFoundError):
        load_scores("week11/없는파일.csv")


def test_헤더만_있으면_빈_결과가_나온다():
    kept, skipped = load_scores("week11/empty.csv")
    assert kept == []
    assert skipped == []

@pytest.mark.parametrize("점수, 유효한가", [
    (-1,   False),   # 경계 바로 아래
    (0,    True),    # 아래쪽 경계
    (1,    True),
    (99,   True),
    (100,  True),    # 위쪽 경계
    (101,  False),   # 경계 바로 위
])
def test_점수_경계값(점수, 유효한가):
    쓰기("week11/임시.csv", 점수)
    kept, skipped = load_scores("week11/임시.csv")
    assert (len(kept) == 1) == 유효한가


def test_이름이_비어_있으면_건너뛴다():
    쓰기("week11/임시.csv", 80)
    with open("week11/임시.csv", "w", encoding="utf-8-sig") as f:
        f.write("name,score\n")
        f.write(",80\n")

    kept, skipped = load_scores("week11/임시.csv")
    assert len(kept) == 0
    assert len(skipped) == 1



def test_빈_줄은_건너뛴다():
    kept, skipped = load_scores("week11/scores.csv")
    assert len(kept) == 5


def test_이름에_쉼표가_있어도_읽는다():
    kept, skipped = load_scores("week11/scores.csv")
    assert ("최,네번", 77) in kept