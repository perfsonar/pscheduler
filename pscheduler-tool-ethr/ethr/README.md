# Ethr Plugin Notes

The current version of this plugin supports the use of Ethr 1.x and
Ethr 0.x for backward compatibility.

Debian 10 and Ubuntu 20 cannot build Ethr 1.x and do not install it,
so this plugin will detect its absence and behave as if it's an Ethr
0.x-only system.

**At a minimum**, any distrbution including this plugin **must** have
the `ethr0` package built and installed.  That package installs its
binary as `eth0` to avoid colliding with Ethr 1.x's `ethr` binary.
