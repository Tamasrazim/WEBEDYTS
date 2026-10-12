; Defines what Inno Setup puts into the Windows installer, including the app files and installation details.

#ifndef AppVersion
  #define AppVersion "0.1.0"
#endif
#ifndef AppArch
  #define AppArch "x64"
#endif
#ifndef StageDir
  #define StageDir "..\..\build-desktop\desktop\Release"
#endif
#ifndef OutputDir
  #define OutputDir "..\..\build-desktop\packages"
#endif

[Setup]
AppId={{8A3D5EB7-6A57-4A4B-8F3B-E3A8D05C3F19}
AppName=WEBEDYTS
AppVersion={#AppVersion}
AppVerName=WEBEDYTS {#AppVersion}
AppPublisher=Robiul Rumman Razim
AppPublisherURL=https://tamasrazim.github.io/projects/webedyts/
AppSupportURL=https://github.com/Tamasrazim/WEBEDYTS/issues
AppUpdatesURL=https://github.com/Tamasrazim/WEBEDYTS
DefaultDirName={localappdata}\Programs\WEBEDYTS
DefaultGroupName=WEBEDYTS
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
ArchitecturesInstallIn64BitMode=x64 arm64
LicenseFile=..\..\LICENSE
SetupIconFile=..\branding\webedyts.ico
UninstallDisplayIcon={app}\WEBEDYTS.exe
OutputDir={#OutputDir}
OutputBaseFilename=WEBEDYTS-Setup-{#AppArch}-v{#AppVersion}
WizardStyle=modern
Compression=lzma2/ultra64
SolidCompression=yes
LZMAUseSeparateProcess=yes
SetupLogging=yes
Uninstallable=yes
VersionInfoDescription=WEBEDYTS Setup
VersionInfoProductName=WEBEDYTS
VersionInfoProductVersion={#AppVersion}
VersionInfoCompany=Robiul Rumman Razim
VersionInfoCopyright=Copyright (C) 2026 Robiul Rumman Razim

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked

[Files]
Source: "{#StageDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: "*.pdb,*.ilk"

[Icons]
Name: "{autoprograms}\WEBEDYTS"; Filename: "{app}\WEBEDYTS.exe"; WorkingDir: "{app}"
Name: "{autodesktop}\WEBEDYTS"; Filename: "{app}\WEBEDYTS.exe"; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
Filename: "{app}\WEBEDYTS.exe"; Description: "Launch WEBEDYTS"; WorkingDir: "{app}"; Flags: postinstall nowait skipifsilent
