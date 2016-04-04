#
# RPM Spec for pScheduler Server
#

Name:		pscheduler-server
Version:	0.0
Release:	1%{?dist}

Summary:	pScheduler Server
BuildArch:	noarch
License:	Apache 2.0
Group:		Unspecified

Source0:	%{name}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

Requires:	pscheduler-database
Requires:	python-Flask
Requires:	python-requests



%description
The pScheduler server

%prep
%setup -q

%build
make

%install
make \
     INITDDIR=$RPM_BUILD_ROOT/%{_initddir} \
     BINDIR=$RPM_BUILD_ROOT/%{_bindir} \
     install


%pre
# TODO: Should probably stop the service if this is an upgrade.


%post
for SERVICE in ticker runner archiver scheduler
do
    chkconfig "pscheduler-${SERVICE}" on
    service "pscheduler-${SERVICE}" start
done


%preun
for SERVICE in ticker runner archiver scheduler
do
    NAME="pscheduler-${SERVICE}"
    service "${NAME}" stop
    chkconfig "${NAME}" off
done


%files
%defattr(-,root,root,-)
%{_initddir}/*
%{_bindir}/*
