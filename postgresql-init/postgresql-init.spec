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
#As of 4.3 we can probably get rid of below, but keep around until 4.4 to handle strange upgrade paths.
Provides:	pscheduler-database-init


# NOTE: This is something of a hack because it forces installation of
# all packages that are likely to be used.  It's necessary because
# pg_upgrade will refuse to work if required libraries are absent.

Requires:	%{_pscheduler_postgresql_package}
Requires:	%{_pscheduler_postgresql_package}-contrib
Requires:	%{_pscheduler_postgresql_package}-devel
Requires:	%{_pscheduler_postgresql_package}-libs
# This is required only for an upgrade to succeed.  Post-Python2 code
# doesn't use it.
# TODO: Remove this after 4.3.x reaches EOL.
Requires:	%{_pscheduler_postgresql_package}-plpython
Requires:	%{_pscheduler_postgresql_package}-plpython3
Requires:	%{_pscheduler_postgresql_package}-server


BuildRequires:	pscheduler-rpm


# NOTE: It would be nice if this version could obsolete older packages
# so they're uninstalled.  There's a conflict with packages that
# haven't been upgraded yet and still depend on the old one, so the
# best thing that can be done is disabling the older one and enabling
# the newer one.



%description
Installing this package initializes the PostgreSQL server, upgrades
the data from and disables any previous versions, starts it and makes
sure it runs at boot.


%define libexec %{_libexecdir}/%{name}

%prep
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

set -e

# Try an upgrade first
%{libexec}/upgrade-postgresql
%{libexec}/initialize-postgresql

# Set up run at boot
systemctl enable --now %{_pscheduler_postgresql_service}


%files
%{libexec}
