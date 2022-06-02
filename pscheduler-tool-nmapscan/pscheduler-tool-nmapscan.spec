#
# RPM Spec for pScheduler nmapscan Tool
#

#
# Development Order #1:
#
# This file is significant for buildling the tool into pScheduler.
# If additional libraries or parts of pScheduler are required,
# they should be added here (line 25).
%define short	nmapscan
%define perfsonar_auto_version 5.0.0
%define perfsonar_auto_relnum 0.b1.1

Name:		pscheduler-tool-%{short}
Version:	%{perfsonar_auto_version}
Release:	%{perfsonar_auto_relnum}%{?dist}

Summary:	nmapscan tool class for pScheduler
BuildArch:	noarch
License:	Apache 2.0
Group:		Unspecified

Source0:	%{short}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

# Include all required libraries here
Requires:	pscheduler-server
Requires:	%{_pscheduler_python}-pscheduler
Requires:	%{_pscheduler_python}-nmap3

BuildRequires:	pscheduler-rpm

%description
nmapscan tool class for pScheduler

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
