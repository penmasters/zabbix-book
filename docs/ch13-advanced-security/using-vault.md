# Secrets Management in Zabbix with HashiCorp Vault

## 1. Why Use a Secrets Manager?

In most monitoring environments, credentials are inevitably spread across many places: SNMP community strings, SSH private keys, database passwords, API tokens, and WMI credentials all need to reach the monitoring system somehow. Without a dedicated secrets manager, these credentials are typically stored in one or more of the following ways:

- **Plaintext in configuration files** — readable by anyone with file system access, often forgotten in backups or version control.
- **Hardcoded in templates or host macros** — while Zabbix's built-in *Secret text* macro type masks the value in the UI and omits it from template exports, the value is still stored in the Zabbix database in plaintext. Anyone with direct database access can read every credential without any additional barrier.
- **Plaintext storage in the Zabbix database** — all macro values, including those marked as *Secret text*, are stored unencrypted in the `globalmacro` and `hostmacro` tables. A compromised database exposes every credential in full.
- **Shared over email or chat** — no audit trail, no expiry, no revocation.

This approach creates significant operational and security risks:

| Risk | Description |
|------|-------------|
| **Credential sprawl** | The same password exists in dozens of config files across multiple servers. |
| **No rotation workflow** | Changing a credential requires hunting down every place it is used. |
| **No audit trail** | There is no log of who accessed a secret and when. |
| **Breach blast radius** | A compromised monitoring server exposes all monitored system credentials. |
| **Compliance failures** | Regulations like ISO 27001, SOC 2, PCI-DSS, and NIS2 require controlled access to credentials. |

### Enter Secrets Managers

Solutions like **HashiCorp Vault** and **CyberArk Conjur** solve these problems by providing a centralised, encrypted secrets store with:

- **Dynamic secrets** — credentials generated on demand with short TTLs, automatically revoked after use.
- **Fine-grained access policies** — each application or service receives only the secrets it needs.
- **Full audit logging** — every secret access is recorded with timestamp, identity, and path.
- **Token and lease management** — Vault auth tokens have configurable TTLs and are automatically expired, reducing the window of exposure if a token is compromised. Dynamic secrets (where supported) are generated on demand and automatically revoked after use.
- **Encryption at rest and in transit** — secrets never touch disk in plaintext.

Zabbix 6.4 and later supports native integration with HashiCorp Vault, allowing macros to reference secrets stored in Vault rather than holding the secret value directly. This keeps plaintext credentials out of the Zabbix database entirely.

---

## 2. HashiCorp Vault Overview

HashiCorp Vault is an open-source (with a BSL licence from 1.14+) secrets management tool. It provides:

- A **KV (Key/Value) secrets engine** for storing static secrets.
- An **audit backend** for logging all secret access.
- **Authentication methods** (AppRole, Token, LDAP, Kubernetes, AWS IAM, etc.).
- A RESTful API and CLI for interaction.

Zabbix uses Vault's **KV v1** secrets engine via the HTTP API, authenticating with either a **Vault token** or **AppRole** credentials.

---

## 3. Installing and Configuring Vault on RHEL

This section covers a minimal production-ready Vault installation on Red Hat Enterprise Linux 8/9 (or compatible distributions such as AlmaLinux, Rocky Linux).

### 3.1 Add the HashiCorp Repository

```bash
sudo dnf install -y dnf-plugins-core
sudo dnf config-manager --add-repo https://rpm.releases.hashicorp.com/RHEL/hashicorp.repo
sudo dnf install -y vault
```

### 3.2 Configure Vault

Create or edit `/etc/vault.d/vault.hcl`. The example below uses a file-based storage backend and enables TLS:

```hcl
ui = true

storage "file" {
  path = "/opt/vault/data"
}

listener "tcp" {
  address       = "0.0.0.0:8200"
  tls_cert_file = "/etc/vault.d/tls/vault.crt"
  tls_key_file  = "/etc/vault.d/tls/vault.key"
}

api_addr     = "https://vault.example.com:8200"
cluster_addr = "https://vault.example.com:8201"
```

!!! note

    For a development or lab environment, set `tls_disable = 1` inside the `listener "tcp"` block and use `http://` addresses. Never disable TLS in production.

```hcl
listener "tcp" {
  address     = "0.0.0.0:8200"
  tls_disable = 1
}
```

### 3.3 Create the Data Directory and Set Permissions

```bash
sudo mkdir -p /opt/vault/data
sudo chown -R vault:vault /opt/vault
sudo chmod 750 /opt/vault/data
```

### 3.4 Enable and Start the Vault Service

