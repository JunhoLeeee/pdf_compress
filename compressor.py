"""PDF 압축 엔진 (PyMuPDF 기반, macOS / Windows / Linux 공통)."""
from dataclasses import dataclass
from pathlib import Path

import pymupdf

# 압축 강도별 설정: 이미지 해상도(dpi) 상한과 JPEG 품질
LEVELS = {
    "낮음 (고화질)": {"dpi_threshold": 225, "dpi_target": 200, "quality": 85},
    "보통 (권장)": {"dpi_threshold": 165, "dpi_target": 150, "quality": 75},
    "높음 (저용량)": {"dpi_threshold": 110, "dpi_target": 96, "quality": 60},
}
DEFAULT_LEVEL = "보통 (권장)"
SUFFIX = "_compressed"


@dataclass
class Result:
    src: Path
    out: Path | None
    before: int
    after: int
    message: str

    @property
    def ratio(self) -> float:
        return (1 - self.after / self.before) * 100 if self.before else 0.0


def output_path(src: Path) -> Path:
    """원본과 같은 폴더에 `이름_compressed.pdf`, 이미 있으면 번호를 붙인다."""
    out = src.with_name(f"{src.stem}{SUFFIX}.pdf")
    n = 2
    while out.exists():
        out = src.with_name(f"{src.stem}{SUFFIX}({n}).pdf")
        n += 1
    return out


def compress(src: Path, level: str = DEFAULT_LEVEL) -> Result:
    src = Path(src)
    before = src.stat().st_size
    opts = LEVELS[level]

    doc = pymupdf.open(src)
    try:
        if doc.needs_pass:
            return Result(src, None, before, before, "암호가 걸린 PDF라 건너뜀")
        doc.rewrite_images(
            dpi_threshold=opts["dpi_threshold"],
            dpi_target=opts["dpi_target"],
            quality=opts["quality"],
        )
        doc.subset_fonts()
        out = output_path(src)
        doc.save(
            out,
            garbage=4,
            clean=True,
            deflate=True,
            deflate_images=True,
            deflate_fonts=True,
            use_objstms=True,
            compression_effort=100,
        )
    finally:
        doc.close()

    after = out.stat().st_size
    if after >= before:
        out.unlink()
        return Result(src, None, before, before, "이미 최적화된 파일이라 더 줄일 수 없음")
    return Result(src, out, before, after, "완료")


def collect_pdfs(paths) -> list[Path]:
    """파일/폴더 목록에서 압축 대상 PDF만 추린다 (폴더는 하위까지 탐색)."""
    found = []
    for p in map(Path, paths):
        if p.is_dir():
            found += sorted(
                f for f in p.rglob("*")
                if f.suffix.lower() == ".pdf" and SUFFIX not in f.stem
            )
        elif p.is_file() and p.suffix.lower() == ".pdf":
            found.append(p)
    return found


def human(size: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:.0f}{unit}" if unit == "B" else f"{size:.1f}{unit}"
        size /= 1024
