#
# RPM Spec for pScheduler Simple Streamer Tool
#

%define short	simplestreamer
%define perfsonar_auto_version 4.2.2
%define perfsonar_auto_relnum 1

Name:		pscheduler-tool-%{short}
Version:	%{perfsonar_auto_version}
Release:	%{perfsonar_auto_relnum}%{?dist}

Summary:	Simple Streamer tool class for pScheduler
BuildArch:	noarch
License:	ASL 2.0
Vendor:	perfSONAR
Group:		Unspecified

Source0:	%{short}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

Requires:	pscheduler-server
Requires:	python-pscheduler
Requires:	pscheduler-test-simplestream >= 1.0.2.6.1

BuildRequires:	pscheduler-rpm


%description
Simple Stream tool class for pScheduler


%prep
%if 0%{?el6}%{?el7} == 0
echo "This package cannot be built on %{dist}."
false
%endif

%setup -q -n %{short}-%{version}


%define dest %{_pscheduler_tool_libexec}/%{short}

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

