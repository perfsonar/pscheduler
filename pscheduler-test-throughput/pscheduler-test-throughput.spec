#
# RPM Spec for pScheduler Throughput Test
#

%define short	throughput
Name:		pscheduler-test-%{short}
Version:	1.1.5
Release:	1%{?dist}

Summary:	Throughput test class for pScheduler
BuildArch:	noarch
License:	ASL 2.0
Vendor:	perfSONAR
Group:		Unspecified

Source0:	%{short}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

Requires:	pscheduler-server
Requires:	python-pscheduler
Requires:	python-jsontemplate
BuildRequires:	pscheduler-rpm
BuildRequires:	python-pscheduler
BuildRequires:  python-nose

%description
Throughput test class for pScheduler


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
