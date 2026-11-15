# Changelog

Releases of the HPC Terminal. The [Trellis Tools](https://github.com/Gardiner-Lab/Trellis-Tools) suite pins
a version of it as `TERMINAL_VERSION`, so a release here changes no installation until the suite is updated
to use it.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the project uses [semantic versioning](https://semver.org/).

## [Unreleased]

## [0.2.0] - 2026-11-15

### Added
- **An overview of open sessions** on the HPC Terminal page: everyone's for an administrator, their labs' members'
  for a lab lead or lab administrator (the suite's lab_members). Who is connected to which machine, since when,
  whether a browser has it open and from where; never what is on the screen. They can end a session (its owner
  sees who ended it; what runs in tmux carries on), and it is logged.
- **Only the lab's networks**: a machine is only added, and only connected to, when its address is in
  `ALLOWED_NETWORKS` (the HPC subnet; private networks only when unset). Checked against the address the name
  resolves to at that moment, and connected to as checked. The server itself, link-local and cloud-metadata
  addresses are never reached unless listed outright.

## [0.1.1] - 2026-11-15

### Fixed
- **Logins were cut off while the password was typed**: AsyncSSH's connect timeout (20 s) counts the login too,
  so anyone taking longer saw "did not answer" or "Could not reach". The network connection now has 20 s and the
  login 10 minutes.
- **No login to an OpenSSH server without PAM** ("Too many authentication failures", the password never asked):
  keyboard-interactive listed but failed without a question was tried until MaxAuthTries ran out. It is now given up
  for the password.
- **A failed login now says why**: a root login refused by the machine (OpenSSH's PermitRootLogin), or a machine
  turning the server away for a while after failed logins (PerSourcePenalties), instead of an empty reason.

### Changed
- **The login's questions are asked in a box of the page's own**, above the terminal: what is typed or pasted there
  goes to the machine as it is, with the browser's handling of the keyboard (dead keys, accents) and of password
  managers. Typing into the terminal still works.

### Added
- **Audit log** (`docker logs`): who started a session on which machine, each time a browser opens it and from which
  address, each login step (the question asked, never the answer), and how each session ended.
- **A pause after 5 refused logins within 10 minutes**, per member, so passwords cannot be guessed through many
  sessions at once.
- **A browser that loses its session to another is told that browser's address**, so a session taken over
  unexpectedly is noticed.
- Runs read-only, with no capabilities and no privilege escalation, as the suite now starts it.

## [0.1.0] - 2026-11-15

The first release.

### Added
- A terminal in the browser on the lab's HPC machines, over SSH (xterm.js and AsyncSSH).
- Saved connections (a member's user name on one of the lab's machines), opened from a link.
- Login in the terminal: password, and keyboard-interactive questions such as a one-time code. Nothing is
  kept; no private key, no SSH agent. Three wrong answers end the attempt.
- Sessions held by the service, running until their member ends them; reattaching replays the last megabyte
  of output. Optionally in tmux on the machine (the default), which outlives the service.
- The page locks after 5 minutes without a key or the mouse: it lets go of the session, clears the screen and
  signs out of the suite; the server holds to it as well. The session carries on.
- Each session recorded in its member's Lab Notebook when it ends, under today, with the text attached; a
  session running past midnight gets the day just past under that day. Per connection, on by default.
- Save a script on the machine (over SFTP) or the session's text to the notebook by hand, under a day chosen.
- Only machines an administrator adds, each pinned to the host key it was added with; a changed key is
  refused until an administrator reads it again and accepts it.
