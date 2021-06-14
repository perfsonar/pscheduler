#
# RPM Spec for pScheduler Syslog http
#

%define short	snmptrap
%define perfsonar_auto_version 4.4.0
%define perfsonar_auto_relnum 0.10.b1

Name:		pscheduler-archiver-%{short}
Version:	%{perfsonar_auto_version}
Release:	%{perfsonar_auto_relnum}%{?dist}

Summary:	snmptrap archiver class for pScheduler
BuildArch:	noarch
License:	ASL 2.0
Vendor:	perfSONAR
Group:		Unspecified

Source0:	%{short}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

Requires:	pscheduler-server
Requires:	%{_pscheduler_python}-pscheduler
Requires:	%{_pscheduler_python}-pysnmp

BuildRequires:	pscheduler-rpm


%define directory %{_includedir}/make

%description
This archiver sends SNMP traps to a specified destination/agent.


%prep
%setup -q -n %{short}-%{version}


%define dest %{_pscheduler_archiver_libexec}/%{short}

%build
make \
     DESTDIR=$RPM_BUILD_ROOT/%{dest} \
     DOCDIR=$RPM_BUILD_ROOT/%{_pscheduler_archiver_doc} \
     install

%post
pscheduler internal warmboot

%postun
pscheduler internal warmboot

%files
%defattr(-,root,root,-)
%license LICENSE
%{dest}
%{_pscheduler_archiver_doc}/*
