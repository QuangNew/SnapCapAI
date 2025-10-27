"""
PyInstaller hook for Azure Cognitive Services Speech SDK
Automatically includes all necessary DLLs and dependencies
"""

from PyInstaller.utils.hooks import collect_dynamic_libs, collect_data_files, collect_submodules

# Collect all DLLs from Azure Speech SDK
binaries = collect_dynamic_libs('azure.cognitiveservices.speech')

# Collect data files (if any)
datas = collect_data_files('azure.cognitiveservices.speech')

# Collect all submodules
hiddenimports = collect_submodules('azure.cognitiveservices.speech')

# Ensure critical DLLs are included
hiddenimports += [
    'azure',
    'azure.cognitiveservices',
    'azure.cognitiveservices.speech',
    'azure.cognitiveservices.speech.audio',
    'azure.cognitiveservices.speech.dialog',
]

print(f"✅ Azure Speech SDK hook loaded")
print(f"   - Binaries: {len(binaries)}")
print(f"   - Data files: {len(datas)}")
print(f"   - Hidden imports: {len(hiddenimports)}")
