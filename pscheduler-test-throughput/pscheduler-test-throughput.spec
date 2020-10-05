#
# RPM Spec for pScheduler Throughput Test
#

%define short	throughput
%define perfsonar_auto_version 4.3.0
%define perfsonar_auto_relnum 0.b1.1

Name:		pscheduler-test-%{short}
Version:	%{perfsonar_auto_version}
Release:	%{perfsonar_auto_relnum}%{?dist}

Summary:	Throughput test class for pScheduler
BuildArch:	noarch
License:	ASL 2.0
Vendor:	perfSONAR
Group:		Unspecified

Source0:	%{short}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

Requires:	pscheduler-server
Requires:	%{_pscheduler_python}-pscheduler
Requires:	%{_pscheduler_python}-jsontemplate

BuildRequires:	pscheduler-rpm
BuildRequires:	%{_pscheduler_python}-pscheduler
BuildRequires:  %{_pscheduler_python_epel}-nose

%description
Throughput test class for pScheduler


%prep
%setup -q -n %{short}-%{version}


%define dest %{_pscheduler_test_libexec}/%{short}

%build
make \
     PYTHON=%{_pscheduler_python} \
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
