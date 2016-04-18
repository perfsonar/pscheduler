#
# RPM Spec for pScheduler Tracepath Tool
#

%define short	tracepath
Name:		pscheduler-tool-%{short}
Version:	0.0
Release:	1%{?dist}

Summary:	Simple Streamer tool class for pScheduler
BuildArch:	noarch
License:	Apache 2.0
Group:		Unspecified

Source0:	%{short}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

Requires:	pscheduler-core
Requires:	python-pscheduler
Requires:	pscheduler-test-trace
requires:	iputils

BuildRequires:	pscheduler-rpm


%define directory %{_includedir}/make

%description
Simple Stream tool class for pScheduler


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
