#
# RPM Spec for pScheduler Tcpping Tool
#

%define short	tcpping
%define perfsonar_auto_version 5.0.0
%define perfsonar_auto_relnum 0.b1.1

Name:		pscheduler-tool-%{short}
Version:	%{perfsonar_auto_version}
Release:	%{perfsonar_auto_relnum}%{?dist}

Summary:	pScheduler Tcpping Tool
BuildArch:	noarch
License:	ASL 2.0
Vendor:	perfSONAR
Group:		Unspecified

Source0:	%{short}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

Requires:	pscheduler-server >= 4.3.0
Requires:	pscheduler-account
Requires:	%{_pscheduler_python}-pscheduler >= 4.3.0
Requires:	pscheduler-test-rtt
Requires:	%{_pscheduler_python}-icmperror
Requires:	tcpping

BuildRequires:	pscheduler-account
BuildRequires:	pscheduler-rpm


%description
pScheduler Tcpping Tool


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
