#
# RPM Spec for postgresql-load
#

Name:		postgresql-load
Version:	1.0
Release:	1%{?dist}

Summary:	Run a SQL file through PostgreSQL

BuildArch:	noarch
License:	Apache 2.0
Group:		Unspecified
Vendor:		perfSONAR Development Team
URL:		http://www.perfsonar.net

Source0:	%{name}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

Requires:	postgresql

%description
This program is used to run SQL files through psql with an option to
run them under an account guaranteed to have superuser rights.


%prep
%setup -q


%build
make \
     BINDIR=$RPM_BUILD_ROOT/%{_bindir} \
     MANDIR=$RPM_BUILD_ROOT/%{_mandir} \
     install


%clean
make clean


%files
%defattr(-,root,root)
%{_bindir}/*
%{_mandir}/man1/*
