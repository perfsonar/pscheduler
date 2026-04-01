#
# RPM Spec for pScheduler Plugin Makefiles
#

%define perfsonar_auto_version 5.3.0
%define perfsonar_auto_relnum 0.a1.0

Name:		pscheduler-plugin-makefiles
Version:	%{perfsonar_auto_version}
Release:	%{perfsonar_auto_relnum}%{?dist}

Summary:	Makefile templates for pScheduler plugins

BuildArch:	noarch
License:	Apache 2.0
Group:		Unspecified
Vendor:		perfSONAR Development Team
URL:		http://www.perfsonar.net

Source0:	%{name}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

Requires:	make
Requires:	pscheduler-build-enumeration

BuildRequires:	pscheduler-rpm

%description
Makefile templates for pScheduler plugins


%prep
%setup -q


%build
make \
     DESTDIR=$RPM_BUILD_ROOT/%{_pscheduler_includedir} \
     install


%clean
make clean


%files
%defattr(-,root,root)
%{_pscheduler_includedir}/*
