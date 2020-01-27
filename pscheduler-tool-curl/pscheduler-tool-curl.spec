#
# RPM Spec for pScheduler curl Tool
#

#
# Development Order #1:
#
# This file is significant for buildling the tool into pScheduler.
# If additional libraries or parts of pScheduler are required,
# they should be added here (line 25).
%define short	curl
%define perfsonar_auto_version 4.3.0
%define perfsonar_auto_relnum 0.a0.0

Name:		pscheduler-tool-%{short}
Version:	%{perfsonar_auto_version}
Release:	%{perfsonar_auto_relnum}%{?dist}

Summary:	curl tool class for pScheduler
BuildArch:	noarch
License:	Apache 2.0
Group:		Unspecified

Source0:	%{short}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

# Include all required libraries here
Requires:	pscheduler-server
Requires:	pscheduler-test-http
Requires:	pscheduler-test-disk-to-disk
Requires:	%{_pscheduler_python}-pscheduler

BuildRequires:	pscheduler-rpm

%description
curl tool class for pScheduler

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
