#
# RPM Spec for pScheduler BWCTL Tracepath Tool
#

%define short	bwctltracepath
Name:		pscheduler-tool-%{short}
Version:	1.0.2
Release:	1%{?dist}

Summary:	pScheduler BWCTL Tracepath Tool
BuildArch:	noarch
License:	Apache 2.0
Group:		Unspecified

Source0:	%{short}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

Requires:	pscheduler-server
Requires:	python-pscheduler
Requires:	pscheduler-test-trace
Requires:	python-icmperror
Requires:	iputils
Requires:	bwctl-client
Requires:	bwctl-server

BuildRequires:	pscheduler-rpm


%description
pScheduler BWCTL Tracepath Tool


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
%{dest}
