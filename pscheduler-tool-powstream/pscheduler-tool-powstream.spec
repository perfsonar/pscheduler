#
# RPM Spec for pScheduler powstream Tool
#

%define short	    powstream
%define resultdir	%{_pscheduler_tool_vardir}/%{short}

Name:		pscheduler-tool-%{short}
Version:	1.0
Release:	0.25.rc3%{?dist}

Summary:	powstream tool class for pScheduler
BuildArch:	noarch
License:	Apache 2.0
Group:		Unspecified

Source0:	%{short}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

Requires:	pscheduler-server
Requires:	python-pscheduler
Requires:	pscheduler-test-latencybg
Requires:	pytz
Requires:	owamp-client
Requires:	owamp-server

BuildRequires:	pscheduler-rpm


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
%defattr(-,pscheduler,pscheduler,-)
%config(noreplace) %{_pscheduler_tool_confdir}/*
%{dest}

