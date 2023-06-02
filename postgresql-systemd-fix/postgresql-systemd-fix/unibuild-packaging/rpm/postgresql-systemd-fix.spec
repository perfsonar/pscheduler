#
# RPM Spec for postgresql-systemd-fix
#

Name:		postgresql-systemd-fix
Version:	1.0
Release:	1%{?dist}

Summary:	Fix a problem with PostgreSQL stopping on EL8

BuildArch:	noarch
License:	Apache 2.0
Group:		Unspecified
Vendor:		perfSONAR Development Team
URL:		http://www.perfsonar.net

Source0:	%{name}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

Requires:	postgresql-server

%description
This packages fixes a problem with stopping PostgreSQL on EL8 systems
under systemd.  See
https://github.com/perfsonar/pscheduler/issues/1335 for details.


%post
sed -i -e 's/^TimeoutSec=.*$/TimeoutSec=10/' /usr/lib/systemd/system/postgresql.service
systemctl daemon-reload

%files
