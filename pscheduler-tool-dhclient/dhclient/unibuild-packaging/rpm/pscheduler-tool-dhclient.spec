#
# RPM Spec for pScheduler dhclient Tool
#

#
# Development Order #1:
#
# This file is significant for buildling the tool into pScheduler.
# If additional libraries or parts of pScheduler are required,
# they should be added here (line 25).
%define short	dhclient
%define perfsonar_auto_version 5.0.0
%define perfsonar_auto_relnum 0.a1.0

Name:		pscheduler-tool-%{short}
Version:	%{perfsonar_auto_version}
Release:	%{perfsonar_auto_relnum}%{?dist}

Summary:	dhclient tool class for pScheduler
BuildArch:	noarch
License:	Apache 2.0
Group:		Unspecified

Source0:	%{short}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

# Include all required libraries here
Requires:	pscheduler-server
Requires:	%{_pscheduler_python}-pscheduler
%if 0%{?el7}
Requires:	dhclient
%endif
%if 0%{?el8}
Requires:	dhcp-client
# Needed so the sudoers file can be built
BuildRequires:	dhcp-client
%endif

BuildRequires:	pscheduler-rpm

%description
dhclient tool class for pScheduler

%prep
%setup -q -n %{short}-%{version}

%define dest %{_pscheduler_tool_libexec}/%{short}

%install

make \
     DESTDIR=$RPM_BUILD_ROOT/%{dest} \
     PYTHON=%{_pscheduler_python} \
     install

# Enable sudo for dhclient

DHCLIENT=$(which dhclient)

mkdir -p $RPM_BUILD_ROOT/%{_pscheduler_sudoersdir}
cat > $RPM_BUILD_ROOT/%{_pscheduler_sudoersdir}/%{name} <<EOF
#
# %{name}
#
Cmnd_Alias PSCHEDULER_TOOL_DHCLIENT = ${DHCLIENT}
%{_pscheduler_user} ALL = (root) NOPASSWD: ${DHCLIENT}
Defaults!PSCHEDULER_TOOL_DHCLIENT !requiretty
EOF

%post
pscheduler internal warmboot

%postun
pscheduler internal warmboot

%files
%defattr(-,root,root,-)
%{dest}
%attr(440,root,root) %{_pscheduler_sudoersdir}/*
