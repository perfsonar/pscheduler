#
# RPM Spec for pScheduler Snooze Tool
#

%define short	snooze
Name:		pscheduler-tool-%{short}
Version:	0.0
Release:	1%{?dist}

Summary:	Sleep tool class for pScheduler
BuildArch:	noarch
License:	Apache 2.0
Group:		Unspecified

Source0:	%{short}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

Requires:	pscheduler-core
Requires:	python-pscheduler
Requires:	pscheduler-test-idle

BuildRequires:	pscheduler-rpm


%define directory %{_includedir}/make

%description
Snooze tool class for pScheduler


%prep
%setup -q -n %{short}-%{version}


%define dest %{_pscheduler_tool_libexec}/%{short}

%build
make \
     DESTDIR=$RPM_BUILD_ROOT/%{dest} \
     DOCDIR=$RPM_BUILD_ROOT/%{_pscheduler_tool_doc} \
     install


%files
%defattr(-,root,root,-)
%{dest}
%{_pscheduler_tool_doc}/*
