#
# RPM Spec for pScheduler Idle Exclusive Test
#

%define short	idleex
Name:		pscheduler-test-%{short}
Version:	1.0
Release:	0.10.rc1%{?dist}

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
     DOCDIR=$RPM_BUILD_ROOT/%{_pscheduler_test_doc} \
     install



%post
pscheduler internal warmboot


%postun
pscheduler internal warmboot


%files
%defattr(-,root,root,-)
%{dest}
%{_pscheduler_test_doc}/*
