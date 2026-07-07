[Setup]
AppName=Kvaritcraft
AppVersion=2.0
DefaultDirName={autopf}\Kvaritcraft
DefaultGroupName=Kvaritcraft
OutputDir=output
WizardStyle=modern dark
OutputBaseFilename=KvaritcraftSetup
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\main\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "dist\main\main.exe"; DestDir: "{app}"; DestName: "Kvaritcraft.exe"; Flags: ignoreversion

[Icons]
Name: "{commondesktop}\Kvaritcraft"; Filename: "{app}\Kvaritcraft.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Создать ярлык на рабочем столе"; GroupDescription: "Дополнительно:"

[Run]
Filename: "{app}\Kvaritcraft.exe"; Description: "Запустить Kvaritcraft"; Flags: nowait postinstall skipifsilent

[Languages]
Name: "ru"; MessagesFile: "compiler:Languages\Russian.isl"