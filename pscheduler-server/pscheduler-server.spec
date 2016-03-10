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

%post
iptables -A INPUT \
    -p tcp -m state --state NEW -m tcp --dport 29285 -j ACCEPT
service iptables save

for SERVICE in ticker runner archiver api-server
do
    chkconfig "pscheduler-${SERVICE}" on
done

%preun
for SERVICE in ticker runner archiver api-server
do
    chkconfig "pscheduler-${SERVICE}" off
done

iptables -D INPUT \
	 -p tcp -m state --state NEW -m tcp --dport 29285 -j ACCEPT
service iptables save

%files
%defattr(-,root,root,-)
%{_initddir}/*
%{_bindir}/*
