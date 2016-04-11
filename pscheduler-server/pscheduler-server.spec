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

Requires:	curl
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
     COMMANDSDIR=$RPM_BUILD_ROOT/%{_pscheduler_commands} \
     install


%pre
if [ "$1" -eq 2 ]
then
    for SERVICE in ticker runner archiver scheduler
    do
        NAME="pscheduler-${SERVICE}"
        service "${NAME}" stop
        chkconfig "${NAME}" off
    done
fi


%post
for SERVICE in ticker runner archiver scheduler
do
    NAME="pscheduler-${SERVICE}"
    chkconfig "${NAME}" on
    service "${NAME}" start
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
%{_pscheduler_commands}/*
