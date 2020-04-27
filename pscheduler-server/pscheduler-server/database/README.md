# Notes on the pScheduler Database

## Table Creation and Maintenance

See [README-tables](README-tables) for important information on how
tables in this database are created and maintained.  It is important
that this be read and understood _before_ undertaking any
modifications.


## PostgreSQL Support Plans

This database was originally developed for PostgreSQL 9.5.

| Pg Release | OS | OS EOL | Pg Version | Pg EOL |
| 9.5 | CentOS 7 | 2024-06-30  | 9.5.3 | 2021-02-11 |
| 9.6 | Debian 9 (Stretch) | 2020-??-?? | 9.6.x | 2021-11-11 |
| 10  | CentOS 8 | 2029-05-31 |10.6 | 2022-11-10 |
| 11  | Debian 10 (Buster) | 2022-??-?? | 11.7 | 2023-11-09 |

**NOTE:** CentOS 7 provides 9.2.x; 9.5.3 is provided by the perfSONAR
repo.

perfSONAR 4.3 should be the last release with support for 9.x.


References:

 * https://www.postgresql.org/support/versioning/
 * https://wiki.centos.org/About/Product
 * https://wiki.debian.org/DebianReleases
