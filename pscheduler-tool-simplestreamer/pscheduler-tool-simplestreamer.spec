#
# RPM Spec for pScheduler Simple Streamer Tool
#

%define short	simplestreamer
Name:		pscheduler-tool-%{short}
Version:	1.1
Release:	0.1.b1%{?dist}

Summary:	Simple Streamer tool class for pScheduler
BuildArch:	noarch
License:	ASL 2.0
Vendor:	perfSONAR
Group:		Unspecified

Source0:	%{short}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

Requires:	pscheduler-server
Requires:	python-pscheduler
Requires:	pscheduler-test-simplestream >= 1.1.1

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

