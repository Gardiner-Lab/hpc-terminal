# Changelog

Releases of the HPC Terminal. The [Trellis Tools](https://github.com/Gardiner-Lab/Trellis-Tools) suite pins
a version of it as `TERMINAL_VERSION`, so a release here changes no installation until the suite is updated
to use it.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the project uses [semantic versioning](https://semver.org/).

## [Unreleased]

### Fixed
- **No login to an OpenSSH server without PAM** ("Too many authentication failures", the password never asked):
  such a server lists keyboard-interactive but fails it at once without a question, and the terminal tried it
  again until the server's MaxAuthTries ran out. A keyboard-interactive attempt that asks nothing is now not
  tried again, and the password is asked.

### Added
- Each session's end in the service's log (`docker logs lab-terminal`): whose, where, before or after login, and why.

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
