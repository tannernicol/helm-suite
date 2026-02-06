# Contributing

Contributions are welcome. If you find a bug or have an idea, open an issue first so we can discuss.

## How to contribute

1. Fork the repo
2. Create a feature branch (`git checkout -b my-feature`)
3. Make your changes
4. Test with `./scripts/security-audit` and `./scripts/homelab status`
5. Open a pull request

## Guidelines

- Keep changes focused -- one PR per feature or fix
- Follow existing code style (bash uses `set -euo pipefail`)
- No real credentials, IPs, or secrets in committed code
- Docker Compose services should bind to `127.0.0.1`, never `0.0.0.0`
- Test on at least one of: Ubuntu 22.04+, Fedora 39+, Debian 12+
