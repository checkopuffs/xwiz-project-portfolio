#!/usr/bin/env bash
# XWiz homelab: READ-ONLY inventory of a Linux node.
# No package installation, edits, network changes, service restarts, or disk writes.
set -u
section() { printf '\n===== %s =====\n' "$1"; }
section 'TIME AND HOST'
date -Is 2>/dev/null || date
hostnamectl 2>/dev/null || hostname
section 'PRODUCT'
for p in sys_vendor product_name product_version; do
  if [ -r "/sys/class/dmi/id/$p" ]; then printf '%s: ' "$p"; cat "/sys/class/dmi/id/$p"; fi
done
section 'OS'
cat /etc/os-release 2>/dev/null | grep -E '^(PRETTY_NAME|VERSION_ID|VERSION_CODENAME)=' || true
section 'CPU'
lscpu 2>/dev/null | grep -E '^(Architecture|CPU\(s\)|Model name|Virtualization|Thread\(s\) per core|Core\(s\) per socket):' || true
section 'MEMORY'
free -h 2>/dev/null || true
section 'DISKS AND MOUNTS'
lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS,MODEL 2>/dev/null || true
section 'NETWORK ADDRESSES'
ip -4 -brief addr 2>/dev/null || true
section 'DEFAULT ROUTE'
ip -4 route show default 2>/dev/null || true
section 'DNS'
if command -v resolvectl >/dev/null 2>&1; then resolvectl dns 2>/dev/null || true; else cat /etc/resolv.conf 2>/dev/null || true; fi
section 'VIRTUALIZATION CHECK'
if [ -r /proc/cpuinfo ]; then grep -Em1 'vmx|svm' /proc/cpuinfo >/dev/null && echo 'CPU virtualization flag present' || echo 'CPU virtualization flag not detected'; fi
section 'TEMPERATURES (if sensors installed)'
command -v sensors >/dev/null 2>&1 && sensors || echo 'sensors utility not available (optional)'
section 'DONE'
echo 'Read-only audit finished. No system changes made.'
