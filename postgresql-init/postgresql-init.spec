#
# RPM Spec for PostgreSQL Initializer
#

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
%if 0%{?el7} == 0
echo "This package cannot be built for %{dist}."
false
%endif


%post

# TODO: If any of this fails, the install doesn't.  Find a way around this.

%if 0%{?el7}
#
# EL7
#
PGDATA=$(egrep -e '^Environment=PGDATA=' \
    "%{_sysconfdir}/systemd/system/multi-user.target.wants/%{_pscheduler_postgresql_service}.service" \
    | awk -F= '{ print $3 }')
if [ ! -d "${PGDATA}" ]
then
    echo "Unable to find PGDATA at ${PGDATA}"
    false
fi

# Don't init if it's already initialized
if [ ! -f "${PGDATA}/PG_VERSION" ]
then
    /usr/%{_pscheduler_postgresql_short}/bin/%{_pscheduler_postgresql_service}-setup initdb
fi

# Set up run at boot
systemctl enable %{_pscheduler_postgresql_service}
systemctl start %{_pscheduler_postgresql_service}
%endif


%files
# No files.
