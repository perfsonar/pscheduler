#
# RPM Spec for pScheduler Esmond Archiver
#

%define short	esmond
%define perfsonar_auto_version 5.0.0
%define perfsonar_auto_relnum 0.b1.1

Name:		pscheduler-archiver-esmond
Version:	%{perfsonar_auto_version}
Release:	%{perfsonar_auto_relnum}%{?dist}

Summary:	Esmond archiver class for pScheduler
BuildArch:	noarch
License:	ASL 2.0
Vendor:	perfSONAR
Group:		Unspecified

Source0:	%{short}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

Requires:	pscheduler-server >= 1.1.6
Requires:	%{_pscheduler_python}-pscheduler >= 1.3.7.1
Requires:	%{_pscheduler_python}-memcached
Requires:	memcached
Requires(post):	memcached
%if 0%{?el7}
%{?systemd_requires: %systemd_requires}
%else
Requires:		chkconfig
%endif

BuildRequires:	pscheduler-rpm
BuildRequires:  %{_pscheduler_python}-pscheduler
BuildRequires:  %{_pscheduler_python_epel}-nose

%define directory %{_includedir}/make

%description
This archiver sends JSON test results to Esmond Measurement Archive


%prep
%setup -q -n %{short}-%{version}


%define dest %{_pscheduler_archiver_libexec}/%{short}

%build
make \
     PYTHON=%{_pscheduler_python} \
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
%license LICENSE
%{dest}
