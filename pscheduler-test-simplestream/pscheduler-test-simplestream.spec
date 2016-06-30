#
# RPM Spec for pScheduler Simplestream Test
#

%define short	simplestream
Name:		pscheduler-test-%{short}
Version:	0.0
Release:	1%{?dist}

Summary:	Simplestream test class for pScheduler
BuildArch:	noarch
License:	Apache 2.0
Group:		Unspecified

Source0:	%{short}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

Requires:	pscheduler-core
Requires:	python-pscheduler

BuildRequires:	pscheduler-rpm


%description
Simplestream test class for pScheduler


%prep
%setup -q -n %{short}-%{version}


%define dest %{_pscheduler_test_libexec}/%{short}

%build
make \
     DESTDIR=$RPM_BUILD_ROOT/%{dest} \
     DOCDIR=$RPM_BUILD_ROOT/%{_pscheduler_test_doc} \
     install


%files
%defattr(-,root,root,-)
%{dest}
%{_pscheduler_test_doc}/*
