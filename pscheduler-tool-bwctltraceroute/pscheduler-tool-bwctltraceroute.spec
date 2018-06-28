#
# RPM Spec for pScheduler BWCTL Traceroute Tool
#

%define short	bwctltraceroute
Name:		pscheduler-tool-%{short}
Version:	1.1
Release:	0.2.b1%{?dist}

Summary:	pScheduler BWCTL Traceroute Tool
BuildArch:	noarch
License:	ASL 2.0
Vendor:	perfSONAR
Group:		Unspecified

Source0:	%{short}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

Requires:	pscheduler-server
Requires:	pscheduler-account
Requires:	python-pscheduler >= 1.3
Requires:	pscheduler-test-trace
Requires:	python-icmperror
Requires:	bwctl-client
Requires:	bwctl-server
Requires:   traceroute

BuildRequires:	pscheduler-account
BuildRequires:	pscheduler-rpm

%description
pScheduler BWCTL Traceroute Tool


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
