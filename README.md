# PDF압축

PDF 파일(또는 폴더)을 프로그램 아이콘 위로 끌어다 놓으면, 창 없이 바로 압축해서
원본과 같은 폴더에 `이름_compressed.pdf` 로 저장합니다. 끝나면 알림이 몇 초간 뜹니다.

- 아이콘을 더블클릭하면 드래그앤드롭 창이 열립니다 (압축 강도 선택 가능)
- 압축해도 크기가 줄지 않으면 파일을 만들지 않습니다
- 암호가 걸린 PDF는 건너뜁니다

## 다운로드

[Releases](../../releases) 에서 OS에 맞는 파일을 받으세요.

| OS | 파일 | 사용법 |
|---|---|---|
| macOS (Apple Silicon) | `PDFCompress-macOS.zip` | 압축 풀고 `PDF압축.app` 을 응용 프로그램 폴더로 옮긴 뒤 아래 "macOS 처음 실행" 참고 |
| Windows | `PDFCompress-Windows.zip` | 압축 풀고 `PDF압축.exe` 를 바탕화면에 두기 |
| Linux | `PDFCompress-Linux.tar.gz` | 압축 풀고 `./install.sh` 실행 → 바탕화면 아이콘 생성 (`python3-tk` 불필요, 실행 파일에 포함) |

### macOS 처음 실행

Apple 공증을 받지 않은 앱이라, 인터넷에서 받으면 macOS가 실행을 막습니다. 터미널에서 한 번만 실행하세요:

```bash
xattr -cr /Applications/PDF압축.app
```

또는 앱을 한 번 실행해 차단되게 한 뒤 **시스템 설정 → 개인정보 보호 및 보안 → 그래도 열기**를 누르세요.

## 릴리스 만들기

`v` 로 시작하는 태그를 push하면 GitHub Actions 가 세 OS용 파일을 빌드해 Releases 에 올립니다.

```bash
git tag v1.0.1 && git push origin v1.0.1
```

## 직접 빌드 (각 OS에서)

```bash
python -m venv .venv
# macOS/Linux: source .venv/bin/activate   Windows: .venv\Scripts\activate
pip install -r requirements.txt
python build.py
```

결과물은 `dist/` 에 생깁니다: macOS `PDF압축.app`, Windows `PDF압축.exe`, Linux `PDFCompress` + `install.sh`.
Linux에서 직접 빌드할 때는 `python3-tk` 패키지가 필요합니다.
