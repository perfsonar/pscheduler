#
# RPM Spec for PostgreSQL Initializer
#

Name:		postgresql-init

# Note that the dot after this is for versions of this package rather
# than the Pg relese.
Version:	%{_pscheduler_postgresql_version}.1
Release:	1%{?dist}

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

#TODO Remove if updates are made to future  postgres version that
#     create the following directory during initalization
#
#Check for directory and if not create it and set permissions

if [ ! -d "/var/run/postgresql/" ]; then
    echo "/var/run/postgresql/ does not exist. Creating it..."
    mkdir -p "/var/run/postgresql/"
    chown postgres:postgres "/var/run/postgresql/"
else
    echo "/var/run/postgresql/ already exists."
fi


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
