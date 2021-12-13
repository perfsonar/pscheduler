#
# RPM Spec for pScheduler mtu Test
#

#
# Development Order #1:
#
# This file is significant for building the test into pScheduler.
# If additional libraries or parts of pScheduler are required,
# they should be added here after line 25.
#

%define short	mtu
%define perfsonar_auto_version 5.0.0
%define perfsonar_auto_relnum 0.a1.0

Name:		pscheduler-test-%{short}
Version:	%{perfsonar_auto_version}
Release:	%{perfsonar_auto_relnum}%{?dist}

Summary:	MTU test for pScheduler
BuildArch:	noarch
License:	Apache 2.0
Group:		Unspecified

Source0:	%{short}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

# Include all required libraries here
Requires:	pscheduler-server
Requires:	%{_pscheduler_python}-pscheduler >= 1.3
Requires:	%{_pscheduler_python}-jsontemplate

BuildRequires:	pscheduler-rpm


%description
MTU test class for pScheduler


%prep
%setup -q -n %{short}-%{version}


%define dest %{_pscheduler_test_libexec}/%{short}

%build
make \
     PYTHON=%{_pscheduler_python} \
     DESTDIR=$RPM_BUILD_ROOT/%{dest} \
     install



%post
pscheduler internal warmboot


%postun
pscheduler internal warmboot


%files
%defattr(-,root,root,-)
%{dest}
