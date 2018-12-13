#
# RPM Spec for pScheduler Idle Test
#

%define short	idle
Name:		pscheduler-test-%{short}
Version:	1.1.5
Release:	1%{?dist}

Summary:	Idle test class for pScheduler
BuildArch:	noarch
License:	ASL 2.0
Vendor:	perfSONAR
Group:		Unspecified

Source0:	%{short}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

Requires:	pscheduler-server >= 1.1.5
Requires:	python-pscheduler

BuildRequires:	pscheduler-rpm


%description
Idle test class for pScheduler


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
%license LICENSE
%{dest}
