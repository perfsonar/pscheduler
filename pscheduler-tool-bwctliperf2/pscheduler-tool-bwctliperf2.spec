#
# RPM Spec for pScheduler BWCTL iperf2 Tool
#

%define short	bwctliperf2
Name:		pscheduler-tool-%{short}
Version:	1.0
Release:	0.13.rc1%{?dist}

Summary:	bwctliperf2 tool class for pScheduler
BuildArch:	noarch
License:	Apache 2.0
Group:		Unspecified

Source0:	%{short}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

Requires:	pscheduler-server
Requires:	python-pscheduler
Requires:	pscheduler-test-throughput
Requires:	bwctl-client
Requires:	bwctl-server
requires:	iperf

BuildRequires:	pscheduler-rpm


%description
bwctliperf2 tool class for pScheduler


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
    # Put our rule after the last ACCEPT in the input chain
    INPUT_LENGTH=$(iptables -L INPUT | egrep -e '^ACCEPT' | wc -l)
    iptables -I INPUT $(expr ${INPUT_LENGTH} + 1 ) \
        -p tcp -m state --state NEW -m tcp --dport 5001 -j ACCEPT
    iptables -I INPUT $(expr ${INPUT_LENGTH} + 1 ) \
        -p udp -m state --state NEW -m udp --dport 5001 -j ACCEPT
    service iptables save
%endif
%if 0%{?el7}
    firewall-cmd -q --add-port=5001/tcp --permanent
    firewall-cmd -q --add-port=5001/udp --permanent
    systemctl restart firewalld
%endif
fi
pscheduler internal warmboot


%postun
if [ "$1" -eq 0 ]
then
%if 0%{?el6}
    iptables -D INPUT \
        -p tcp -m state --state NEW -m tcp --dport 5001:5300 -j ACCEPT
    # TODO: Make this use systemd on CentOS 7
    service iptables save
%endif
%if 0%{?el7}
    firewall-cmd -q --remove-port=5001-5200/tcp --permanent
    systemctl restart firewalld
%endif
fi
pscheduler internal warmboot


%files
%defattr(-,root,root,-)
%{dest}
%{_pscheduler_tool_doc}/*
