# PDF압축

PDF 파일(또는 폴더)을 프로그램 아이콘 위로 끌어다 놓으면, 창 없이 바로 압축해서
원본과 같은 폴더에 `이름_compressed.pdf` 로 저장합니다. 끝나면 알림이 몇 초간 뜹니다.

- 아이콘을 더블클릭하면 드래그앤드롭 창이 열립니다 (압축 강도 선택 가능)
- 압축해도 크기가 줄지 않으면 파일을 만들지 않습니다
- 암호가 걸린 PDF는 건너뜁니다

## 빌드 (각 OS에서 한 번씩)

```bash
python -m venv .venv
# macOS/Linux: source .venv/bin/activate   Windows: .venv\Scripts\activate
pip install -r requirements.txt
python build.py
```

| OS | 결과물 (`dist/`) | 사용법 |
|---|---|---|
| macOS | `PDF압축.app` | 응용 프로그램 폴더/Dock/바탕화면에 두고 PDF를 아이콘에 드롭 |
| Windows | `PDF압축.exe` | 바탕화면에 두고(또는 바로가기) PDF를 아이콘에 드롭 |
| Linux | `PDFCompress` + `PDF압축.desktop` | `.desktop` 을 바탕화면에 복사 → 우클릭 '실행 허용' 후 드롭 |

Linux는 `python3-tk` 패키지가 필요합니다.
