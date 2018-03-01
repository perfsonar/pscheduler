#
# RPM Spec for pScheduler SNMP Tool
#

%define short	net-snmp-set
Name:		pscheduler-tool-%{short}
Version:	1.0.2.5
Release:	1%{?dist}

Summary:	snmpset tool class for pScheduler
BuildArch:	noarch
License:	Apache 2.0
Group:		Unspecified

Source0:	%{short}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

Requires:	pscheduler-server
Requires:	net-snmp
Requires:	python-pscheduler
Requires:	pscheduler-test-snmpset

BuildRequires:	pscheduler-rpm

%description
snmpset tool class for pScheduler

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
%{dest}
