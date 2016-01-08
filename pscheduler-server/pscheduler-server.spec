#
# RPM Spec for pScheduler Server
#

Name:		pscheduler-server
Version:	0.0
Release:	1%{?dist}

Summary:	pScheduler Server
BuildArch:	noarch
License:	Apache 2.0
Group:		Unspecified

Source0:	%{name}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

Requires:	postgresql-init
Requires:	postgresql-load
Requires:	python-psycopg2
Requires:	python >= 2.6


%description
The pScheduler server


%prep
%setup -q

%build
make

%install
make \
     INITDDIR=$RPM_BUILD_ROOT/%{_initddir} \
     DATADIR=$RPM_BUILD_ROOT/%{_pscheduler_datadir} \
     BINDIR=$RPM_BUILD_ROOT/%{_bindir} \
     install


%post

# TODO: Drop in pg_hba.conf

# TODO: Remove this once we figure out how to get PostgreSQL not to
# install itself in /usr/local.
export PATH="/usr/local/bin:${PATH}"
PSQL_VERSION=$(psql --version \
		    | awk '{ print $NF }' \
		    | sed -e 's/\.[0-9]\+$//' )
service postgresql-${PSQL_VERSION} reload

# TODO: Load the database

ROLE=$(fgrep 'CREATE ROLE' %{_pscheduler_datadir}/database-build-super.sql \
	     | head -1 \
	     | awk '{ print $3 }')

if [ -z "${ROLE}" ]
then
	echo "Can't find role name in SQL" 1>&2
	exit 1
fi

postgresql-load %{_pscheduler_datadir}/database-build-super.sql
postgresql-load --role "${ROLE}" %{_pscheduler_datadir}/database-build.sql


# TODO: Will eventually need to handle upgrades, but that's a ways off.


%postun
# TODO: Remove pg_hba.conf

# TODO: Remove this once we figure out how to get PostgreSQL not to
# install itself in /usr/local.
export PATH="/usr/local/bin:${PATH}"
PSQL_VERSION=$(psql --version \
		    | awk '{ print $NF }' \
		    | sed -e 's/\.[0-9]\+$//' )
service postgresql-${PSQL_VERSION} reload


%files
%defattr(-,root,root,-)
%{_initddir}/*
%{_pscheduler_datadir}/*
%{_bindir}/*
