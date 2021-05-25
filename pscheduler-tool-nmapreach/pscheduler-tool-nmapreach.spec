#
# RPM Spec for pScheduler nmapreach Tool
#

%define short	nmapreach
%define perfsonar_auto_version 4.4.0
%define perfsonar_auto_relnum 0.3.b1

Name:		pscheduler-tool-%{short}
Version:	%{perfsonar_auto_version}
Release:	%{perfsonar_auto_relnum}%{?dist}

Summary:	DNS tool class for pScheduler
BuildArch:	noarch
License:	ASL 2.0
Vendor:		perfSONAR
Group:		Unspecified

Source0:	%{short}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

Requires:	pscheduler-server >= 4.3.0
Requires:	%{_pscheduler_python}-pscheduler >= 4.3.0
Requires:	pscheduler-test-netreach
Requires:	nmap

BuildRequires:	pscheduler-rpm


%description
Network reachability tool for pScheduler


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

