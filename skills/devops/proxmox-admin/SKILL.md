---
name: proxmox-admin
description: Manage Proxmox VE infrastructure — VMs, LXC containers, storage, networking, clusters, backups, API automation, Terraform, Ansible integration. Covers PVE 7.x/8.x.
---

# Proxmox Admin — VE Infrastructure Management

Complete skill for managing Proxmox Virtual Environment (PVE) clusters, VMs, LXC containers, storage, networking, and automation.

## Proxmox Architecture

```
┌─────────────────────────────────────────────────┐
│                  Proxmox Cluster                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │  Node 1   │  │  Node 2   │  │  Node 3   │      │
│  │ pve.local │──│ pve2.local│──│ pve3.local│      │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
│       │              │              │              │
│  ┌────┴──────────────┴──────────────┴────┐        │
│  │           Corosync Cluster            │        │
│  │        (quorum, HA, migration)        │        │
│  └────────────────────┬─────────────────┘        │
│                       │                           │
│  ┌────────────────────┴─────────────────┐        │
│  │              Ceph / ZFS / LVM         │        │
│  │           (shared storage)            │        │
│  └───────────────────────────────────────┘        │
│                                                   │
│  VMs:      QEMU/KVM (full virtualization)         │
│  LXC:      Linux Containers (lightweight)          │
│  API:      REST API v2 (pve.proxmox.com)          │
│  CLI:      qm, pct, pvesm, pveum, pvecm           │
└─────────────────────────────────────────────────┘
```

## Connection & Auth

### API Access
```bash
# API URL
https://pve.example.com:8006/api2/json

# Auth methods:
# 1. API Token (recommended for automation)
pveum useradd deploy@pve
pveum roleadd Admin -privs "Datastore.Allocate ..."  # or use built-in roles
pveum usermod deploy@pve -token my-token
# Usage: Authorization: PVEAPIToken=deploy@pve!my-token=secret

# 2. Password auth (interactive)
Username: root@pam or user@pve
Password: ****
```

### SSH Access
```bash
ssh root@pve.example.com
# or
ssh -i ~/.ssh/proxmox deploy@pve.example.com
```

## VM Management (QEMU/KVM)

### Create VM
```bash
# Create empty VM
qm create 100 --name ubuntu-server --memory 2048 --cores 2 --net0 virtio,bridge=vmbr0

# Add disk
qm set 100 --scsi0 local-lvm:32

# Add ISO
qm set 100 --ide2 local:iso/ubuntu-24.04.iso,media=cdrom

# Set boot order
qm set 100 --boot order=ide2

# Start
qm start 100

# Cloud-init VM (recommended)
qm create 100 --name ubuntu-ci --memory 4096 --cores 2 --net0 virtio,bridge=vmbr0
qm set 100 --ide2 local-lvm:cloudinit
qm set 100 --scsi0 local-lvm:32,ssd=1
qm set 100 --boot order=scsi0
qm set 100 --serial0 socket --vga serial0
qm set 100 --ipconfig0 ip=dhcp
qm set 100 --ciuser ubuntu --cipassword $(openssl passwd -6 'password')
qm set 100 --sshkey ~/.ssh/id_rsa.pub
qm start 100
```

### Clone VM
```bash
# Full clone (independent copy)
qm clone 100 101 --name ubuntu-server-2 --full

# Linked copy (fast, depends on template)
qm clone 100 102 --name test-vm --full 0

# Template (cannot be started, only cloned)
qm template 100
```

### VM Operations
```bash
qm start 100           # Start
qm stop 100            # Stop (force)
qm shutdown 100        # Graceful shutdown
qm reset 100           # Force reset
qm destroy 100         # Delete (DANGER: no confirmation with --purge)
qm destroy 100 --purge # Delete + remove from all configs

qm suspend 100         # Suspend to disk
qm resume 100          # Resume

qm migrate 100 pve2    # Live migrate to node pve2
qm migrate 100 pve2 --online 1

# Snapshot
qm snapshot 100 snap1 --description "before upgrade"
qm rollback 100 snap1  # Revert to snapshot
qm delsnapshot 100 snap1

# Monitor
qm status 100          # Status
qm monitor 100         # QEMU monitor (type 'quit' to exit)
```

