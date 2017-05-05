#
# RPM Spec for pScheduler RabbitMQ Archiver
#

%define short	rabbitmq
Name:		pscheduler-archiver-%{short}
Version:	1.0.0.2
Release:	1%{?dist}

Summary:	RabbitMQ archiver class for pScheduler
BuildArch:	noarch
License:	Apache 2.0
Group:		Unspecified

Source0:	%{short}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

Requires:	pscheduler-server

# Note that this doesn't get used since we're supplying our own 0.10.0
# as a stopgap.
# TODO: Make this require >= 0.9.8 once EL6 goes away.
#Requires:	python-pika

BuildRequires:	pscheduler-rpm


%define directory %{_includedir}/make

%description
This archiver sends JSON test results to RabbitMQ


%prep
%setup -q -n %{short}-%{version}


%define dest %{_pscheduler_archiver_libexec}/%{short}

%build
make \
     DESTDIR=$RPM_BUILD_ROOT/%{dest} \
     install

%post
pscheduler internal warmboot

%postun
pscheduler internal warmboot

%files
%defattr(-,root,root,-)
%{dest}
