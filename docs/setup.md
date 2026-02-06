# Setup Guide

This guide is intentionally minimal and does not include real credentials or domains.

## Prerequisites
- Linux host with Docker or systemd services
- Private DNS for internal routing

## Staged Setup
1. Provision the host and storage volumes.
2. Deploy the reverse proxy and auth layer.
3. Bring up each app in isolation.
4. Validate backups and access controls.
