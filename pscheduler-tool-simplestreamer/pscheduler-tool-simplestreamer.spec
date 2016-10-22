#
# RPM Spec for pScheduler Simple Streamer Tool
#

%define short	simplestreamer
Name:		pscheduler-tool-%{short}
Version:	1.0
Release:	0.13.rc1%{?dist}

Summary:	Simple Streamer tool class for pScheduler
BuildArch:	noarch
License:	Apache 2.0
Group:		Unspecified

Source0:	%{short}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

Requires:	pscheduler-server
Requires:	python-pscheduler
Requires:	pscheduler-test-simplestream
requires:	nc

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
     DOCDIR=$RPM_BUILD_ROOT/%{_pscheduler_tool_doc} \
     install

%post
if [ "$1" -eq 1 ]
then
%if 0%{?el6}
    # TODO: It would be nicer if this entry were placed at the end so
    # it doesn't have to be evaluated when processing traffic that
    # needs low latency.
    iptables -I INPUT \
        -p tcp -m state --state NEW -m tcp --dport 10000:10010 -j ACCEPT
    service iptables save
%endif
%if 0%{?el7}
    firewall-cmd -q --add-port=10000-10010/tcp --permanent
    systemctl restart firewalld
%endif
fi
pscheduler internal warmboot


%postun
if [ "$1" -eq 0 ]
then
%if 0%{?el6}
    iptables -D INPUT \
        -p tcp -m state --state NEW -m tcp --dport 10000:10010 -j ACCEPT
    service iptables save
%endif
%if 0%{?el7}
    firewall-cmd -q --remove-port=10000-10010/tcp --permanent
    systemctl restart firewalld
%endif
fi
pscheduler internal warmboot









%files
%defattr(-,root,root,-)
%{dest}
%{_pscheduler_tool_doc}/*
