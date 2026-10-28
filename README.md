# PDF압축

PDF 파일(또는 폴더)을 프로그램 아이콘 위로 끌어다 놓으면 바로 압축해서
원본과 같은 폴더에 `이름_compressed.pdf` 로 저장합니다. 압축 중에는 진행 창이, 끝나면 결과가 몇 초간 뜹니다.

- 아이콘을 더블클릭하면 드래그앤드롭 창이 열립니다. 여기서 고른 압축 강도는 저장되어 아이콘 드롭에도 적용됩니다 (처음엔 보통)
- 압축해도 크기가 줄지 않으면 파일을 만들지 않습니다
- 암호가 걸린 PDF는 건너뜁니다

## 다운로드

[Releases](../../releases) 에서 OS에 맞는 파일을 받으세요.

| OS | 파일 | 사용법 |
|---|---|---|
| macOS (Apple Silicon) | `PDFCompress-macOS.zip` | 압축 풀고 `PDF압축.app` 을 응용 프로그램 폴더로 옮긴 뒤 아래 "macOS 처음 실행" 참고 |
| Windows | `PDFCompress-Windows-Setup.exe` | 실행해서 설치 → 바탕화면 `PDF압축` 아이콘에 PDF 드롭. 제거는 설정 → 앱 |
| Linux | `PDFCompress-Linux.tar.gz` | 원하는 곳에 압축 풀고 `PDFCompress/install.sh` 실행 → 바탕화면 아이콘 생성 |

### macOS 처음 실행

Apple 공증을 받지 않은 앱이라, 인터넷에서 받으면 macOS가 실행을 막습니다. 터미널에서 한 번만 실행하세요:

```bash
xattr -cr /Applications/PDF압축.app
```

또는 앱을 한 번 실행해 차단되게 한 뒤 **시스템 설정 → 개인정보 보호 및 보안 → 그래도 열기**를 누르세요.

Windows 에서도 서명되지 않은 설치 프로그램이라 SmartScreen 경고가 뜨면 **추가 정보 → 실행**을 누르세요.
받은 파일이 변조되지 않았는지는 릴리스의 `SHA256SUMS.txt` 와 비교해 확인할 수 있습니다.

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

결과물은 `dist/` 에 생깁니다: macOS `PDF압축.app`, Windows/Linux `PDFCompress/` 폴더.
Windows 설치 프로그램은 [Inno Setup 6](https://jrsoftware.org/isinfo.php) 설치 후 `iscc installer.iss` 로 만듭니다.
Linux에서 직접 빌드할 때는 `python3-tk` 패키지가 필요합니다.
