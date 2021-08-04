#
# RPM Spec for pScheduler wpa-supplicant Tool
#

%define short	wpa-supplicant
%define perfsonar_auto_version 4.4.0
%define perfsonar_auto_relnum  0.a1.0

Name:		pscheduler-tool-%{short}
Version:	%{perfsonar_auto_version}
Release:	%{perfsonar_auto_relnum}%{?dist}

Summary:	WPA supplicant tool class for pScheduler
BuildArch:	noarch
License:	ASL 2.0
Vendor:	perfSONAR
Group:		Unspecified

Source0:	%{short}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

Requires:	pscheduler-server >= 4.4.0
Requires:	pscheduler-account
Requires:	%{_pscheduler_python}-pscheduler >= 4.4.0
Requires:	pscheduler-test-rtt
Requires:	%{_pscheduler_python}-icmperror

Requires:	sudo
Requires:       isc-dhcp-common
Requires:       wpasupplicant

BuildRequires:	pscheduler-rpm


%description
WPA-supplicant tool class for pScheduler


%prep
%setup -q -n %{short}-%{version}


%define dest %{_pscheduler_tool_libexec}/%{short}

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
