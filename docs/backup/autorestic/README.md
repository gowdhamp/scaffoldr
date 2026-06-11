# Autorestic — Production Setup Guide

[Autorestic](https://autorestic.vercel.app/) is a high-level wrapper around [Restic](https://restic.net/) that manages multiple backup locations and backends from a single YAML file.

> Restic is the backup engine. Autorestic is the configuration and orchestration layer.

---

## When to Choose Autorestic

Autorestic is the right choice when:

- Your backup target is **object storage** — S3, Backblaze B2, Wasabi, Azure Blob, Google Cloud Storage
- You need to back up **one location to multiple backends simultaneously** (e.g., local + S3)
- You want a **portable single binary** with no system dependencies

For SSH-based remote targets (rsync.net, Hetzner Storage Box), see [Borgmatic](../borgmatic/README.md) instead.

---

## What Your Backup Must Cover

Same principle as borgmatic — a backup of a running application must include:

| Component | Method |
|-----------|--------|
| Application files | `from:` source directory |
| Database | Pre-backup dump into the source directory |
| Config files | Add to `from:` list |
| SSL certificates | Add to `from:` list |

---

## Database Backup — Export to File First

Like all filesystem backup tools, Restic cannot safely snapshot a live database. Export to a file first:

```yaml
hooks:
  before:
    - mkdir -p /srv/example.com/pgbackup
    - PGPASSWORD='...' pg_dump -U backup_user appdb \
        | gzip > /srv/example.com/pgbackup/appdb.sql.gz
```

The dump directory is inside the `from:` source path, so it is captured automatically with no extra configuration. The fixed filename (`appdb.sql.gz`) overwrites on each run — Restic's deduplication means only changed bytes are stored.

---

## Repository Encryption

**All Restic repositories require an encryption key at initialisation.** There is no option to skip it.

```yaml
backends:
  my-s3:
    type: s3
    path: s3.amazonaws.com/my-bucket/example.com
    key: your-strong-unique-passphrase
    requireKey: true
```

- Use a unique key per repository
- Store the key in a password manager or secrets vault — **never in version control**
- The key cannot be recovered if lost — the repository becomes permanently inaccessible

Initialise the repository before the first backup:

```bash
autorestic check -c autorestic.yml
```

Autorestic initialises any uninitialised backends automatically on first `check` or `backup`.

---

## Alerting and Monitoring

Autorestic does not have native healthchecks.io integration. Monitoring is configured via shell hooks:

```yaml
hooks:
  before:
    - curl -fsS -m 10 --retry 5 -o /dev/null "https://hc-ping.com/your-uuid/start"
  success:
    - curl -fsS -m 10 --retry 5 -o /dev/null "https://hc-ping.com/your-uuid"
  failure:
    - curl -fsS -m 10 --retry 5 -o /dev/null "https://hc-ping.com/your-uuid/fail"
```

A missed healthcheck ping after the grace period triggers an alert — cover the same start/success/failure lifecycle as borgmatic.

---

## Failure Handling

The `failure` hook runs if any step in the backup process fails:

```yaml
hooks:
  failure:
    - echo "Backup failed on $(hostname)" | mail -s "Autorestic Failure" ops@example.com
    - curl -fsS -m 10 --retry 5 -o /dev/null "https://hc-ping.com/your-uuid/fail"
```

**Common failure causes:**
- Invalid S3/B2 credentials or permissions
- Network connectivity to the object storage endpoint
- Database export failure (wrong credentials, DB not running)
- Repository locked — run `autorestic unlock -a -c autorestic.yml`

---

## Retention Policy

Autorestic uses Restic's `forget` command to prune old snapshots. Configure under `options.forget`:

```yaml
options:
  forget:
    keep-last: 5
    keep-daily: 7
    keep-weekly: 4
    keep-monthly: 6
    keep-yearly: 1
```

Set `forget: prune` on the location to reclaim storage space immediately after pruning. Use `forget: yes` if you want to mark snapshots as forgotten but reclaim space separately.

---

## Backup Scheduling

Autorestic does not have a built-in scheduler. Use cron or a systemd timer:

**Cron:**
```bash
0 2 * * * root autorestic --ci backup -a -c /etc/autorestic.yml >> /var/log/autorestic.log 2>&1
```

The `--ci` flag disables interactive output for clean log files.

---

## Audit and Compliance

| Requirement | Autorestic / Restic capability |
|-------------|-------------------------------|
| Encrypted backups at rest | AES-256 via `key` (mandatory) |
| Integrity verification | `autorestic exec -a -- check` |
| Retention enforcement | `options.forget` with prune |
| Backup completion evidence | healthchecks.io logs, `autorestic exec -a -- snapshots` |
| Off-site storage | Object storage backends (S3, B2, etc.) |
| Access control | IAM roles / bucket policies on the storage provider |

---

## See Also

- [Restic documentation](https://restic.readthedocs.io)
- [Autorestic documentation](https://autorestic.vercel.app/)
- [Backup strategy overview](../README.md)
