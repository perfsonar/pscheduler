#
# RPM Spec for pScheduler BWCTL iperf3 Tool
#

%define short	bwctliperf3
%define perfsonar_auto_version 4.3.0
%define perfsonar_auto_relnum 0.a0.0

Name:		pscheduler-tool-%{short}
Version:	%{perfsonar_auto_version}
Release:	%{perfsonar_auto_relnum}%{?dist}

Summary:	BWCTL iperf3 tool class for pScheduler (DISABLED)
BuildArch:	noarch
License:	ASL 2.0
Vendor:	perfSONAR
Group:		Unspecified

Source0:	%{short}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

Requires:	pscheduler-server
Requires:	pscheduler-test-throughput

BuildRequires:	pscheduler-rpm


%description
BWCTL iperf3 tool class for pScheduler (DISABLED)


%prep
%setup -q -n %{short}-%{version}


%define dest %{_pscheduler_tool_libexec}/%{short}

%build
make \
     DESTDIR=$RPM_BUILD_ROOT/%{dest} \
     install

%post
pscheduler internal warmboot


%postun
pscheduler internal warmboot


%files
%defattr(-,root,root,-)
%license LICENSE
%{dest}
