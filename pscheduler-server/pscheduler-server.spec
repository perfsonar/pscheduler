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
Requires:	pscheduler-account
Requires:	pscheduler-database
Requires:	python-Flask
Requires:	python-requests



%description
The pScheduler server

%prep
%setup -q


%build
make \
     DAEMONDIR=%{_pscheduler_daemons} \
     DSNFILE=%{_pscheduler_database_dsn_file} \
     PSUSER=%{_pscheduler_user} \
     VAR=%{_var}


%install
make \
     INITDDIR=$RPM_BUILD_ROOT/%{_initddir} \
     DAEMONDIR=$RPM_BUILD_ROOT/%{_pscheduler_daemons} \
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
%{_pscheduler_daemons}/*
%{_pscheduler_commands}/*
