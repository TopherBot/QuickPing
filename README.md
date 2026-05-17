# QuickPing

**QuickPing** is a minimal command‑line tool written in Python that pings a host and reports the average round‑trip time.

## Installation

```bash
# Clone the repo (or copy the files)
git clone <repo-url>
cd QuickPing
```

*Python 3.7+ is required.*

## Usage

```bash
python ping.py example.com
```

You can also specify a custom count of echo requests:

```bash
python ping.py example.com 5
```

## How it works

The script creates raw ICMP echo requests using the `socket` module (requires admin/root privileges on most systems) and computes the average latency over the requested number of pings.

## License

MIT – see `LICENSE` if added later.
