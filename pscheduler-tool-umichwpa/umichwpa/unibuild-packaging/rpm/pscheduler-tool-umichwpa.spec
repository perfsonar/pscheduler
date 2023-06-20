#
# RPM Spec for pScheduler umichwpa Tool
#

#
# Development Order #1:
#
# This file is significant for buildling the tool into pScheduler.
# If additional libraries or parts of pScheduler are required,
# they should be added here (line 25).
%define short	umichwpa
%define perfsonar_auto_version 5.0.2
%define perfsonar_auto_relnum 1

Name:		pscheduler-tool-%{short}
Version:	%{perfsonar_auto_version}
Release:	%{perfsonar_auto_relnum}%{?dist}

Summary:	umichwpa tool class for pScheduler
BuildArch:	noarch
License:	Apache 2.0
Group:		Unspecified

Source0:	%{short}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

# Include all required libraries here
Requires:	pscheduler-server
Requires:	%{_pscheduler_python}-pscheduler

BuildRequires:	pscheduler-rpm

%description
umichwpa tool class for pScheduler

%prep
%setup -q -n %{short}-%{version}

%define dest %{_pscheduler_tool_libexec}/%{short}

%build
make \
     DESTDIR=$RPM_BUILD_ROOT/%{dest} \
     install

# Enable sudo for layer2 auth

SUPP=$(command -v wpa_supplicant)
CLI=$(command -v wpa_cli)

mkdir -p $RPM_BUILD_ROOT/%{_pscheduler_sudoersdir}
cat > $RPM_BUILD_ROOT/%{_pscheduler_sudoersdir}/%{name} <<EOF

#
# pscheduler-tool-umichwpa
#
Cmnd_Alias PSCHEDULER_WPA_SUPPLICANT = ${SUPP}
%{_pscheduler_user} ALL = (root) NOPASSWD: ${SUPP}
Defaults!PSCHEDULER_WPA_SUPPLICANT !requiretty

Cmnd_Alias PSCHEDULER_WPA_CLI = ${CLI}
%{_pscheduler_user} ALL = (root) NOPASSWD: ${CLI}
Defaults!PSCHEDULER_WPA_CLI !requiretty

%post
pscheduler internal warmboot

%postun
pscheduler internal warmboot

%files
%defattr(-,root,root,-)
%{dest}
