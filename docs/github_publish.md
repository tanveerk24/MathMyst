# GitHub publication and account setup

The repository is configured as `https://github.com/tanveerk24/MathMyst.git`.
Its original commit and MIT license were preserved. Completed implementation,
tests, documentation, and screenshots are published on `main`.

Publication succeeded on **6 November 2026** after signing in as `tanveerk24`.
The push advanced the existing remote branch from `86405e2` to `18c434b`,
preserving its history. The repository selects `tanveerk24` through its local
`credential.https://github.com.username` setting.

The earlier attempt with the other account failed with this response:

```text
remote: Permission to tanveerk24/MathMyst.git denied to tanveerk13.
fatal: unable to access 'https://github.com/tanveerk24/MathMyst.git/': The requested URL returned error: 403
```

That attempt used `tanveerk13`, which lacked write access. Signing in as
`tanveerk24` resolved the error. The local application is independent of GitHub.

## Reconnect from Windows PowerShell if needed

Sign in as the repository owner, or another account with write access. For the
owner account, run these commands and complete the browser sign-in yourself:

```powershell
$gitExecutable = 'C:\Program Files\Git\cmd\git.exe'
$projectDirectory = 'C:/Users/Tanveer/OneDrive/Desktop/dbms project/MathMyst'
& $gitExecutable -c "safe.directory=$projectDirectory" -C $projectDirectory credential-manager github login --username tanveerk24 --browser
& $gitExecutable -c "safe.directory=$projectDirectory" -C $projectDirectory -c credential.https://github.com.username=tanveerk24 push -u origin main
```

The account selection applies only to this command. The `safe.directory` value
also applies only to this known checkout and avoids an ownership error when Git
runs under your normal Windows account after a sandbox created the repository.
Neither command changes global Git settings or removes another account's login.
Do not paste access tokens or passwords into this repository or its remote URL.

Alternatively, have the repository owner grant `tanveerk13` write access and
accept any invitation before retrying the push with that account.

If GitHub CLI is installed instead, `gh auth login --hostname github.com --web`
and `gh auth setup-git` provide another authentication method. GitHub CLI is not
installed on the machine used for this verification. VS Code's Accounts menu
also offers GitHub sign-in; ensure the selected account has repository access.

If a later push is rejected because the remote gained commits, fetch and inspect
those changes before integrating them. Never force-push over the remote history.
