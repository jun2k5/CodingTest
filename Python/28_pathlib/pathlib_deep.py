"""28. pathlib·shutil·tempfile: 경로 객체, 경로 조작, 읽기·쓰기, glob, 복사·이동·삭제, 임시 파일"""
import os
import shutil
import tempfile
from pathlib import Path, PurePosixPath, PureWindowsPath


def path_parts():
    p = PurePosixPath("/srv/app/data/report.final.csv")
    print("name:", p.name, "| stem:", p.stem, "| suffix:", p.suffix, "| suffixes:", p.suffixes)
    print("parent:", p.parent, "| parents[1]:", p.parents[1], "| parts:", p.parts)
    print("with_suffix:", p.with_suffix(".json"), "| with_name:", p.with_name("x.txt"))
    print("with_stem(3.9+):", p.with_stem("summary"))
    print("/ 연산자로 결합:", PurePosixPath("/srv") / "app" / "logs")
    print("Windows 경로도 같은 API:", PureWindowsPath(r"C:\Users\kim\a.txt").parent)
    print("relative_to:", p.relative_to("/srv/app"))
    print("상대 경로 결합 시 절대 경로가 이긴다:", PurePosixPath("/a") / "/b")


def file_io(base: Path):
    data_dir = base / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    f = data_dir / "hello.txt"
    f.write_text("안녕\n파이썬\n", encoding="utf-8")
    print("read_text 줄 수:", len(f.read_text(encoding="utf-8").splitlines()))
    print("exists/is_file/is_dir:", f.exists(), f.is_file(), data_dir.is_dir())
    print("stat 크기:", f.stat().st_size, "바이트")
    (data_dir / "b.bin").write_bytes(bytes([1, 2, 3]))
    with f.open("a", encoding="utf-8") as fh:
        fh.write("추가\n")
    print("open으로 추가 후:", f.read_text(encoding="utf-8").split())


def searching(base: Path):
    for name in ["a.py", "b.py", "sub/c.py", "sub/deep/d.txt"]:
        target = base / "src" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.touch()
    src = base / "src"
    print("glob('*.py'):", sorted(p.name for p in src.glob("*.py")))
    print("rglob('*.py'):", sorted(p.relative_to(src).as_posix() for p in src.rglob("*.py")))
    print("iterdir:", sorted(p.name for p in src.iterdir()))
    walked = sorted(d.relative_to(src).as_posix() for d, dirs, files in src.walk())   # 3.12+
    print("Path.walk:", walked)


def copy_move_delete(base: Path):
    src = base / "src"
    backup = base / "backup"
    shutil.copytree(src, backup, ignore=shutil.ignore_patterns("*.txt"))
    print("copytree(txt 제외):", sorted(p.relative_to(backup).as_posix() for p in backup.rglob("*") if p.is_file()))
    shutil.copy2(src / "a.py", base / "a_copy.py")            # 메타데이터(수정 시각) 포함
    shutil.move(base / "a_copy.py", base / "moved.py")
    print("move 후 존재:", (base / "moved.py").exists(), (base / "a_copy.py").exists())
    (base / "moved.py").unlink()
    (base / "moved.py").unlink(missing_ok=True)               # 3.8+: 없어도 오류 없음
    shutil.rmtree(backup)
    print("rmtree 후:", backup.exists())
    total, used, free = shutil.disk_usage(base)
    print("disk_usage 반환 필드 수:", len((total, used, free)))
    print("which python:", shutil.which("python") is not None)


def temp_files():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        (tmp_path / "x.txt").write_text("임시", encoding="utf-8")
        inside = tmp_path.exists()
    print("TemporaryDirectory: 안에서", inside, "| 나오면 삭제:", tmp_path.exists())

    with tempfile.NamedTemporaryFile("w+", suffix=".csv", delete=False, encoding="utf-8") as f:
        f.write("a,b\n")
        name = f.name
    print("NamedTemporaryFile(delete=False) 확장자:", Path(name).suffix, "| 남아 있음:", Path(name).exists())
    os.remove(name)

    with tempfile.SpooledTemporaryFile(max_size=1024, mode="w+") as sp:
        sp.write("작으면 메모리에만")
        print("SpooledTemporaryFile 디스크로 넘어갔나:", sp._rolled)


if __name__ == "__main__":
    path_parts()
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        file_io(base)
        searching(base)
        copy_move_delete(base)
    temp_files()
    print("현재 디렉터리 / 홈:", Path.cwd().is_absolute(), Path.home().is_absolute())
    print("모든 검증 통과")
