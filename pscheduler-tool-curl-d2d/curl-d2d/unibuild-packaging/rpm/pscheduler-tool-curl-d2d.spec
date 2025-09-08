#
# RPM Spec for pScheduler curl Tool
#

#
# Development Order #1:
#
# This file is significant for buildling the tool into pScheduler.
# If additional libraries or parts of pScheduler are required,
# they should be added here (line 25).
%define short	curl-d2d
%define perfsonar_auto_version 5.2.2
%define perfsonar_auto_relnum 1

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
Requires:	pscheduler-server >= 4.3.0
Requires:	pscheduler-test-http
Requires:	pscheduler-test-disk-to-disk
Requires:	%{_pscheduler_python}-pscheduler >= 4.3.0
Requires:	%{_pscheduler_python}-pycurl
Requires:	rpm-post-wrapper

BuildRequires:	pscheduler-rpm

%description
curl tool class for pScheduler

%prep
%setup -q -n %{short}-%{version}

%define dest %{_pscheduler_tool_libexec}/%{short}

%build
make \
     DESTDIR=$RPM_BUILD_ROOT/%{dest} \
     PYTHON=%{_pscheduler_python} \
     install

%post
rpm-post-wrapper '%{name}' "$@" <<'POST-WRAPPER-EOF'
pscheduler internal warmboot
POST-WRAPPER-EOF

%postun
pscheduler internal warmboot

%files
%defattr(-,root,root,-)
%{dest}
