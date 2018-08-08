#
# RPM Spec for pScheduler nuttcp Tool
#

%define short	nuttcp
Name:		pscheduler-tool-%{short}
Version:	1.1
Release:	0.3.b1%{?dist}

Summary:	nuttcp tool class for pScheduler
BuildArch:	noarch
License:	ASL 2.0
Vendor:	perfSONAR
Group:		Unspecified

Source0:	%{short}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

Requires:	pscheduler-server
Requires:	python-pscheduler
Requires:	pscheduler-test-throughput
Requires:	nuttcp >= 8.1.4

BuildRequires:	pscheduler-rpm


%description
nuttcp tool class for pScheduler


%prep
%if 0%{?el6}%{?el7} == 0
echo "This package cannot be built on %{dist}."
false
%endif

%setup -q -n %{short}-%{version}


%define dest %{_pscheduler_tool_libexec}/%{short}

%build
make \
     DESTDIR=$RPM_BUILD_ROOT/%{dest} \
     CONFDIR=$RPM_BUILD_ROOT/%{_pscheduler_tool_confdir}\
     install

%post
pscheduler internal warmboot


%postun
pscheduler internal warmboot


%files
%defattr(-,root,root,-)
%license LICENSE
%config(noreplace) %{_pscheduler_tool_confdir}/*
%{dest}
