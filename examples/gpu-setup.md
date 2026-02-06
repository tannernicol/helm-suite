# GPU Passthrough Guide

This guide covers GPU passthrough for Docker containers on Linux with NVIDIA
GPUs. This is required for Ollama (LLM inference) and Immich (photo ML).

## Quick Check

```bash
# Is your GPU detected?
nvidia-smi

# Is the container toolkit installed?
nvidia-ctk --version

# Can Docker see the GPU?
docker run --rm --gpus all nvidia/cuda:12.4.0-base-ubuntu22.04 nvidia-smi
```

If all three work, you're good. Start GPU services:

```bash
cd infra/compose/ollama && docker compose up -d
cd infra/compose/immich && docker compose up -d
```

## Full Setup (from scratch)

See [docs/GPU.md](../docs/GPU.md) for the complete installation guide covering:

1. NVIDIA driver installation (Ubuntu, Fedora)
2. NVIDIA Container Toolkit setup
3. Docker runtime configuration
4. Starting GPU services
5. VRAM management
6. Recommended models by VRAM size
7. Troubleshooting

## Docker Compose GPU Configuration

Add this to any service that needs GPU access:

```yaml
services:
  myservice:
    image: myimage:latest
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1              # Number of GPUs
              capabilities: [gpu]   # Add 'video' for transcoding
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
      - NVIDIA_DRIVER_CAPABILITIES=compute,utility
```

## CPU-Only Fallback

If you don't have a GPU, modify the compose files:

1. Remove the `deploy.resources.reservations` block
2. Remove NVIDIA environment variables
3. For Immich, change the ML image from `-cuda` to the default tag

Ollama will automatically fall back to CPU inference (slower but functional).
