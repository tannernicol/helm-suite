# GPU Setup -- Local AI Inference

## Why GPU?

Running LLMs locally means your conversations never leave your machine. A modern
NVIDIA GPU can run 7B-32B parameter models at usable speeds.

## What Uses the GPU

| Service | GPU Use | VRAM Needed |
|---------|---------|-------------|
| Ollama | LLM inference | 4-24 GB depending on model |
| Immich ML | Photo classification, face recognition, CLIP search | 2-4 GB |
| ComfyUI | Image generation (optional, not included) | 8+ GB |

## Prerequisites

- NVIDIA GPU (RTX 3060+ recommended, 8+ GB VRAM)
- Linux with proprietary NVIDIA drivers
- NVIDIA Container Toolkit

## Step 1: Install NVIDIA Drivers

### Ubuntu/Debian

```bash
sudo apt install -y nvidia-driver-550
sudo reboot
```

### Fedora

```bash
# Enable RPM Fusion
sudo dnf install -y \
  https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm \
  https://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm

sudo dnf install -y akmod-nvidia xorg-x11-drv-nvidia-cuda
sudo reboot
```

### Verify

```bash
nvidia-smi
# Should show your GPU, driver version, and CUDA version
```

## Step 2: Install NVIDIA Container Toolkit

```bash
# Add the repository
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | \
  sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg

curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

# Install
sudo apt update
sudo apt install -y nvidia-container-toolkit

# Configure Docker runtime
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

For Fedora, see the [NVIDIA docs](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html).

## Step 3: Verify Docker GPU Access

```bash
docker run --rm --gpus all nvidia/cuda:12.4.0-base-ubuntu22.04 nvidia-smi
```

You should see the same output as running `nvidia-smi` on the host.

## Step 4: Start GPU Services

### Ollama

```bash
cd infra/compose/ollama
docker compose up -d

# Pull a model
docker exec ollama ollama pull qwen2.5-coder:7b

# Test it
curl http://localhost:11434/api/generate -d '{
  "model": "qwen2.5-coder:7b",
  "prompt": "Write a hello world in Python",
  "stream": false
}'
```

### Immich (GPU-accelerated ML)

The Immich compose file automatically uses the CUDA ML container when
`GPU_ENABLED=true` in your `.env`.

```bash
cd infra/compose/immich
docker compose up -d
```

## VRAM Management

With a single GPU shared across services, you need to manage VRAM:

```bash
# Check VRAM usage
nvidia-smi

# If gaming or doing heavy GPU work, stop Ollama temporarily
docker stop ollama

# Resume after
docker start ollama
```

## Recommended Models by VRAM

| VRAM | Recommended Models |
|------|-------------------|
| 8 GB | qwen2.5:7b, qwen2.5-coder:7b |
| 16 GB | qwen2.5:14b, qwen2.5-coder:14b |
| 24+ GB | qwen2.5:32b, qwen2.5-coder:32b |

## Troubleshooting

### "CUDA out of memory"

- Check what's using VRAM: `nvidia-smi`
- Stop other GPU processes or use a smaller model
- Set `OLLAMA_MAX_LOADED_MODELS=1` in the compose file

### Container can't see GPU

1. Verify nvidia-container-toolkit: `nvidia-ctk --version`
2. Verify Docker runtime: `docker info | grep -i nvidia`
3. Restart Docker: `sudo systemctl restart docker`

### Driver mismatch after kernel update

```bash
# Fedora
sudo akmods --force
sudo reboot

# Ubuntu
sudo apt install --reinstall nvidia-driver-550
sudo reboot
```
