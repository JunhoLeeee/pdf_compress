"""현재 OS용 실행 파일을 dist/ 에 만든다. (각 OS에서 한 번씩 실행해야 함)

    python build.py
"""
import os
import shutil
import sys
from pathlib import Path

import PyInstaller.__main__

# 내부 실행 파일 이름은 영문이어야 함 (한글이면 macOS codesign 이 충돌). 사용자에게는 DISPLAY_NAME 으로 보임
NAME = "PDFCompress"
DISPLAY_NAME = "PDF압축"
ROOT = Path(__file__).parent

args = [
    str(ROOT / "app.py"),
    "--name", NAME,
    "--windowed",
    "--noconfirm",
    # 실행 파일 아이콘 (macOS는 PNG → icns 자동 변환, Pillow 필요) + 창 아이콘용 이미지
    "--icon", str(ROOT / "assets" / ("icon.ico" if sys.platform == "win32" else "icon.png")),
    "--add-data", f"{ROOT / 'assets' / 'icon_256.png'}{os.pathsep}assets",
    # PyMuPDF 2.x 의 AI 레이아웃 분석 모듈은 압축에 불필요 (없으면 pymupdf가 알아서 건너뜀)
    "--exclude-module", "pymupdf.layout",
    "--exclude-module", "pymupdf4llm",
    "--exclude-module", "onnxruntime",
    "--exclude-module", "numpy",
]
if sys.platform == "darwin":
    args += ["--argv-emulation"]  # Finder에서 아이콘에 드롭한 파일을 sys.argv 로 전달
else:
    args += ["--onefile"]

PyInstaller.__main__.run(args)

if sys.platform == "darwin":
    import plistlib
    import subprocess

    # Finder가 앱 아이콘 위로 PDF/폴더 드롭을 허용하도록 문서 타입 선언
    app = ROOT / "dist" / f"{NAME}.app"
    plist_path = app / "Contents" / "Info.plist"
    info = plistlib.loads(plist_path.read_bytes())
    info["CFBundleDocumentTypes"] = [{
        "CFBundleTypeName": "PDF",
        "CFBundleTypeRole": "Viewer",
        "LSHandlerRank": "Alternate",
        "LSItemContentTypes": ["com.adobe.pdf", "public.folder"],
    }]
    info["CFBundleName"] = info["CFBundleDisplayName"] = DISPLAY_NAME
    plist_path.write_bytes(plistlib.dumps(info))
    subprocess.run(["xattr", "-cr", str(app)], check=True)
    subprocess.run(["codesign", "-s", "-", "--force", "--deep", str(app)], check=True)
    # .app 폴더 이름은 서명 대상이 아니므로 서명 후 한글 이름으로 변경
    final = app.with_name(f"{DISPLAY_NAME}.app")
    shutil.rmtree(final, ignore_errors=True)
    app.rename(final)
    print(f"\n{final} 를 응용 프로그램 폴더나 Dock/바탕화면에 두고 PDF를 아이콘 위로 끌어다 놓으세요.")

if sys.platform == "win32":
    exe = ROOT / "dist" / f"{NAME}.exe"
    final = exe.with_name(f"{DISPLAY_NAME}.exe")
    final.unlink(missing_ok=True)
    exe.rename(final)
    print(f"\n{final} 를 바탕화면에 두고(또는 바로가기 생성) PDF를 아이콘 위로 끌어다 놓으세요.")

if sys.platform.startswith("linux"):
    # .desktop 의 Exec 는 절대 경로여야 하므로, 압축을 푼 위치에서 install.sh 가 바탕화면 아이콘을 만든다
    shutil.copy(ROOT / "assets" / "icon_256.png", ROOT / "dist" / f"{NAME}.png")
    install = ROOT / "dist" / "install.sh"
    install.write_text(
        "#!/bin/sh\n"
        "# 바탕화면에 PDF를 끌어다 놓을 수 있는 아이콘을 만든다\n"
        'DIR="$(cd "$(dirname "$0")" && pwd)"\n'
        'DESKTOP="$(xdg-user-dir DESKTOP 2>/dev/null || echo "$HOME/Desktop")"\n'
        f'FILE="$DESKTOP/{DISPLAY_NAME}.desktop"\n'
        "cat > \"$FILE\" <<EOF\n"
        "[Desktop Entry]\n"
        "Type=Application\n"
        f"Name={DISPLAY_NAME}\n"
        f'Exec="$DIR/{NAME}" %F\n'
        f"Icon=$DIR/{NAME}.png\n"
        "MimeType=application/pdf;inode/directory;\n"
        "Terminal=false\n"
        "EOF\n"
        'chmod +x "$FILE" "$DIR/' + NAME + '"\n'
        'gio set "$FILE" metadata::trusted true 2>/dev/null\n'
        'echo "$FILE 생성 완료 (안 되면 아이콘 우클릭 → \'실행 허용\')"\n',
        encoding="utf-8",
    )
    install.chmod(0o755)
    print(f"\ndist/ 폴더에서 ./install.sh 를 실행하면 바탕화면에 아이콘이 생깁니다.")
