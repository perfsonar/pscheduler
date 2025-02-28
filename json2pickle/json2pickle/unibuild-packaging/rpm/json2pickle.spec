#
# RPM Spec for json2pickle
#

Name:		json2pickle
Version:	1.0
Release:	1%{?dist}

Summary:	Tools for converting between Python-pickled data and JSON

BuildArch:	noarch
License:	Apache 2.0
Group:		Unspecified
Vendor:		perfSONAR Development Team
URL:		http://www.perfsonar.net

Source0:	%{name}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

Requires:	postgresql-server
Requires:	procps-ng

BuildRequires:	pscheduler-rpm

%description
This package contains json2pickle and pickle2json, which
convert between JSON and Python-pickled data.


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
