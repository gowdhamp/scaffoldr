# Backup Strategy Guide

## Why Backups Matter

Data loss is not a matter of *if* — it is a matter of *when*. Hardware fails, humans make mistakes, ransomware encrypts, and cloud providers have outages. A backup is the only guarantee that an incident does not become permanent.

**Common causes of data loss:**

| Cause | Example |
|-------|---------|
| Hardware failure | Disk crash, RAID degradation |
| Human error | Accidental deletion, failed migration |
| Ransomware | Encrypted or destroyed production data |
| Software bug | Corrupted write, bad database upgrade |
| Provider outage | Cloud storage region failure |

> **A backup that has never been restored is not a backup.** Test your restores regularly.

---

## The 3-2-1 Rule

The industry-standard baseline for data protection:

| | Rule |
|-|------|
| **3** | Keep at least 3 copies of your data |
| **2** | Store copies on 2 different types of media |
| **1** | Keep 1 copy offsite |

The original plus two backups, at least one of which is geographically separate from the source.

---

## Local Backups

A local backup lives on the same machine, same rack, or same data centre as the source data.

**When to use:**
- Fast recovery is required (RTO in minutes)
- Network bandwidth to an offsite target is limited
- As the second copy in a 3-2-1 strategy

**Drawbacks:**
- Vulnerable to the same physical events as the source (fire, flood, power failure)
- Ransomware can reach locally mounted drives if accessible from the infected host
- Provides no protection against site-level incidents

**Local backups alone are not sufficient for production data.**

---

## Off-site Backups

Off-site backups store data in a physically or logically separate location, isolated from the primary site.

**When to use:**
- Production systems where data loss is unacceptable
- Compliance requires geographic separation (GDPR, HIPAA, SOC 2)
- Protection against ransomware is required (immutable or append-only targets)
- Site-level disaster recovery

**Types of off-site storage:**

| Type | Examples | Best for |
|------|----------|----------|
| Remote server (SSH) | rsync.net, Hetzner Storage Box | BorgBackup, low cost, simple |
| Object storage | S3, Backblaze B2, Wasabi | Restic, scalable, pay-per-GB |
| Dedicated backup service | BorgBase, Storj | Optimised for Borg/Restic, append-only support |
| Tape / air-gapped | LTO tape, offline drives | Compliance-grade, ransomware-proof |

---

## Borgmatic vs Restic (Autorestic)

Both tools use **deduplication** and **encryption at rest**. The right choice depends primarily on your storage target.

| | Borgmatic (BorgBackup) | Restic (via Autorestic) |
|--|------------------------|-------------------------|
| **Storage targets** | SSH / local | S3, B2, SFTP, Azure, local + more |
| **Deduplication** | Variable-length chunking | Content-defined chunking |
| **Encryption** | AES-256 + HMAC-SHA256 | AES-256-CTR + Poly1305 |
| **Monitoring** | Native healthchecks.io | Via shell hooks |
| **Config format** | Single YAML | Single YAML (autorestic wrapper) |
| **Multi-backend** | One repository per config | Multiple backends per location |
| **Maturity** | High (since 2015) | High (Restic since 2014) |

**Choose Borgmatic when:**
- Your target is a remote server over SSH (rsync.net, Hetzner, your own VPS)
- You want native healthchecks.io monitoring with no extra scripting
- You are on Ubuntu LTS and want a system package (`apt install borgmatic`)

**Choose Restic / Autorestic when:**
- Your target is object storage (S3, Backblaze B2, Wasabi, Azure Blob)
- You need to replicate to multiple backends simultaneously
- You want a more portable, single-binary tool

---

## Production Backup Checklist

Before considering a backup setup production-ready:

- [ ] 3-2-1 strategy confirmed (local + offsite)
- [ ] All databases exported to files before the snapshot runs
- [ ] Repository encrypted with a strong, unique passphrase
- [ ] Passphrase stored in a password manager or secrets vault — **not in version control**
- [ ] Monitoring and alerting configured (start, finish, and failure signals)
- [ ] Retention policy defined — daily, weekly, monthly, yearly
- [ ] Repository integrity checks scheduled
- [ ] Restore procedure documented and tested
- [ ] Backup logs reviewed on a regular cadence

---

## Tool-specific Guides

- [Borgmatic](./borgmatic/README.md)
- [Autorestic](./autorestic/README.md)
