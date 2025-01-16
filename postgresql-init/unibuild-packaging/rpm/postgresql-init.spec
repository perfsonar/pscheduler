#
# RPM Spec for PostgreSQL Initializer
#

Name:		postgresql-init

# Note that the dot after this is for versions of this package rather
# than the Pg relese.
Version:	%{_pscheduler_postgresql_version}.1
Release:	4%{?dist}

Summary:	Initializes PostgreSQL
BuildArch:	noarch

License:	Apache 2.0
Group:		Unspecified

# No source file.
# Source:		%{name}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

# TODO: This isn't harmful but can probably go.

# NOTE: This is something of a hack because it forces installation of
# all packages that are likely to be used.  It's necessary because
# pg_upgrade will refuse to work if required libraries are absent.

Requires:	postgresql >= %{_pscheduler_postgresql_version}
Requires:	postgresql-contrib >= %{_pscheduler_postgresql_version}
Requires:	postgresql-devel >= %{_pscheduler_postgresql_version}
Requires:	postgresql-libs >= %{_pscheduler_postgresql_version}
Requires:	postgresql-plpython3 >= %{_pscheduler_postgresql_version}
Requires:	postgresql-server  >= %{_pscheduler_postgresql_version}
Requires:	rpm-post-wrapper

Requires:       pscheduler-rpm
Requires:       selinux-policy-devel

BuildRequires:	pscheduler-rpm



%description
Installing this package initializes the PostgreSQL server, starts it
and makes sure it runs at boot.


%define pg_version_file %{_pscheduler_postgresql_data}/PG_VERSION


# No prep or build.


%post
rpm-post-wrapper '%{name}' "$@" <<'POST-WRAPPER-EOF'

# Note that if any of this fails, the install doesn't.  This is an
# problem inherent in RPM that the developers won't fix.

set -e

if [ -e "%{pg_version_file}" ]
then
    echo "PostgreSQL is already initialized.  Doing nothing."
    systemctl enable --now postgresql
    exit 0
fi

# BEGIN PSQL FIXES

# Red Hat changed the way PostgreSQL was packaged between 13.16 and
# 13.18.  Creating /run/postgresql was passed off to systemd-tmpfiles,
# which expects a reboot before it does its thing.  This means the @
# system needs to be rebooted for PostgreSQL to function, which isn't
# acceptable here because builds require a functioning database.

# Fix 1: Create run directory and set permissions

if [ ! -d "%{_rundir}/postgresql/" ]; then
    echo "%{_rundir}/postgresql/ does not exist. Creating it..."
    mkdir -p "%{_rundir}/postgresql/"
    chown -R postgres:postgres "%{_rundir}/postgresql/"
    chmod -R 755  "%{_rundir}/postgresql/"
fi

# Fix 2: Install SELinux policy to allow PostgreSQL to set up its
#        socket.

WORK=$(mktemp -d)

cleanup()
{
    rm -rf "${WORK}"
}
trap cleanup EXIT

TE="${WORK}/psql.te"

rm -f "${TE}"
cat > "${TE}" << TE_EOF
module psql 1.0;

require {
    type postgresql_t;    # PostgreSQL process type
    type var_run_t;       # PostgreSQL database files type
    class sock_file read;
    class sock_file write;
    class sock_file create;
    class sock_file open;
    class sock_file getattr;
    class sock_file setattr;
    class sock_file unlink;
    class sock_file append;
    class sock_file rename;
}

allow postgresql_t var_run_t:sock_file { read write create open getattr setattr unlink append rename };

TE_EOF

make -f /usr/share/selinux/devel/Makefile -C "${WORK}" psql.pp
semodule -i "${WORK}/psql.pp"

# END PSQL FIXES



# Initialize PostgreSQL

systemctl stop postgresql

echo 'Initializing PostgreSQL.'
postgresql-setup --initdb

systemctl start postgresql

# Set up run at boot
systemctl enable postgresql
POST-WRAPPER-EOF


%files
# No files.
