#
# RPM Spec for pScheduler BWCTL Ping Tool
#

%define short	bwctlping
Name:		pscheduler-tool-%{short}
Version:	1.1.5
Release:	1%{?dist}

Summary:	pScheduler BWCTL Ping Tool (DISABLED)
BuildArch:	noarch
License:	ASL 2.0
Vendor:	perfSONAR
Group:		Unspecified

Source0:	%{short}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

Requires:	pscheduler-server
Requires:	pscheduler-account
Requires:	pscheduler-test-rtt

BuildRequires:	pscheduler-account
BuildRequires:	pscheduler-rpm


%description
pScheduler Ping Tool (DISABLED)


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
