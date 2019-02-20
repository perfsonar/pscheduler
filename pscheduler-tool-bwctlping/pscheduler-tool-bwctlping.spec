#
# RPM Spec for pScheduler BWCTL Ping Tool
#

%define short	bwctlping
Name:		pscheduler-tool-%{short}
Version:	1.1.6
Release:	1%{?dist}

Summary:	pScheduler BWCTL Ping Tool
BuildArch:	noarch
License:	ASL 2.0
Vendor:	perfSONAR
Group:		Unspecified

Source0:	%{short}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

Requires:	pscheduler-server
Requires:	pscheduler-account
Requires:	python-ipaddr
Requires:	python-pscheduler >= 1.3
Requires:	pscheduler-test-rtt
Requires:	python-icmperror
# This supplies ping.
Requires:	iputils
Requires:	bwctl-client
Requires:	bwctl-server

BuildRequires:	pscheduler-account
BuildRequires:	pscheduler-rpm
BuildRequires:	iputils


%description
pScheduler Ping Tool


%prep
%setup -q -n %{short}-%{version}


%define dest %{_pscheduler_tool_libexec}/%{short}

%install
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
