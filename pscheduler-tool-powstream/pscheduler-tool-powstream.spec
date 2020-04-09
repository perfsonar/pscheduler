#
# RPM Spec for pScheduler powstream Tool
#

%define short	    powstream
%define resultdir	%{_pscheduler_tool_vardir}/%{short}

%define perfsonar_auto_version 4.3.0
%define perfsonar_auto_relnum 0.a0.0

Name:		pscheduler-tool-%{short}
Version:	%{perfsonar_auto_version}
Release:	%{perfsonar_auto_relnum}%{?dist}

Summary:	powstream tool class for pScheduler
BuildArch:	noarch
License:	ASL 2.0
Vendor:	perfSONAR
Group:		Unspecified

Source0:	%{short}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

Requires:	pscheduler-server
Requires:	%{_pscheduler_python}-pscheduler
Requires:	pscheduler-test-latencybg
Requires:	pytz
Requires:	owamp-client
Requires:	owamp-server

BuildRequires:	pscheduler-rpm
BuildRequires:	%{_pscheduler_python}-pscheduler
BuildRequires:  %{_pscheduler_python_epel}-nose

%description
powstream tool class for pScheduler


%prep
%if 0%{?el6}%{?el7} == 0
echo "This package cannot be built on %{dist}."
false
%endif

%setup -q -n %{short}-%{version}


%define dest %{_pscheduler_tool_libexec}/%{short}

%build
make \
     PYTHON=%{_pscheduler_python} \
     DESTDIR=$RPM_BUILD_ROOT/%{dest} \
     CONFDIR=$RPM_BUILD_ROOT/%{_pscheduler_tool_confdir}\
     install

%post
#make data directory
mkdir -p %{resultdir}
chown pscheduler:pscheduler %{resultdir}/
chmod 755 %{resultdir}
pscheduler internal warmboot

%postun
pscheduler internal warmboot


%files
%defattr(-,root,root,-)
%license LICENSE
%config(noreplace) %{_pscheduler_tool_confdir}/*
%{dest}
