# XWiz homelab — Linux, Docker, Proxmox and monitoring

**Status:** Running, with improvements ongoing. No private infrastructure configuration is included in this public repository.

## Overview

- **Fedora Docker host:** Immich photo management, Plex media server, Pi-hole, Portainer, Homepage, Sonarr/Radarr, Prowlarr and qBittorrent, with VPN isolation for downloads in the lab.
- **Proxmox VE lab:** Two nodes organized into a cluster, with local SSD-based VM storage per node. **Not** shared storage; quorum requires careful handling in a two-node setup.
- **Ubuntu AI node:** Ollama/Open WebUI and the [XWiz Telegram bot](../xwiz-ai/README.md).
- **Small Debian NUC:** Uptime Kuma monitoring (and potential future infrastructure services).

## What I learned and practiced

System imaging, storage layouts, root filesystem sizing, Linux administration, Docker and container configuration, troubleshooting SELinux volume labels, remote SSH access, network DNS architecture, and understanding quorum limits.

## Tools and docs

- [`node-audit.sh`](scripts/node-audit.sh) — **read-only** Bash inventory of Linux OS, CPU, RAM, disks, interface addresses and DNS settings.

  ```bash
  bash projects/homelab/scripts/node-audit.sh
  ```

  This script does not edit host configuration, but **its output contains machine identifiers and network details**. Do not upload raw audit output publicly.

## Next improvements

- Build a proper backup/restore runbook and test restores.
- Add dashboards with meaningful service checks rather than shortcut links only.
- Revisit independent quorum voting for the two-node Proxmox setup.
- Document Immich storage expansion with a verified backup-first approach.

**Security note:** Real IP addresses, account identifiers, tokens, serial numbers, config files, volume data, and private topology are intentionally omitted.
