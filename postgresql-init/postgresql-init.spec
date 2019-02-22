#
# RPM Spec for PostgreSQL Initializer
#

# PostgreSQL version
# TODO: Make the scripts figure this out.
%define pg_major 9
%define pg_minor 5

%define pg_point %{pg_major}.%{pg_minor}
%define pg_ver   %{pg_major}%{pg_minor}


Name:		postgresql-init
Version:	%{_pscheduler_postgresql_version}
Release:	1%{?dist}

Summary:	Initializes PostgreSQL
BuildArch:	noarch

License:	Apache 2.0
Group:		Unspecified

# No Source:

Provides:	%{name} = %{version}-%{release}
Provides:	pscheduler-database-init

Requires:	%{_pscheduler_postgresql_package}-server

BuildRequires:	pscheduler-rpm



%description
Installing this package initializes the PostgreSQL server, starts it
and makes sure it runs at boot.


%prep
%if 0%{?el6}%{?el7} == 0
echo "This package cannot be built for %{dist}."
false
%endif


%post

# TODO: If any of this fails, the install doesn't.  Find a way around this.

%if 0%{?el6}
#
# EL6
#
PGDATA=$(egrep -e '^PGDATA=' %{_sysconfdir}/rc.d/init.d/postgresql-%{pg_point} \
    | awk -F= '{ print $2 }')
if [ ! -d "${PGDATA}" ]
then
    echo "Unable to find PGDATA at ${PGDATA}"
    false
fi

# Don't init if it's already initialized
if [ ! -f "${PGDATA}/PG_VERSION" ]
then
    service postgresql-%{pg_point} initdb
fi

# Set up run at boot
chkconfig postgresql-%{pg_point} on
service postgresql-%{pg_point} start
%endif

%if 0%{?el7}
#
# EL7
#
PGDATA=$(egrep -e '^Environment=PGDATA=' \
    "%{_sysconfdir}/systemd/system/multi-user.target.wants/postgresql-%{pg_point}.service" \
    | awk -F= '{ print $3 }')
if [ ! -d "${PGDATA}" ]
then
    echo "Unable to find PGDATA at ${PGDATA}"
    false
fi

# Don't init if it's already initialized
if [ ! -f "${PGDATA}/PG_VERSION" ]
then
    /usr/pgsql-%{pg_point}/bin/postgresql%{pg_major}%{pg_minor}-setup initdb
fi

# Set up run at boot
systemctl enable postgresql-%{pg_point}
systemctl start postgresql-%{pg_point}
%endif


%files
# No files.
