; ============================================================
; SnapCapAI - Inno Setup Installer Script
; Version: 2.0
; Created: January 2026
; ============================================================

[Setup]
; App Information
AppName=SnapCapAI
AppVersion=2.0
AppPublisher=QuangNew
AppPublisherURL=https://github.com/QuangNew/SnapCapAI
AppSupportURL=https://github.com/QuangNew/SnapCapAI/issues
AppUpdatesURL=https://github.com/QuangNew/SnapCapAI/releases
AppId={SnapCapAI-A5F3-4B2E-8C9D-1E4F6A7B8C9D}

; Installation Settings
DefaultDirName={autopf}\SnapCapAI
DefaultGroupName=SnapCapAI
AllowNoIcons=yes
DisableProgramGroupPage=yes

; Output Settings
OutputDir=Output
OutputBaseFilename=SnapCapAI-Setup
SetupIconFile=SnapCapAI.ico
UninstallDisplayIcon={app}\SnapCapAI.ico

; Compression
Compression=lzma2/ultra64
SolidCompression=yes

; Privileges and Architecture
PrivilegesRequired=admin
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

; Wizard Style
WizardStyle=modern
DisableWelcomePage=no

; Uninstall Settings
UninstallDisplayName=SnapCapAI
UninstallFilesDir={app}\uninst

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: checkedonce
Name: "startup"; Description: "Start SnapCapAI with &Windows"; GroupDescription: "Startup options:"; Flags: checkedonce

[Files]
; Main executable
Source: "dist\SnapCapAI.exe"; DestDir: "{app}"; Flags: ignoreversion

; Icon file
Source: "SnapCapAI.ico"; DestDir: "{app}"; Flags: ignoreversion

; Source Python files
Source: "src\*.py"; DestDir: "{app}\src"; Flags: ignoreversion recursesubdirs

[Icons]
; Start Menu shortcut
Name: "{autoprograms}\SnapCapAI"; Filename: "{app}\SnapCapAI.exe"; IconFilename: "{app}\SnapCapAI.ico"

; Desktop shortcut
Name: "{autodesktop}\SnapCapAI"; Filename: "{app}\SnapCapAI.exe"; IconFilename: "{app}\SnapCapAI.ico"; Tasks: desktopicon

; Uninstaller in Start Menu
Name: "{autoprograms}\Uninstall SnapCapAI"; Filename: "{uninstallexe}"

[Registry]
; Auto-start with Windows (if user selected the option)
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "SnapCapAI"; ValueData: """{app}\SnapCapAI.exe"""; Tasks: startup; Flags: uninsdeletevalue

[Run]
; Option to launch app after installation
Filename: "{app}\SnapCapAI.exe"; Description: "Launch SnapCapAI"; Flags: nowait postinstall skipifsilent shellexec

[Messages]
; Custom messages
WelcomeLabel2=This will install [name/ver] on your computer.%n%nSnapCapAI is a powerful screen capture and AI transcription tool that runs in stealth mode with global hotkeys.%n%nIt is recommended that you close all other applications before continuing.

[Code]
// Note: Shortcuts are created normally. Users running the app will get UAC prompt
// if admin privileges are needed for stealth mode features.

function InitializeSetup(): Boolean;
begin
  Result := True;
end;