```bash
sudo systemctl enable vault
sudo systemctl start vault
```

### 3.5 Initialise Vault

Vault must be initialised once. This generates unseal keys and an initial root token.

```bash
export VAULT_ADDR='https://vault.example.com:8200'
vault operator init -key-shares=5 -key-threshold=3
```

Save the **5 unseal keys** and the **initial root token** securely. You need at least 3 keys to unseal Vault after every restart.

### 3.6 Unseal Vault

```bash
vault operator unseal   # repeat 3 times with different unseal keys
```

### 3.7 Authenticate as Root

```bash
vault login <initial-root-token>
```

Example output:

```bash
# vault login <root token>

Success! You are now authenticated. The token information displayed below
is already stored in the token helper. You do NOT need to run "vault login"
again. Future Vault requests will automatically use this token.

Key                  Value
---                  -----
token                <root token>
token_accessor       EuHT6HFt9QLZ6v8skiqSGyEa
token_duration       ∞
token_renewable      false
token_policies       ["root"]
identity_policies    []
policies             ["root"]
```

---

## 4. Configuring Vault for Zabbix

### 4.1 Enable the KV Secrets Engine

Zabbix requires the **KV version 1** secrets engine. Enable it on a path of your choice (e.g., `secret/`):

```bash
vault secrets enable -path=secret kv
```

!!! info

    Use KV v1, not KV v2. Zabbix does not support the v2 API metadata wrapper.

### 4.2 Store Zabbix Secrets

Create secrets using the structure `secret/<path>` where each secret is a key/value map:

```bash
# SNMP community string
vault kv put secret/zabbix/snmp community="public_prod_string"

# SSH credentials for a Linux host
vault kv put secret/zabbix/linux-ssh username="zabbix_monitor" password="S3cur3P@ss!"

# Database monitoring credentials
vault kv put secret/zabbix/mysql username="zbx_mon" password="DbP@ssw0rd"

# Windows WMI credentials
vault kv put secret/zabbix/windows username="DOMAIN\\zbx_wmi" password="W1nP@ss!"
```

### 4.3 Create a Policy for Zabbix

Create a Vault policy that grants read-only access to the Zabbix secrets path:

```hcl
mkdir /etc/vault.d/policies
# /etc/vault.d/policies/zabbix-read.hcl
path "secret/zabbix/*" {
  capabilities = ["read", "list"]
}
```

Apply the policy:

```bash
vault policy write zabbix-read /etc/vault.d/policies/zabbix-read.hcl
```

### 4.4 Create an AppRole for Zabbix (Recommended)

AppRole authentication is recommended for production because it avoids long-lived root tokens.

```bash
# Enable AppRole auth method
vault auth enable approle

# Create the Zabbix role
vault write auth/approle/role/zabbix \
    token_policies="zabbix-read" \
    token_ttl=1h \
    token_max_ttl=4h \
    secret_id_ttl=0   # 0 = never expires; set a value in production

# Retrieve the Role ID (not secret — can be stored openly)
vault read auth/approle/role/zabbix/role-id

# Generate a Secret ID (treat like a password)
vault write -f auth/approle/role/zabbix/secret-id
```

!!! note

    the `role_id` and `secret_id` values — you will need both to configure Zabbix.

### 4.5 Alternatively: Create a Static Token

For simpler setups, generate a token scoped to the Zabbix policy:

```bash
vault token create \
    -policy=zabbix-read \
    -ttl=0 \
    -display-name="zabbix-monitoring"
```

Note the `token` value.

---

## 5. Configuring the Zabbix Server for Vault
 
The Zabbix server daemon reads Vault configuration from `zabbix_server.conf`. Before editing, it is important to understand what each parameter actually controls — they serve distinct purposes.
 
### 5.1 Understanding VaultDBPath and VaultPrefix
 
These two parameters are often confused but do very different things:
 
**`VaultDBPath`** — used exclusively for retrieving the **Zabbix database credentials** (the `DBUser` and `DBPassword` connection parameters). It cannot be used if `DBUser` or `DBPassword` are already set in the config file. Zabbix looks for exactly two hardcoded keys at this path: `username` and `password`.
 
**`VaultPrefix`** — defines the URL prefix used to construct all Vault API requests, both for `VaultDBPath` and for macro secret resolution. If not set, Zabbix uses a default that automatically appends `/data/` after the mountpoint, which is the KV v2 API path structure. For KV v1, you must set this explicitly.
 
| Parameter | Purpose | Keys used |
|-----------|---------|-----------|
| `VaultDBPath` | Zabbix database credentials only | `username`, `password` (hardcoded) |
| `VaultPrefix` | URL prefix for all Vault API calls | n/a — affects path construction |
 
