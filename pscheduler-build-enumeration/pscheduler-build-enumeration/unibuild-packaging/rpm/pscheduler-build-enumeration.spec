#
# RPM Spec for pscheduler-build-enumeration
#

%define perfsonar_auto_version 5.3.0
%define perfsonar_auto_relnum 0.a1.0

Name:		pscheduler-build-enumeration
Version:	%{perfsonar_auto_version}
Release:	%{perfsonar_auto_relnum}%{?dist}

Summary:	Build a pScheduler enumeration script from JSON

BuildArch:	noarch
License:	Apache 2.0
Group:		Unspecified
Vendor:		perfSONAR Development Team
URL:		http://www.perfsonar.net

Source0:	%{name}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

Requires:	jq
Requires:	jsonschematool


%description
Build a pScheduler enumeration script from JSON


%prep
%setup -q


%build
make \
     BINDIR=$RPM_BUILD_ROOT/%{_bindir} \
     install


%clean
make clean


%files
%defattr(-,root,root)
%{_bindir}/*
