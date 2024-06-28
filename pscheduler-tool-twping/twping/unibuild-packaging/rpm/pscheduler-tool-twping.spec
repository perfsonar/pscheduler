#
# RPM Spec for pScheduler twping Tool
#

%define short	twping
%define perfsonar_auto_version 5.2.0
%define perfsonar_auto_relnum 0.a1.0

Name:		pscheduler-tool-%{short}
Version:	%{perfsonar_auto_version}
Release:	%{perfsonar_auto_relnum}%{?dist}

Summary:	twping tool class for pScheduler
BuildArch:	noarch
License:	ASL 2.0
Vendor:	perfSONAR
Group:		Unspecified

Source0:	%{short}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

Requires:	pscheduler-server >= 4.3.0
Requires:	%{_pscheduler_python}-pscheduler >= 4.3.0
Requires:	pscheduler-test-latency
Requires:	twamp-client
Requires:	rpm-post-wrapper

BuildRequires:	pscheduler-rpm
BuildRequires:	%{_pscheduler_python}-pscheduler
BuildRequires:  %{_pscheduler_python}-nose

%description
twping tool class for pScheduler


%prep
%setup -q -n %{short}-%{version}


%define dest %{_pscheduler_tool_libexec}/%{short}

%build
make \
     PYTHON=%{_pscheduler_python} \
     DESTDIR=$RPM_BUILD_ROOT/%{dest} \
     CONFDIR=$RPM_BUILD_ROOT/%{_pscheduler_tool_confdir}\
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
%config(noreplace) %{_pscheduler_tool_confdir}/*
%{dest}
