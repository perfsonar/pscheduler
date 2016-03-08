#
# RPM Spec for PostgreSQL Initializer
#

# PostgreSQL version
%define pg_major 9
%define pg_minor 5

%define pg_point %{pg_major}.%{pg_minor}
%define pg_ver   %{pg_major}%{pg_minor}


Name:		postgresql-init
Version:	%{pg_point}
Release:	1%{?dist}

Summary:	Initializes PostgreSQL
BuildArch:	noarch

License:	Apache 2.0
Group:		Unspecified

# No Source:

Provides:	%{name} = %{version}-%{release}

Requires:	postgresql%{pg_ver}-server


%description
Installing this package initializes the PostgreSQL server, starts it
and makes sure it runs at boot.


%post
PGDATA=$(egrep -e '^PGDATA=' /etc/rc.d/init.d/postgresql-%{pg_point} \
	       | awk -F= '{ print $2 }')

# Don't init if it's already initialized
if [ ! -f "${PGDATA}/PG_VERSION" ]
then
    service postgresql-%{pg_point} initdb
fi

chkconfig postgresql-%{pg_point} on
service postgresql-%{pg_point} start


%postun
service postgresql-%{pg_point} stop
chkconfig postgresql-%{pg_point} off

### # Optional: Remove all data
### PGDATA=$(egrep -e '^PGDATA=' /etc/rc.d/init.d/postgresql-%{pg_point} \
###	       | awk -F= '{ print $2 }')
### %{__rm} -rf ${PGDATA}/*


%files
# No files.
