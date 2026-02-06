# Architecture Overview

Helm Suite is a private, local-first suite of personal tools with strict data boundaries.

## Goals
- Fast, private workflows for personal ops
- Minimal external dependencies
- Clear separation of concerns across tools

## Core Components
- UI layer: unified navigation and shared styling
- Service layer: individual apps (Money, Notes, etc.)
- Storage layer: local databases + encrypted backups

## Trust Boundaries
- Edge vs internal services
- Per-app data isolation
- Explicit approval for automation