### VM Config
```bash
cat /etc/pve/qemu-server/100.conf
# Example:
# boot: order=scsi0
# cores: 2
# memory: 2048
# net0: virtio=XX:XX:XX:XX:XX:XX,bridge=vmbr0
# scsi0: local-lvm:vm-100-disk-0,size=32G
# sockets: 1

# Edit config
qm set 100 --memory 4096
qm set 100 --cores 4
qm set 100 --cpu host  # Passthrough CPU features
```

## LXC Container Management

### Create LXC
```bash
# List available templates
pveam available --section system

# Download template
pveam download local ubuntu-24.04-standard_24.04-2_amd64.tar.zst

# Create container
pct create 200 local:vztmpl/ubuntu-24.04-standard_24.04-2_amd64.tar.zst \
  --name web-server \
  --memory 1024 \
  --cores 2 \
  --net0 name=eth0,bridge=vmbr0,ip=dhcp \
  --rootfs local-lvm:8 \
  --unprivileged 1 \
  --features keyctl=1,nesting=1  # nesting=1 for Docker-in-LXC

# Start
pct start 200

# Enter container
pct enter 200

# From host: run command in container
pct exec 200 -- apt update && apt upgrade -y
```

### LXC Operations
```bash
pct start 200
pct stop 200
pct shutdown 200
pct destroy 200 --purge  # DANGER

pct clone 200 201 --name web-server-2 --full
pct template 200      # Convert to template

pct migrate 200 pve2  # Live migrate

pct snapshot 200 snap1
pct rollback 200 snap1

pct mount 200         # Mount container filesystem (debugging)
pct unmount 200
```

### LXC Config
```bash
cat /etc/pve/lxc/200.conf
# Example:
# arch: amd64
# cores: 2
# memory: 1024
# net0: name=eth0,bridge=vmbr0,hwaddr=XX:XX:XX:XX:XX:XX,ip=dhcp,type=veth
# ostype: ubuntu
# rootfs: local-lvm:vm-200-disk-0,size=8G
# unprivileged: 1
# features: keyctl=1,nesting=1

# Edit
pct set 200 --memory 2048
pct set 200 --cores 4
pct set 200 --nesting 1       # Enable Docker
pct set 200 --features keyctl=1,nesting=1, fuse=1  # For Docker + FUSE
```

### LXC Privileges for Docker
```bash
# Unprivileged + Docker (most secure)
pct set 200 --features keyctl=1,nesting=1
# In container:
# /etc/docker/daemon.json: { "storage-driver": "overlay2" }

# Privileged (easier but less secure)
pct set 200 --unprivileged 0
pct set 200 --features nesting=1
```

## Storage Management

### Storage Types
```bash
# List storage
pvesm status

# Local directory (ISO, backups, templates)
pvesm add dir local-iso --path /var/lib/vz --content images,iso,vztmpl

# Local LVM
pvesm add lvm local-lvm --vgname pve

# LVM-Thin (recommended for VM disks)
pvesm add lvm-thin local-thin --thinpool data --vgname pve

# ZFS (recommended for data integrity)
pvesm add zfspool zfs-pool --pool tank/pve

# Ceph (shared across cluster)
pvesm add rbd ceph-pool --pool rbd --monhost 10.0.0.1,10.0.0.2

# NFS
pvesm add nfs nfs-backup --server 10.0.0.100 --export /backups --content backup

# SMB/CIFS
pvesm add cifs cifs-backup --server 10.0.0.100 --share backups --username backup
```

### ZFS Operations
```bash
# Create pool
zpool create tank /dev/sdb /dev/sdc mirror  # mirror
zpool create tank /dev/sdb /dev/sdc raidz1    # RAID-5 equivalent

# Dataset
zfs create tank/vm-disks
zfs set compression=lz4 tank/vm-disks
zfs set dedup=on tank/vm-disks  # Watch RAM usage!

# Snapshot
zfs snapshot tank/vm-disks@snap1
zfs rollback tank/vm-disks@snap1

# Monitor
zpool status
zfs list -t snapshot
```

### Move Disks
```bash
# Move VM disk between storage
qm move-disk 100 scsi0 zfs-pool --delete 1

# Resize disk
qm resize 100 scsi0 +20G   # Add 20GB
qm resize 100 scsi0 50G    # Set to 50GB
```

## Networking

