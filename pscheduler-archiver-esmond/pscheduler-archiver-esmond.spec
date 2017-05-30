#
# RPM Spec for pScheduler Esmond Archiver
#

%define short	esmond
Name:		pscheduler-archiver-esmond
Version:	1.0.0.4
Release:	1%{?dist}

Summary:	Esmond archiver class for pScheduler
BuildArch:	noarch
License:	Apache 2.0
Group:		Unspecified

Source0:	%{short}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

Requires:	pscheduler-server
Requires:	python-requests
Requires:	python-memcached
Requires:	memcached
Requires(post):	memcached
%if 0%{?el7}
%{?systemd_requires: %systemd_requires}
%else
Requires:		chkconfig
%endif

BuildRequires:	pscheduler-rpm


%define directory %{_includedir}/make

%description
This archiver sends JSON test results to Esmond Measurement Archive


%prep
%setup -q -n %{short}-%{version}


%define dest %{_pscheduler_archiver_libexec}/%{short}

%build
make \
     DESTDIR=$RPM_BUILD_ROOT/%{dest} \
     install


%post
pscheduler internal warmboot

#Only start memcached on new install so people have ability to disable if they so desire
if [ "$1" = "1" ]; then

%if 0%{?el7}
    #enable memcached on new install
    systemctl enable memcached.service
    systemctl start memcached.service
%else
    /sbin/chkconfig memcached on
    /sbin/service memcached start
%endif

fi



%postun
pscheduler internal warmboot


%files
%defattr(-,root,root,-)
%{dest}
