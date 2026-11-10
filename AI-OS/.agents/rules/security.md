# Security Governance & Kernel Guardrails

## 1. Non-Configurable Kernel Guardrails
These security invariants cannot be disabled, weakened, or overridden by any configuration profile, environment variable, or agent prompt:

1. **Secret Redaction**:
   - All outgoing and persisted data streams (standard output, standard error, database records, prompts, task handoffs, and audit logs) must pass through the secret redaction engine.
   - Any detected credential token is replaced with the literal string `[REDACTED_SECRET]`.
   - Covered credential formats:
     - OpenAI API keys: `sk-[a-zA-Z0-9_\-]{20,}`
     - Anthropic API keys: `sk-ant-[a-zA-Z0-9_\-]{20,}`
     - Google / Gemini API keys: `AIza[0-9A-Za-z\-_]{30,40}`
     - GitHub Personal Access Tokens (classic `ghp_` and fine-grained `github_pat_`)
     - AWS Access Key IDs (`AKIA...`, `ASIA...`) and Secret Keys
     - PEM formatted private keys (`-----BEGIN ... PRIVATE KEY-----`)
     - Bearer tokens in HTTP Authorization headers
     - URI embedded passwords (`protocol://user:password@host`)
     - Common configuration key assignments (`password = ...`, `api_key = ...`)

2. **Workspace Boundary & Destructive Action Prohibition**:
   - The canonical workspace root is `~/Documents/Antigravity/AI-OS/`.
   - Autonomous mutating operations (`write`, `delete`, `install`, `execute`) targeting paths outside the canonical workspace root are strictly FORBIDDEN and cannot be auto-approved.
   - Any external destructive request is forcibly intercepted, demoted to `ASK` or `DENY`, and marked with `guardrail_enforced = True`.
   - Path resolution must use realpath canonicalization to prevent path traversal (`../`) and symlink escape attacks.
   - Root (`/`), home (`~`), and system directories (`/etc`, `/var`, `/tmp` outside sandbox) are non-negotiably protected.

3. **Destructive Shell Command Denylist**:
   - The following commands and patterns are unconditionally blocked:
     - Root or recursive file removal: `rm -rf /`, `rm -rf ~`, `rm -rf /*`, `rm -rf /tmp`
     - Filesystem destruction: `mkfs`, `mkfs.ext4`, `dd if=`, `> /dev/sda`
     - Privilege escalation: `sudo`, `su`
     - System shutdown / reboot: `shutdown`, `reboot`, `poweroff`, `init`
     - Fork bombs: `:(){ :|:& };:`
     - Unsafe global permission changes: `chmod -R 777 /`
