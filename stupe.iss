[Setup]
; --- Informações do Aplicativo ---
AppId={{D1A39E6D-30D1-4E6D-A5B2-1B6553B18F21}}
AppName=Efeito Voz Guitarra
AppVersion=1.5.2
AppPublisher=Jefferson Jaily Felix
AppContact=jeffersson.jaily@gmail.com
DefaultDirName={autopf}\Efeito Voz Guitarra
DefaultGroupName=Efeito Voz Guitarra
OutputBaseFilename=setup_efeito_voz_guitarra
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Files]
Source: "dist\Efeito Voz Guitarra.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "G:\DIO\pedais\icon\icon.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "shortcuts.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "layout_config.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "backend\*.py"; DestDir: "{app}\backend"; Flags: ignoreversion
Source: "backend\effects_config.py"; DestDir: "{app}\backend"; Flags: ignoreversion
Source: "backend\voz\effects_config.py"; DestDir: "{app}\backend\voz"; Flags: ignoreversion
Source: "backend\effects\*.py"; DestDir: "{app}\backend\effects"; Flags: ignoreversion
Source: "backend\voz\*.py"; DestDir: "{app}\backend\voz"; Flags: ignoreversion
Source: "backend\effects\cpp_effects\*.pyd"; DestDir: "{app}\backend\effects\cpp_effects"; Flags: ignoreversion
Source: "ui\*.py"; DestDir: "{app}\ui"; Flags: ignoreversion

[Icons]
Name: "{group}\Efeito Voz Guitarra"; Filename: "{app}\Efeito Voz Guitarra.exe"; IconFilename: "{app}\icon.ico"
Name: "{autodesktop}\Efeito Voz Guitarra"; Filename: "{app}\Efeito Voz Guitarra.exe"; IconFilename: "{app}\icon.ico"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Run]
Filename: "{app}\Efeito Voz Guitarra.exe"; Description: "Iniciar Efeito Voz Guitarra"; Flags: nowait postinstall

[UninstallDelete]
Type: filesandordirs; Name: "{app}"
