#
# RPM Spec for pScheduler Dublin-Traceroute Tool
#

%define short	dublin-traceroute
%define perfsonar_auto_version 5.1.4
%define perfsonar_auto_relnum 1

Name:		pscheduler-tool-%{short}
Version:	%{perfsonar_auto_version}
Release:	%{perfsonar_auto_relnum}%{?dist}

Summary:	pScheduler Dublin Traceroute Tool
BuildArch:	noarch
License:	ASL 2.0
Vendor:		perfSONAR
Group:		Unspecified

Source0:	%{short}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

Requires:	pscheduler-server >= 4.3.0
Requires:	pscheduler-account
Requires:	%{_pscheduler_python}-pscheduler >= 4.3.0
Requires:	pscheduler-test-trace
Requires:	dublin-traceroute >= 0.4.2
Requires:	%{_pscheduler_python}-icmperror
Requires:	rpm-post-wrapper

BuildRequires:	pscheduler-account
BuildRequires:	pscheduler-rpm

%description
pScheduler Dublin Traceroute Tool


%prep
%setup -q -n %{short}-%{version}


%define dest %{_pscheduler_tool_libexec}/%{short}

%install
make \
     DESTDIR=$RPM_BUILD_ROOT/%{dest} \
     install


%post
rpm-post-wrapper '%{name}' "$@" <<'POST-WRAPPER-EOF'
pscheduler internal warmboot
POST-WRAPPER-EOF

%postun
pscheduler internal warmboot


%files
%defattr(-,root,root,-)
%license LICENSE
%{dest}
