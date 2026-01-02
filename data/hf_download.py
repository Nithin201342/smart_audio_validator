#Custom script which downloads only specific files from a Hugging Face dataset repository
from huggingface_hub import snapshot_download

# Download ONLY wav files
snapshot_download(
    repo_id="TangRain/SingMOS-Pro",
    repo_type="dataset",
    allow_patterns=["wav/*"],
    local_dir="SingMOS-Pro",
    local_dir_use_symlinks=False
)

# Download metadata.json
snapshot_download(
    repo_id="TangRain/SingMOS-Pro",
    repo_type="dataset",
    allow_patterns=["metadata.json"],
    local_dir="SingMOS-Pro",
    local_dir_use_symlinks=False
)

print("Download completed successfully!")
