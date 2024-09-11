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
%define perfsonar_auto_version 5.1.4
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
Requires:	rpm-post-wrapper

# TODO: Why is there a discrepancy between dhcp-client and dhclient here?

# Needed so the sudoers file can be built
BuildRequires:	dhcp-client

BuildRequires:	pscheduler-rpm
BuildRequires: dhclient

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

DHCLIENT=$(command -v dhclient)

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
rpm-post-wrapper '%{name}' "$@" <<'POST-WRAPPER-EOF'
pscheduler internal warmboot
POST-WRAPPER-EOF

%postun
pscheduler internal warmboot

%files
%defattr(-,root,root,-)
%{dest}
%attr(440,root,root) %{_pscheduler_sudoersdir}/*
