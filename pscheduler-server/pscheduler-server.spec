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

%post
chkconfig pscheduler-ticker on
# TODO: chkconfig pscheduler-runner on

%preun
chkconfig pscheduler-ticker off
# TODO: chkconfig pscheduler-runneroff



%files
%defattr(-,root,root,-)
%{_initddir}/*
%{_bindir}/*
