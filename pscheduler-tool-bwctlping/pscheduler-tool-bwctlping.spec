#
# RPM Spec for pScheduler BWCTL Ping Tool
#

%define short	bwctlping
%define perfsonar_auto_version 4.4.0
%define perfsonar_auto_relnum 0.3.b1

Name:		pscheduler-tool-%{short}
Version:	%{perfsonar_auto_version}
Release:	%{perfsonar_auto_relnum}%{?dist}

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
