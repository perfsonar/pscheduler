changequote(<<<,>>>)dnl
changecom()dnl
#
# Systemd unit for __PROG__
#
# Systemd version __SYSTEMD_VERSION__ was installed at build time.
#
# 
#   Version of systemd installed by distros we support:
# 
#     EL7 229
#     EL8 239
#     EL9 252
#     D10 241
#     D11 247
#     D12 252
#     U20 245
#     U22 249

[Unit]
Description=pScheduler Server - __PROG__
# This forces starting and stopping in concert
PartOf=__PGSERVICE__
After=__PGSERVICE__
Wants=__PGSERVICE__

[Service]
# Systemd 240 added exec, which is better.
Type=ifelse(eval(__SYSTEMD_VERSION__ <  240),1,simple,exec)

User=__PSUSER__
Group=__PSUSER__

PermissionsStartOnly=true
LimitNOFILE=32768
LimitNPROC=32768

Restart=always
RestartSec=15

# This is slightly longer than the database check below so failures
# will be more apparent than just a timeout.
TimeoutStartSec=130

# Wait for the database to become accessible.  This is done because
# the PostgreSQL service can appear up when it isn't ready to take
# queries yet.  That will cause this service to die.
ExecStartPre=__DAEMONDIR__/wait-for-database --dsn @__DSN__ --dwell 120 --retry 5

# Create the run directory
ExecStartPre=/bin/mkdir -p __RUNDIR__/__PROG__
ExecStartPre=/bin/chmod 755 __RUNDIR__/__PROG__

# Set up some temporary space and export its location
ExecStartPre=/bin/mkdir -p __RUNDIR__/__PROG__/tmp
ExecStartPre=/bin/chmod 700 __RUNDIR__/__PROG__/tmp
Environment=TMPDIR=__RUNDIR__/__PROG__/tmp

# Set ownership
ExecStartPre=/bin/chown -R __PSUSER__:__PSUSER__ __RUNDIR__/__PROG__

# Generate options file
ExecStartPre=/bin/sh -c "if [ -r __CONFIGDIR__/__PROG__.conf ]; then opts=$(sed -e 's/#.*$//' __CONFIGDIR__/__PROG__.conf); echo OPTIONS=$opts > __RUNDIR__/__PROG__/options; chown __PSUSER__:__PSUSER__ __RUNDIR__/__PROG__/options; fi"

# Redirections
StandardOutput=journal
StandardError=journal

# Start service
EnvironmentFile=-__RUNDIR__/__PROG__/options
ExecStart=__DAEMONDIR__/__PROG__ --dsn @__DSN__ $OPTIONS

# Stop service
ExecStopPost=/bin/rm -rf __RUNDIR__/__PROG__

[Install]
WantedBy=multi-user.target