**Macro secrets** (the `vault:<path>:<key>` values on hosts and templates) are a separate mechanism and are **not** controlled by `VaultDBPath`. The `<path>` and `<key>` in a macro value are resolved using `VaultPrefix` as the base.
 
### 5.2 Edit `zabbix_server.conf`
 
Open `/etc/zabbix/zabbix_server.conf` and add or update the following parameters:
 
```ini
### HashiCorp Vault configuration ###
 
# Vault server URL (must include scheme and port)
VaultURL=https://vault.example.com:8200
 
# VaultPrefix — sets the full path prefix for all Vault API requests.
#
# For KV v1 (recommended for Zabbix):
VaultPrefix=/v1/secret/zabbix/
#
# For KV v2 (note the 'data' segment required by the v2 API):
# VaultPrefix=/v1/secret/data/zabbix/
#
# If VaultPrefix is not set, Zabbix defaults to KV v2 behaviour and
# automatically appends 'data' after the mountpoint.
 
# VaultDBPath — only set this if you want Vault to supply the Zabbix
# database credentials (DBUser / DBPassword). Leave commented out if
# DBUser and DBPassword are set directly in this file.
# The path is relative to VaultPrefix. Zabbix reads the keys
# 'username' and 'password' from this path.
#
# Example — with VaultPrefix=/v1/secret/zabbix/ this resolves to:
#   /v1/secret/zabbix/database
# VaultDBPath=database
 
# Authentication — uncomment ONE method.
 
# Option 1 — Static token
VaultToken=<your-vault-token>
 
# Option 2 — AppRole (recommended for production)
# VaultRoleID=<role_id>
# VaultSecretID=<secret_id>
```
 
### 5.3 TLS Certificate Verification
 
If Vault uses a certificate signed by an internal CA, configure the Zabbix server to trust it:
 
```ini
# Path to the CA certificate (PEM format) that signed Vault's TLS certificate
VaultTLSCAFile=/etc/zabbix/ssl/vault-ca.pem
```
 
If Vault uses a publicly trusted certificate, this parameter is not required.
 
### 5.4 Restart the Zabbix Server
 
```bash
sudo systemctl restart zabbix-server
sudo journalctl -u zabbix-server -f   # verify no Vault connection errors
```
 
---

## 6. Configuring the Zabbix Frontend for Vault

The Zabbix frontend also needs Vault access so that administrators can resolve and view macro values from the UI.

### 6.1 Edit `zabbix.conf.php`

Open `/etc/zabbix/web/zabbix.conf.php` and add the Vault configuration:

```php
// HashiCorp Vault
$DB['VAULT_URL'] = 'https://vault.example.com:8200';
$DB['VAULT_DB_PATH'] = 'secret';

// Authentication — choose one:

// Option 1: Static token
$DB['VAULT_TOKEN'] = '<your-vault-token>';

// Option 2: AppRole
// $DB['VAULT_ROLE_ID'] = '<role_id>';
// $DB['VAULT_SECRET_ID'] = '<secret_id>';

// TLS — only required if using a custom CA
// $DB['VAULT_CACERT'] = '/etc/zabbix/ssl/vault-ca.pem';
```

> **Security note:** The `zabbix.conf.php` file contains credentials. Ensure it is owned by the web server user and has permissions set to `640` at most:
> ```bash
> sudo chown apache:apache /etc/zabbix/web/zabbix.conf.php
> sudo chmod 640 /etc/zabbix/web/zabbix.conf.php
> ```

### 6.2 Restart the Web Server

```bash
sudo systemctl restart httpd   # or nginx + php-fpm
```

---

## 7. Using Vault Secrets as Macros in Zabbix

Once both the server and frontend are configured, you can reference Vault secrets in Zabbix macros using a special URI syntax.

### 7.1 Macro Syntax

Zabbix resolves a macro value from Vault when its value follows this pattern:

```
vault:<path>:<key>
```

| Component | Description |
|-----------|-------------|
| `vault:` | Prefix that tells Zabbix to fetch the value from Vault. |
| `<path>` | Path relative to `VaultDBPath`. E.g., `zabbix/snmp` maps to `secret/zabbix/snmp`. |
| `<key>` | The field name within the secret. |

### 7.2 Example: Global Macro for SNMP Community

**Secret stored in Vault:**
```bash
vault kv put secret/zabbix/snmp community="public_prod_string"
```

**Macro configuration in Zabbix UI:**

Navigate to **Administration → Macros** and create:

