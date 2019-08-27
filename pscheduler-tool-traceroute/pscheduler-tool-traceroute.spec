#
# RPM Spec for pScheduler Traceroute Tool
#

%define short	traceroute
%define perfsonar_auto_version 4.2.1
%define perfsonar_auto_relnum 0.a1.0

Name:		pscheduler-tool-%{short}
Version:	%{perfsonar_auto_version}
Release:	%{perfsonar_auto_relnum}%{?dist}

Summary:	pScheduler Traceroute Tool
BuildArch:	noarch
License:	ASL 2.0
Vendor:	perfSONAR
Group:		Unspecified

Source0:	%{short}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

Requires:	pscheduler-server
Requires:	pscheduler-account
Requires:	python-pscheduler
Requires:	pscheduler-test-trace
Requires:	python-icmperror
Requires:	traceroute
Requires:	sudo

BuildRequires:	pscheduler-account
BuildRequires:	pscheduler-rpm
BuildRequires:	traceroute

%description
pScheduler Traceroute Tool


%prep
%setup -q -n %{short}-%{version}


%define dest %{_pscheduler_tool_libexec}/%{short}

%install
make \
     DESTDIR=$RPM_BUILD_ROOT/%{dest} \
     install


# Enable sudo for traceroute

TRACEROUTE=$(which traceroute)

mkdir -p $RPM_BUILD_ROOT/%{_pscheduler_sudoersdir}
cat > $RPM_BUILD_ROOT/%{_pscheduler_sudoersdir}/%{name} <<EOF
#
# %{name}
#
Cmnd_Alias PSCHEDULER_TOOL_TRACEROUTE = ${TRACEROUTE}
%{_pscheduler_user} ALL = (root) NOPASSWD: ${TRACEROUTE}
Defaults!PSCHEDULER_TOOL_TRACEROUTE !requiretty


EOF

%post
pscheduler internal warmboot

%postun
pscheduler internal warmboot


%files
%defattr(-,root,root,-)
%license LICENSE
%{dest}
%attr(440,root,root) %{_pscheduler_sudoersdir}/*
