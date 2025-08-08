; Script gerado para instalar o aplicativo PedalPy
[Setup]
AppName=PedalPy
AppVersion=1.0
DefaultDirName={pf}\PedalPy
DefaultGroupName=PedalPy
OutputDir=dist
OutputBaseFilename=PedalPySetup
Compression=lzma
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "portuguese"; MessagesFile: "compiler:Languages\Portuguese.isl"

[Files]
Source: "dist\PedalPy.exe"; DestDir: "{app}"; Flags: ignoreversion
; Inclua outras DLLs ou arquivos adicionais, se necessário:
; Source: "dlls\*"; DestDir: "{app}\dlls"; Flags: ignoreversion recursesubdirs

[Icons]
Name: "{group}\PedalPy"; Filename: "{app}\PedalPy.exe"
Name: "{commondesktop}\PedalPy"; Filename: "{app}\PedalPy.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na área de trabalho"; GroupDescription: "Opções adicionais:"

[Run]
Filename: "{app}\PedalPy.exe"; Description: "Executar PedalPy"; Flags: nowait postinstall skipifsilent
