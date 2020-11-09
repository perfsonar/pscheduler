#
# RPM Spec for pScheduler Paris-Traceroute Tool
#

%define short	paris-traceroute
%define perfsonar_auto_version 4.3.2
%define perfsonar_auto_relnum 0.a1.0

Name:		pscheduler-tool-%{short}
Version:	%{perfsonar_auto_version}
Release:	%{perfsonar_auto_relnum}%{?dist}

Summary:	pScheduler Paris Traceroute Tool
BuildArch:	noarch
License:	ASL 2.0
Vendor:	perfSONAR
Group:		Unspecified

Source0:	%{short}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

Requires:	pscheduler-server >= 4.3.0
Requires:	pscheduler-account
Requires:	%{_pscheduler_python}-pscheduler >= 4.3.0
Requires:	pscheduler-test-trace
Requires:	paris-traceroute
Requires:	sudo
Requires:	%{_pscheduler_python}-icmperror

BuildRequires:	pscheduler-account
BuildRequires:	pscheduler-rpm
BuildRequires:	paris-traceroute

%description
pScheduler Paris Traceroute Tool


%prep
%setup -q -n %{short}-%{version}


%define dest %{_pscheduler_tool_libexec}/%{short}

%install
make \
     DESTDIR=$RPM_BUILD_ROOT/%{dest} \
     install


# Enable sudo for traceroute

PARIS_TRACEROUTE=$(which paris-traceroute)

mkdir -p $RPM_BUILD_ROOT/%{_pscheduler_sudoersdir}
cat > $RPM_BUILD_ROOT/%{_pscheduler_sudoersdir}/%{name} <<EOF
#
# %{name}
#
Cmnd_Alias PSCHEDULER_TOOL_PARIS_TRACEROUTE = ${PARIS_TRACEROUTE}
%{_pscheduler_user} ALL = (root) NOPASSWD: ${PARIS_TRACEROUTE}
Defaults!PSCHEDULER_TOOL_PARIS_TRACEROUTE !requiretty


EOF


%post
pscheduler internal warmboot

%postun
ldconfig
pscheduler internal warmboot


%files
%defattr(-,root,root,-)
%license LICENSE
%{dest}
%attr(440,root,root) %{_pscheduler_sudoersdir}/*
