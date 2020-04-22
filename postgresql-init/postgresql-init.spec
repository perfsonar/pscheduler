#
# RPM Spec for PostgreSQL Initializer
#

Name:		postgresql-init
Version:	%{_pscheduler_postgresql_version}
Release:	1%{?dist}

Summary:	Initializes and upgrades PostgreSQL
BuildArch:	noarch

License:	Apache 2.0
Group:		Unspecified

Source:		%{name}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}
Provides:	pscheduler-database-init

Requires:	%{_pscheduler_postgresql_package}-server

BuildRequires:	pscheduler-rpm

# Older versions.  Note that perfSONAR only ever shipped with 9.5;
# everything else is for completeness.

Obsoletes:	postgresql95
Obsoletes:	postgresql95-contrib
Obsoletes:	postgresql95-devel
Obsoletes:	postgresql95-libs
Obsoletes:	postgresql95-plpython
Obsoletes:	postgresql95-server

Obsoletes:	postgresql96
Obsoletes:	postgresql96-contrib
Obsoletes:	postgresql96-devel
Obsoletes:	postgresql96-libs
Obsoletes:	postgresql96-plpython
Obsoletes:	postgresql96-server

Obsoletes:	postgresql10
Obsoletes:	postgresql10-contrib
Obsoletes:	postgresql10-devel
Obsoletes:	postgresql10-libs
Obsoletes:	postgresql10-plpython
Obsoletes:	postgresql10-server

Obsoletes:	postgresql11
Obsoletes:	postgresql11-contrib
Obsoletes:	postgresql11-devel
Obsoletes:	postgresql11-libs
Obsoletes:	postgresql11-plpython
Obsoletes:	postgresql11-server



%description
Installing this package initializes the PostgreSQL server, upgrades
(and removes) any previous versions, starts it and makes sure it runs
at boot.


%define libexec %{_libexecdir}/%{name}


%prep
%if 0%{?el7} == 0
echo "This package cannot be built for %{dist}."
false
%endif

%setup -q


%build
make \
    PG_LIB="%{_pscheduler_postgresql_data_top}" \
    PG_USER="%{_pscheduler_postgresql_user}" \
    USR="%{_usr}" \
    DESTDIR="${RPM_BUILD_ROOT}/%{libexec}" \
    install



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


%posttrans
echo EWWWW
false


%files
%{libexec}
