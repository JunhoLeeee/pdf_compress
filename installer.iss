; Windows 설치 프로그램 (Inno Setup 6). python build.py 로 dist\PDFCompress 를 만든 뒤:
;   iscc installer.iss            → dist\PDFCompress-Windows-Setup.exe
; 버전은 iscc /DAppVersion=1.2.0 installer.iss 처럼 넘길 수 있다.

#ifndef AppVersion
  #define AppVersion "0.0.0"
#endif

[Setup]
AppId={{5B8C2E61-3F4A-4D7B-9E0C-8A1F6D2B7C34}
AppName=PDF압축
AppVersion={#AppVersion}
AppPublisher=JunhoLeeee
AppPublisherURL=https://github.com/JunhoLeeee/pdf_compress
; 관리자 권한 없이 현재 사용자에게만 설치 (%LOCALAPPDATA%\Programs\PDF압축)
PrivilegesRequired=lowest
DefaultDirName={autopf}\PDF압축
DefaultGroupName=PDF압축
DisableProgramGroupPage=yes
OutputDir=dist
OutputBaseFilename=PDFCompress-Windows-Setup
SetupIconFile=assets\icon.ico
UninstallDisplayIcon={app}\PDFCompress.exe
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "korean"; MessagesFile: "compiler:Languages\Korean.isl"

[Tasks]
Name: "desktopicon"; Description: "바탕화면에 아이콘 만들기 (PDF를 이 아이콘에 끌어다 놓으면 압축)"; GroupDescription: "추가 작업:"

[Files]
Source: "dist\PDFCompress\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\PDF압축"; Filename: "{app}\PDFCompress.exe"
Name: "{group}\PDF압축 제거"; Filename: "{uninstallexe}"
Name: "{autodesktop}\PDF압축"; Filename: "{app}\PDFCompress.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\PDFCompress.exe"; Description: "PDF압축 실행"; Flags: nowait postinstall skipifsilent
