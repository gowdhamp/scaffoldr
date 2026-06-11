# Borgmatic — Production Setup Guide

Borgmatic is a configuration-driven wrapper around [BorgBackup](https://www.borgbackup.org/). It handles scheduling, hooks, retention, integrity checks, and monitoring from a single YAML file.

> See the [sample config](./sample.yaml) for a fully annotated production example.

---

## What Your Backup Must Cover

A backup of a web application or server is incomplete if it only captures files on disk. A production backup should include:

| Component | Method |
|-----------|--------|
| Application files | Source directory in borgmatic |
| Database | Pre-backup dump (see below) |
| Configuration files | `/etc`, app config, `.env` files |
| SSL certificates | `/etc/letsencrypt` or equivalent |
| Cron jobs / systemd units | `/etc/cron.d`, `/etc/systemd/system` |

---

## Database Backup — Export to File First

Borgmatic is a filesystem backup tool. Running databases cannot be safely captured by snapshotting files while the database engine is writing — this produces a corrupt or inconsistent backup.

**The correct approach: export the database to a file before the snapshot runs**, then include that file in the backup.

Borgmatic's `before_backup` hook runs this automatically:

```yaml
before_backup:
    - mkdir -p /srv/example.com/pgbackup
    - PGPASSWORD='...' pg_dump -h localhost -U backup_user appdb \
        | gzip > /srv/example.com/pgbackup/appdb.sql.gz
```

**Why export to a file rather than stream directly to Borg:**
- The dump file is deduplicated — only changed bytes are stored after the first backup
- The dump is readable independently of Borg if you need a quick database restore
- Consistent snapshot: Borg captures the dump file atomically after it is fully written
- Dump files inside `source_directory` are automatically included — no extra config needed

**Supported dump types (via Scaffoldr):** `mysql`, `postgres`, `wordpress` (wp-cli), `docker-mysql`, `docker-postgres`

---

## Repository Encryption

**Encryption is mandatory for any off-site repository.**

Borg encrypts the repository at rest using AES-256. Without encryption, your data — including database dumps, credentials in config files, and private keys — is readable by anyone with access to the storage target.

```yaml
encryption_passphrase: 'your-strong-unique-passphrase'
```

**Rules:**
- Use a unique passphrase per repository — never reuse across projects
- Store the passphrase in a password manager or secrets vault (Bitwarden, 1Password, HashiCorp Vault)
- **Never commit the passphrase to version control**
- If the passphrase is lost, the repository cannot be decrypted — keep a secure backup of it

Initialise the repository with the matching encryption mode:

```bash
borgmatic rcreate -e repokey -c borgmatic.yaml
```

Use `repokey` (passphrase stored in the repo) for remote targets. Use `keyfile` if you need to store the key separately from the repository.

---

## Alerting and Monitoring

Silent backup failures are as dangerous as no backups. Configure monitoring so that a missed or failed backup immediately raises an alert.

Borgmatic has native [healthchecks.io](https://healthchecks.io) integration — no shell scripting required:

```yaml
healthchecks:
    ping_url: https://hc-ping.com/your-uuid-here
    states:
        - start
        - finish
        - fail
```

Borgmatic pings the URL at the start, on success, and on failure. If a ping is missed (e.g., the cron job did not run), healthchecks.io raises an alert after a configurable grace period.

**Self-hosted option:** healthchecks.io is open-source and can be self-hosted.  
**Alternatives:** Uptime Kuma push monitors, PagerDuty, Opsgenie, ntfy (borgmatic supports these natively too).

---

## Failure Handling

The `on_error` hook runs when any borgmatic step fails. Use it to emit an alert or write to a log:

```yaml
on_error:
    - echo "Backup failed for 'production-web'." | mail -s "Backup Failure" ops@example.com
```

With healthchecks monitoring enabled, the `/fail` ping is sent automatically — `on_error` is for additional notifications or remediation steps.

**Common failure causes:**
- SSH key or network connectivity to the repository
- Repository locked by a previous crashed run (`borgmatic borg break-lock`)
- Disk full at source or destination
- Database export failure (wrong credentials, DB not running)

---

## Repository Integrity Checks

Deduplication and compression mean that repository corruption, however rare, can affect multiple archives. Schedule regular integrity checks:

```yaml
checks:
    - name: repository   # Verifies repository structure and index
    - name: archives     # Verifies all archive contents
```

- `repository` — fast, checks index consistency. Run on every borgmatic invocation.
- `archives` — slower, reads all archive data. Run weekly or monthly via `frequency`.
- `data` — full data verification, reads and verifies every chunk. Use for compliance audits.

Add `frequency` to avoid running expensive checks on every backup:

```yaml
checks:
    - name: repository
    - name: archives
      frequency: 1 week
    - name: data
      frequency: 1 month
```

---

## Retention Policy

Define how many archives to keep. Borg prunes archives outside the retention window after each backup run.

```yaml
keep_daily: 7       # One archive per day for the last 7 days
keep_weekly: 4      # One per week for the last 4 weeks
keep_monthly: 6     # One per month for the last 6 months
keep_yearly: 1      # One per year
```

Tune based on your RTO and RPO requirements. Compliance environments often require monthly archives for 7 years.

---

## Backup Scheduling

Borgmatic is typically run via cron or a systemd timer. A daily backup at 2 AM:

**Cron:**
```bash
0 2 * * * root borgmatic -c /etc/borgmatic/config.yaml >> /var/log/borgmatic.log 2>&1
```

**Systemd timer** (recommended — handles missed runs and logging):
```ini
# /etc/systemd/system/borgmatic.timer
[Timer]
OnCalendar=02:00
Persistent=true
```

---

## Audit and Compliance

For environments subject to audit (SOC 2, HIPAA, ISO 27001, GDPR):

| Requirement | Borgmatic capability |
|-------------|----------------------|
| Encrypted backups at rest | AES-256 via `encryption_passphrase` |
| Integrity verification | `checks: data` |
| Retention policy enforcement | `keep_daily/weekly/monthly/yearly` |
| Backup completion evidence | Healthchecks.io logs, `borgmatic list` |
| Off-site storage | SSH remote repository |
| Access control | SSH key-based authentication to remote |

Retain borgmatic logs (`/var/log/borgmatic.log`) as evidence of backup execution. The `borgmatic list` command provides an archive inventory for audit review.

---

## See Also

- [Sample configuration](./sample.yaml)
- [BorgBackup documentation](https://borgbackup.readthedocs.io)
- [Borgmatic documentation](https://torsion.org/borgmatic/)
- [Backup strategy overview](../README.md)
