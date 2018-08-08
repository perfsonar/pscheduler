#
# RPM Spec for pScheduler Snooze Tool
#

%define short	snooze
Name:		pscheduler-tool-%{short}
Version:	1.1
Release:	0.3.b1%{?dist}

Summary:	Sleep tool class for pScheduler
BuildArch:	noarch
License:	ASL 2.0
Vendor:	perfSONAR
Group:		Unspecified

Source0:	%{short}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

Requires:	pscheduler-server
Requires:	python-pscheduler
Requires:	pscheduler-test-idle

BuildRequires:	pscheduler-rpm


%description
Snooze tool class for pScheduler


%prep
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