| Field | Value |
|-------|-------|
| Macro | `{$SNMP_COMMUNITY}` |
| Value | `vault:zabbix/snmp:community` |
| Type | `Secret text` |
| Description | SNMP community string from Vault |

Zabbix will resolve `vault:zabbix/snmp:community` by calling:
```
GET https://vault.example.com:8200/v1/secret/zabbix/snmp
```
and returning the value of the `community` key.

### 7.3 Example: Host-Level Macro for SSH Credentials

For SSH checks on Linux hosts, store the password in Vault and reference it as a host macro.

**Secret stored in Vault:**
```bash
vault kv put secret/zabbix/linux-ssh username="zabbix_monitor" password="S3cur3P@ss!"
```

**Host macro configuration:**

Navigate to the host → **Macros** tab and add:

| Macro | Value | Type |
|-------|-------|------|
| `{$SSH_USERNAME}` | `vault:zabbix/linux-ssh:username` | Secret text |
| `{$SSH_PASSWORD}` | `vault:zabbix/linux-ssh:password` | Secret text |

These macros can then be used in SSH agent items or scripts.

### 7.4 Example: Template-Level Macro for Database Monitoring

Store MySQL credentials per environment:

```bash
vault kv put secret/zabbix/mysql-prod username="zbx_mon" password="ProdDbPass!"
vault kv put secret/zabbix/mysql-dev  username="zbx_mon" password="DevDbPass!"
```

At the template level, define:

| Macro | Default Value | Description |
|-------|--------------|-------------|
| `{$MYSQL_USER}` | `vault:zabbix/mysql-prod:username` | MySQL monitoring user |
| `{$MYSQL_PASS}` | `vault:zabbix/mysql-prod:password` | MySQL monitoring password |

Override the macro at the **host** level for development hosts:

| Macro | Value |
|-------|-------|
| `{$MYSQL_PASS}` | `vault:zabbix/mysql-dev:password` |

This follows Zabbix's standard macro precedence: host-level overrides template-level.

### 7.5 How Resolution Works

When the Zabbix server needs to use a macro value:

1. It detects the `vault:` prefix in the macro value.
2. It constructs the Vault API URL: `{VaultURL}/v1/{VaultDBPath}/{path}`.
3. It authenticates using the configured token or AppRole credentials.
4. It retrieves the JSON response and extracts the value at the specified `{key}`.
5. The resolved plaintext value is used in the check — it is **never stored** in the Zabbix database.

> **Important:** The macro value stored in the Zabbix database is always the `vault:<path>:<key>` reference string, not the actual secret. This means database exports, backups, and UI views never expose the real credential.

---

## 8. TLS Configuration

For production use, all communication between Zabbix and Vault must be TLS-encrypted.

### 8.1 Using a Custom CA Certificate

If your Vault instance uses a certificate signed by an internal Certificate Authority:

**Zabbix Server (`zabbix_server.conf`):**
```ini
VaultTLSCAFile=/etc/zabbix/ssl/vault-ca.pem
```

**Zabbix Frontend (`zabbix.conf.php`):**
```php
$DB['VAULT_CACERT'] = '/etc/zabbix/ssl/vault-ca.pem';
```

### 8.2 Client Certificate Authentication (mTLS)

Zabbix does not currently support client certificates for Vault authentication natively. Use **AppRole** authentication as the recommended alternative for strong mutual authentication.

### 8.3 Verifying TLS Connectivity

Test Vault connectivity from the Zabbix server host before restarting the service:

```bash
curl --cacert /etc/zabbix/ssl/vault-ca.pem \
     -H "X-Vault-Token: <your-token>" \
     https://vault.example.com:8200/v1/secret/zabbix/snmp
```

A successful response looks like:

```json
{
  "request_id": "abc123...",
  "data": {
    "community": "public_prod_string"
  }
}
```

---

## 9. Verifying the Integration

Once Vault and Zabbix are configured, use the steps below to confirm that the integration is working end to end — from Vault connectivity through to macro resolution in an actual check.

### 9.1 Reload Secrets from Vault

The Zabbix server caches secret values after startup. When you add or update a secret in Vault, you can force the server to reload all secrets without a full restart using the runtime control option:

```bash
zabbix_server -R secrets_reload
```

This sends a signal to the running Zabbix server process instructing it to re-fetch all macros that reference Vault. Use this command whenever you:

- Add a new `vault:` macro to a host, template, or globally.
- Update a secret value in Vault.
- Rotate a Vault token or AppRole secret ID in `zabbix_server.conf`.

### 9.2 Verify Connectivity in the Server Log

