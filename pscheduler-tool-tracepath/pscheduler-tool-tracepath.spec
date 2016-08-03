#
# RPM Spec for pScheduler Tracepath Tool
#

%define short	tracepath
Name:		pscheduler-tool-%{short}
Version:	0.0
Release:	1%{?dist}

Summary:	pScheduler Tracepath Tool
BuildArch:	noarch
License:	Apache 2.0
Group:		Unspecified

Source0:	%{short}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

Requires:	pscheduler-core
Requires:	python-pscheduler
Requires:	pscheduler-test-trace
Requires:	python-icmperror
Requires:	iputils

BuildRequires:	pscheduler-rpm


%description
pScheduler Tracepath Tool


%prep
%setup -q -n %{short}-%{version}


%define dest %{_pscheduler_tool_libexec}/%{short}

%build
make \
     DESTDIR=$RPM_BUILD_ROOT/%{dest} \
     DOCDIR=$RPM_BUILD_ROOT/%{_pscheduler_tool_doc} \
     install

%post
# TODO: Insert iptables rules to allow traceroute out?  Tracepath
# sweeps a range of UDP ports.

%postun
# TODO: Delete iptables rules to allow traceroute out?


%files
%defattr(-,root,root,-)
%{dest}