### Bridges
```bash
cat /etc/network/interfaces
# auto vmbr0
# iface vmbr0 inet static
#     address 10.0.0.1/24
#     bridge-ports eno1
#     bridge-stp off
#     bridge-fd 0

# Create Linux Bridge
cat >> /etc/network/interfaces << 'EOF'
auto vmbr1
iface vmbr1 inet static
    address 10.10.0.1/24
    bridge-ports none
    bridge-stp off
    bridge-fd 0
    post-up echo 1 > /proc/sys/net/ipv4/ip_forward
    post-up iptables -t nat -A POSTROUTING -s '10.10.0.0/24' -o vmbr0 -j MASQUERADE
EOF

systemctl restart networking
```

### VLANs
```bash
# VLAN-aware bridge
auto vmbr0
iface vmbr0 inet manual
    bridge-ports eno1
    bridge-stp off
    bridge-fd 0
    bridge-vlan-aware yes
    bridge-vids 2-4094

# VM on specific VLAN
qm set 100 --net0 virtio,bridge=vmbr0,tag=100
pct set 200 --net0 name=eth0,bridge=vmbr0,tag=100
```

### OVS (Open vSwitch)
```bash
apt install openvswitch-switch

auto vmbr0
iface vmbr0 inet static
    address 10.0.0.1/24
    ovs_type OVSBridge
    ovs_ports eno1
    ovs_options other-config:hwaddr=XX:XX:XX:XX:XX:XX

auto eno1
iface eno1 inet manual
    ovs_type OVSPort
    ovs_bridge vmbr0
```

## Cluster Management

### Create Cluster
```bash
# On first node
pvecm create mycluster

# Join additional nodes
ssh root@pve2 pvecm add 10.0.0.1

# Check status
pvecm status
pvecm nodes
```

### HA (High Availability)
```bash
# Requirements: shared storage, fencing, min. 3 nodes for quorum

# Add HA resource
ha-manager add vm:100 --group prefer-pve1 --max_relocate 2
ha-manager add ct:200

# Configure groups
ha-group add prefer-pve1 --nodes pve1:100,pve2:50,pve3:10

# Monitor ha-manager status
ha-manager status
```

### Corosync
```bash
# Check quorum
corosync-quorumtool

# If lost quorum: force it (EMERGENCY ONLY on single-node recovery)
pvecm expected 1

# Edit corosync config
 nano /etc/cosync/corosync.conf
systemctl restart corosync
```

## Backup & Restore

### Backup
```bash
# Backup single VM
vzdump 100 --mode snapshot --compress zstd --storage local

# Backup all VMs
vzdump all --mode snapshot --compress zstd --storage local --mailto admin@example.com

# Schedule via cron
cat >> /etc/crontab << 'EOF'
0 2 * * * root vzdump all --mode snapshot --compress zstd --storage local --mailnotification failure --mailto admin@example.com --quiet 1
EOF

# Backup modes:
# snapshot: live backup (VM stays running)
# stop: stop VM, backup, restart
# suspend: suspend-then-snapshot (legacy)
```

### Restore
```bash
# Restore VM
qmrestore /var/lib/vz/dump/vzdump-qemu-100-2025_06_02-02_00_00.vma.zst 101

# Restore to new ID
qmrestore dump.vma.zst 200 --storage zfs-pool

# Restore LXC
pct restore 200 /var/lib/vz/dump/vzdump-lxc-200-2025_06_02-02_00_00.tar.zst
```

### Proxmox Backup Server (PBS)
```bash
# Add PBS storage
pvesm add pbs pbs-backup --server pbs.local --username backup@pve --password ***** --datastore tank --namespace production

# Backup to PBS
vzdump 100 --storage pbs-backup --mode snapshot --compress zstd --notes-template "{{guestname}}"
```

## User & Permission Management

### Users
```bash
# Create user
pveum useradd deploy@pve --password $(openssl passwd -6)

# API Token
pveum token add deploy@pve automation --privsep 0

# Groups
pveum	groupadd admins
pveum usermod deploy@pve -group admins

# Roles
pveum rolelist
pveum roleadd CustomRole -privs "VM.Allocate VM.Config.*

# ACL (Access Control)
pveum aclmod /vms/100 --roles PVEVMUser --users deploy@pve
pveum aclmod /storage/local-lvm --roles PVEDatastoreUser --users deploy@pve
pveum aclmod /roles/PVEAdmin --users admin@pve
```

## Python API (proxmoxer)

