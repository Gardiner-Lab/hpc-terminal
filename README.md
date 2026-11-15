# HPC Terminal

A terminal in the browser on the lab's HPC machines, over SSH, for [Trellis Tools](https://github.com/Gardiner-Lab/Trellis-Tools).
Start long work, close the page, and come back to it from any computer; each session is recorded in the
Lab Notebook.

- **Saved connections**, opened from a link: who you log in as, on which of the lab's machines.
- **Log in in the terminal**: your password, and a one-time code if the machine asks. Never kept; no
  private key is stored and no SSH agent is used.
- **Sessions keep running** with the browser closed, until you end them. Opening the link again, anywhere,
  shows what was printed meanwhile (the last megabyte), then carries on. With tmux (the default) the work
  also outlives a restart of the suite.
- **The page locks after 5 minutes away**: it lets go of the session, clears the screen and signs out, so an
  unattended computer is not a way onto the lab's machines. The session carries on.
- **Recorded in the Lab Notebook**: when a session ends, its transcript is a page under today; a session
  running past midnight gets each day under that day. Scripts on the machine (over SFTP) and the session's
  text can also be saved by hand.
- **Only the lab's machines**: an administrator adds each one, and every connection is checked against the
  host key it was added with. Nothing runs on the suite's server.

## In the suite

It runs as the `terminal` service of Trellis Tools, at `/terminal/`, signed in by the suite's proxy
(`X-Suite-User`). The suite pins a version of it as `TERMINAL_VERSION`.

| Variable | Default | |
| --- | --- | --- |
| `URL_PREFIX` | `/terminal` | where the proxy serves it |
| `TERMINAL_DATA` | `/terminal-data` | its database: machines, host keys, saved connections |
| `MOCLO_DB` | `/moclo/moclo.db` | the suite's account directory, read only: who is an administrator |
| `NOTEBOOK_URL` | `/notebook` | the Lab Notebook, for the browser |
| `NOTEBOOK_INTERNAL` | | the notebook inside the suite's network, for recording sessions |
| `IDLE_MINUTES` | `5` | a page with no activity this long locks (0: never) |
| `KEEP_HOURS` | `0` | close sessions left with no browser this long (0: never) |
| `SESSIONS_PER_MEMBER` | `6` | open sessions each member may have |

| `ALLOWED_NETWORKS` | private networks | the networks it may connect to, comma-separated CIDRs (the HPC subnet) |
| `SUITE_DATABASE_PATH` | `/suite/suite.db` | the suite's labs, read only: who leads which lab, for the overview |

### Limiting where it can connect

`ALLOWED_NETWORKS` is enforced by the terminal: a machine outside it is neither added nor connected to. For a
limit that holds even if the service itself were compromised, also let its container out only to those networks
in the server's firewall. On a Linux server, with Docker's `DOCKER-USER` chain (adjust the subnets):

```sh
TERMINAL_NET=$(docker network inspect gardiner-lab-suite_terminal -f '{{(index .IPAM.Config 0).Subnet}}')
iptables -I DOCKER-USER -s "$TERMINAL_NET" -j DROP
iptables -I DOCKER-USER -s "$TERMINAL_NET" -d 192.168.2.0/24 -p tcp --dport 22 -j ACCEPT
iptables -I DOCKER-USER -s "$TERMINAL_NET" -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
```

In the suite it is on a Docker network of its own, shared only with the proxy and the notebook.

Behind the proxy only: reachable directly, anyone could name themselves in `X-Suite-User`. The proxy's
`/terminal/` block must set that header itself (and the websocket upgrade headers).

## Developing

```sh
pip install -r requirements.txt
pytest -q
```

The tests run a real SSH server (AsyncSSH) and a stand-in notebook, and drive the service through its API
and websocket.

## Licence

GPL-3.0. The terminal is drawn by [xterm.js](https://xtermjs.org) (MIT); SSH is
[AsyncSSH](https://asyncssh.readthedocs.io) (EPL-2.0).
