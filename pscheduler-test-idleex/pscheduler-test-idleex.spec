#
# RPM Spec for pScheduler Idle Exclusive Test
#

%define short	idleex
Name:		pscheduler-test-%{short}
Version:	1.0.0.3
Release:	1%{?dist}

Summary:	Idle Exclusive test class for pScheduler
BuildArch:	noarch
License:	Apache 2.0
Group:		Unspecified

Source0:	%{short}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

Requires:	pscheduler-server
Requires:	python-pscheduler

BuildRequires:	pscheduler-rpm


%description
Idle test class for pScheduler that runs exclusively.


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
