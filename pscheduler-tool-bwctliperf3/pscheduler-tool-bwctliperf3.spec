#
# RPM Spec for pScheduler BWCTL iperf3 Tool
#

%define short	bwctliperf3
Name:		pscheduler-tool-%{short}
Version:	1.1.2
Release:	1%{?dist}

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
%if 0%{?el6}%{?el7} == 0
echo "This package cannot be built on %{dist}."
false
%endif

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
