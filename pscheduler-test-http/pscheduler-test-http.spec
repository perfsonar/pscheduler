#
# RPM Spec for pScheduler HTTP Test
#

%define short	http
Name:		pscheduler-test-%{short}
Version:	1.1.6
Release:	1%{?dist}

Summary:	http test for pScheduler
BuildArch:	noarch
License:	ASL 2.0
Vendor:	perfSONAR
Group:		Unspecified

Source0:	%{short}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

Requires:	pscheduler-server
Requires:	python-pscheduler >= 1.3
Requires:	python-jsontemplate

BuildRequires:	pscheduler-rpm


%description
HTTP test class for pScheduler


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
