# Repository Guidelines

## Project Structure & Module Organization
This repository is organized by KVM passthrough setup stages. Main folders are:
- `1.iommu/`: IOMMU checks and group inspection scripts.
- `2.modprobe/`: VFIO and kernel module examples.
- `3.libvirt/`: libvirt configuration notes.
- `4.bridge_network/`: bridge network setup scripts and XML.
- `99.sound/`: host sound helper scripts.
- `CreateVMInCommandline/`: VM XML templates.
- Process notes: `安装过程*.md`, troubleshooting in `解决问题/` and `避坑记录/`.

## Build, Test, and Development Commands
Most root-level content is scripts/docs; run scripts directly as needed:
- `bash 1.iommu/2.CheckIommuGroup.sh`: print IOMMU groups.
- `bash 99.sound/1.getCardNames.sh`: inspect audio devices.

## Coding Style & Naming Conventions
- Keep staged folder naming pattern: `<number>.<topic>`.
- Shell scripts should keep executable shebangs and descriptive lowercase names.
- Isolate host-specific values (PCI IDs, VM names) and document edits near changed lines.

## Testing Guidelines
- No global automated CI exists at repository root.
- Validate passthrough behavior manually on a non-production host:
  1. Start/stop VM with `virsh`.
  2. Verify module/device state via `lsmod` and `virsh nodedev-list --tree`.
  3. Inspect `/var/log/libvirt/hooks.log` for hook execution order.

## Commit & Pull Request Guidelines
Recent history contains very short messages (for example, `ok`, `qemu.ts`, `createvm`). For new work, use clearer commits:
- Format: `<area>: <imperative summary>` (example: `hooks: fix vfio reattach timing`).
- One logical change per commit; include config and docs together when coupled.
- PRs should include purpose, affected paths, validation commands run, and key logs/screenshots when behavior changes.

## Security & Configuration Tips
- Do not commit private host identifiers (serials, MAC/IP mappings, personal paths).
- Keep reusable templates as `example_*` files where possible.
- For GPU passthrough changes, ensure local console recovery is available before testing.