```python
!pip install proxmoxer requests -q

from proxmoxer import ProxmoxAPI

# Connect
proxmox = ProxmoxAPI(
    'pve.example.com',
    user='deploy@pve',
    token_name='automation',
    token_value='secret-token',
    verify_ssl=False,  # Set True with valid cert
)

# List all nodes
for node in proxmox.nodes.get():
    print(f"Node: {node['node']}, Status: {node['status']}")

# List VMs on node
for vm in proxmox.nodes('pve1').qemu.get():
    print(f"VM {vm['vmid']}: {vm['name']} ({vm['status']})")

# Create VM
proxmox.nodes('pve1').qemu.create(
    vmid=200,
    name='test-vm',
    memory=2048,
    cores=2,
    net0='virtio,bridge=vmbr0',
    scsi0='local-lvm:32',
    ostype='l26',          # Linux 2.6+ kernel
    onboot=1,
    startup='order=2,up=30,down=30',
)

# Start VM
proxmox.nodes('pve1').qemu(200).status.start.post()

# Get VM config
config = proxmox.nodes('pve1').qemu(200).config.get()
print(config)

# Update config
proxmox.nodes('pve1').qemu(200).config.post(memory=4096)

# Delete VM
proxmox.nodes('pve1').qemu(200).delete()

# Snapshots
proxmox.nodes('pve1').qemu(200).snapshot.post(snapname='before-upgrade', description='Pre-upgrade snapshot')
proxmox.nodes('pve1').qemu(200).snapshot('before-upgrade').post()  # Rollback

# Monitor
status = proxmox.nodes('pve1').qemu(200).status.current.get()
print(f"CPU: {status['cpu']*100:.1f}%, Mem: {status['mem']/1e9:.1f}GB/{status['maxmem']/1e9:.1f}GB")

# Storage
for storage in proxmox.storage.get():
    print(f"{storage['storage']}: {storage['content']}")

# Tasks
for task in proxmox.nodes('pve1').tasks.get(limit=10):
    print(f"{task['starttime']}: {task['type']} - {task['status']}")
```

## PVE Firewall

```bash
# Enable firewall on datacenter level
pvefirewall enable

# VM-specific firewall
cat /etc/pve/firewall/100.conf
# [RULES]
# IN ACCEPT -p tcp -dport 22
# IN ACCEPT -p tcp -dport 80
# IN ACCEPT -p tcp -dport 443
# IN DROP

# Or via command
qm set 100 --firewall 1
pve-firewall compile
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| VM won't start | `qm start 100 2>&1` for errors; check disk space; verify config syntax |
| Can't connect to web UI | `systemctl status pveproxy`; check firewall; `systemctl restart pveproxy` |
| Cluster quorum lost | `pvecm expected 1` (single node); fix network; add nodes back |
| ZFS pool degraded | `zpool status`; replace failed disk; `zpool replace tank old new` |
| Out of disk space | `df -h`; `zfs list`; clean old snapshots; `pvesm purge` |
| VM migration fails | Check network, shared storage, CPU compatibility |
| LXC can't start | Check nesting/keyctl features; verify template; `pct config 200` |
| HA failover not working | Check fencing; verify ha-manager status; test with `ha-manager migrate` |
| Slow VMs | Check CPU type (use 'host'), enable SSD emulation, add RAM |
| Backup fails | Check storage space; verify lock mode; `vzdump 100 --mode stop` |

## Emergency Recovery

```bash
# VM locked (stale lock)
qm unlock 100

# Corrupt VM config
cp /etc/pve/qemu-server/100.conf /etc/pve/qemu-server/100.conf.bak
# Edit and fix

# Single-node cluster (lost quorum)
systemctl stop pvedaemon
systemctl stop pve-cluster
pmxcfs -l                    # start in local mode
# Fix config...
systemctl start pve-cluster
systemctl start pvedaemon

# Reinstall kernel (broken update)
apt install pve-kernel-6.8
update-grub
reboot

# Access VM disk from host (VM won't start)
mount /dev/pve/vm-100-disk-0 /mnt
# Edit files...
umount /mnt
```

## Web UI Access
- **URL:** `https://pve.example.com:8006`
- **Auth:** Linux PAM (`root@pam`) or Proxmox VE auth (`user@pve`)
- **Dark mode:** `Datacenter → Options → Color Scheme`
- **2FA:** `Datacenter → Permissions → Two Factor`