Immediately after running `secrets_reload`, tail the Zabbix server log and look for confirmation or errors:

```bash
tail -f /var/log/zabbix/zabbix_server.log | grep -i vault
```

A successful reload produces output similar to:

```
zabbix_server [12345]: DEBUG: vault secrets reload started
zabbix_server [12345]: DEBUG: successfully retrieved secret: secret/zabbix/snmp
zabbix_server [12345]: DEBUG: successfully retrieved secret: secret/zabbix/linux-ssh
zabbix_server [12345]: DEBUG: vault secrets reload completed
```

If you see `failed to retrieve secret` or `403 Forbidden`, refer to the Troubleshooting section.

### 9.3 Verify Macro Resolution in the Frontend

The Zabbix frontend independently fetches secrets from Vault for display purposes. To verify it is working:

1. Navigate to **Administration → Macros** (for a global macro) or open a host and go to the **Macros** tab.
2. Find a macro with a `vault:` value, for example `{$SNMP_COMMUNITY}`.
3. Click the **eye icon** next to the macro value.
4. If the frontend can reach Vault and the token/AppRole is valid, the resolved plaintext value is shown momentarily.

If the eye icon shows an error or the value does not resolve, check the web server error log:

```bash
# Apache
sudo tail -f /var/log/httpd/error_log | grep -i vault

# Nginx
sudo tail -f /var/log/nginx/error.log | grep -i vault
```

### 9.4 Verify a Secret Reaches an Actual Check

The most definitive test is confirming a Vault-backed macro is used successfully in a real monitoring item.

**Example: test SNMP connectivity using the Vault-backed community string**

1. Create a simple SNMP item on a host (e.g., `sysDescr` OID `1.3.6.1.2.1.1.1.0`).
2. Set the **SNMP community** field to `{$SNMP_COMMUNITY}`, which resolves from `vault:zabbix/snmp:community`.
3. Navigate to **Monitoring → Latest data** and filter for the host.
4. If the item returns a value, the secret was successfully retrieved from Vault and used in the check.
5. If the item shows an authentication error specifically, the macro likely did not resolve — trigger a `secrets_reload` and recheck the log.

**Example: verify using the Get Value button**

For quicker feedback without waiting for the poller:

1. Open the item configuration.
2. Click **Test** → **Get value**.
3. Check whether the item returns data or an authentication error.

### 9.5 Confirm No Plaintext in the Zabbix Database

To confirm that Vault-backed macro values are stored as references and not as plaintext secrets, query the database directly:

```sql
-- Check global macros
SELECT macro, value FROM globalmacro WHERE value LIKE 'vault:%';

-- Check host macros
SELECT macro, value FROM hostmacro WHERE value LIKE 'vault:%';
```

All rows should show the `vault:<path>:<key>` reference string, never the resolved secret value. This confirms that the plaintext credential never touches the Zabbix database.

---

## 10. Troubleshooting

### Zabbix Server Cannot Connect to Vault

Check the Zabbix server log for errors:

```bash
grep -i vault /var/log/zabbix/zabbix_server.log
```

Common errors and resolutions:

| Error | Cause | Resolution |
|-------|-------|------------|
| `SSL certificate problem` | Vault uses a self-signed or internal CA cert | Set `VaultTLSCAFile` to the CA certificate path |
| `403 Forbidden` | Token/AppRole lacks permission | Review and reapply the Vault policy |
| `connection refused` | Vault is sealed or not running | Unseal Vault: `vault operator unseal` |
| `invalid path` | `VaultDBPath` or secret path is incorrect | Verify with `vault kv list secret/zabbix/` |
| `macro not resolved` | `vault:` prefix missing or wrong key name | Check macro value syntax: `vault:<path>:<key>` |

### Verify a Secret is Accessible

From the Zabbix server host, test with the same credentials Zabbix uses:

```bash
# Token auth
vault login <token>
vault kv get secret/zabbix/snmp

# AppRole auth
vault write auth/approle/login \
    role_id="<role_id>" \
    secret_id="<secret_id>"
```

### Check Vault Audit Log

If Vault's audit backend is enabled, you can trace exactly what Zabbix is requesting:

```bash
# Enable file audit log (if not already enabled)
vault audit enable file file_path=/var/log/vault/audit.log

# Tail the audit log
sudo tail -f /var/log/vault/audit.log | jq '.request.path'
```

---

*This chapter covers Zabbix 7.4 with HashiCorp Vault using the KV v1 secrets engine. For the most current parameter names and defaults, always refer to the [official Zabbix documentation](https://www.zabbix.com/documentation/7.4/en/manual/config/secrets/hashicorp).*
