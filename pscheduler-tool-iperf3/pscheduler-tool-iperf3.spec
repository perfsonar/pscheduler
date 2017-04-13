#
# RPM Spec for pScheduler iperf3 Tool
#

%define short	iperf3
Name:		pscheduler-tool-%{short}
Version:	1.0
Release:	1%{?dist}

Summary:	iperf3 tool class for pScheduler
BuildArch:	noarch
License:	Apache 2.0
Group:		Unspecified

Source0:	%{short}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

Requires:	pscheduler-server
Requires:	python-pscheduler
Requires:	pscheduler-test-throughput
requires:	iperf3

BuildRequires:	pscheduler-rpm


%description
iperf3 tool class for pScheduler


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
%config(noreplace) %{_pscheduler_tool_confdir}/*
%{dest}
