#
# RPM Spec for pScheduler Latency Background Test
#

%define short	latencybg
Name:		pscheduler-test-%{short}
Version:	1.0.2.1
Release:	1%{?dist}

Summary:	Latency Background test class for pScheduler
BuildArch:	noarch
License:	Apache 2.0
Group:		Unspecified

Source0:	%{short}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

Requires:	pscheduler-server
Requires:	python-pscheduler

BuildRequires:	pscheduler-rpm
BuildRequires:	python-pscheduler
BuildRequires:  python-nose

%description
Latency test class for pScheduler that runs in the background.


%prep
%setup -q -n %{short}-%{version}


%define dest %{_pscheduler_test_libexec}/%{short}

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

