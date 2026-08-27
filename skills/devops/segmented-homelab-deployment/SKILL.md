---
name: segmented-homelab-deployment
description: Build and deploy a fully automated OpenWrt Router-on-a-Stick homelab stack with OPNsense, Proxmox, CrowdSec, banIP, SQM CAKE, and validation/compliance tests.
---

# Segmented Homelab Deployment

Production-grade, zero-touch automation for a defense-in-depth homelab:
- OpenWrt Image Builder pipeline for Raspberry Pi 4 (bcm27xx/bcm2711)
- Cross-stack Ansible orchestration for OPNsense + Proxmox + Prometheus
- Automated validation and compliance checks (VLAN isolation, nftables, CrowdSec, CAKE, metrics)

## Deliverables in this skill

- `scripts/build_openwrt_image.sh`
- `templates/openwrt-image/files/...` (full first-boot config overlay)
- `templates/ansible/playbook.yml`
- `scripts/verify_stack.sh`

## Usage

### 1) Build zero-touch OpenWrt image

```bash
cd skills/devops/segmented-homelab-deployment/scripts
./build_openwrt_image.sh
```

Artifact output:
- `build/output/openwrt-24.10.0-bcm27xx-bcm2711-rpi-4-ext4-factory.img.gz`

### 2) Provision supporting infrastructure

```bash
cd ../templates/ansible
export OPNSENSE_API_KEY='set-in-shell'
export OPNSENSE_API_SECRET='set-in-shell'
ansible-playbook -i inventory.ini playbook.yml
```

### 3) Run compliance validation

```bash
cd ../../scripts
./verify_stack.sh
```
