#
# RPM Spec for pScheduler nuttcp Tool
#

%define short	nuttcp
Name:		pscheduler-tool-%{short}
Version:	1.0
Release:	0.7.rc1%{?dist}

Summary:	nuttcp tool class for pScheduler
BuildArch:	noarch
License:	Apache 2.0
Group:		Unspecified

Source0:	%{short}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

Requires:	pscheduler-server
Requires:	python-pscheduler
Requires:	pscheduler-test-throughput
Requires:	nuttcp >= 8.1.3

BuildRequires:	pscheduler-rpm


%description
nuttcp tool class for pScheduler


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
     CONFDIR=$RPM_BUILD_ROOT/%{_pscheduler_tool_confdir}\
     install

%post
if [ "$1" -eq 1 ]
then
%if 0%{?el6}
    # Put our rule after the last ACCEPT in the input chain
    INPUT_LENGTH=$(iptables -L INPUT | egrep -e '^ACCEPT' | wc -l)
    iptables -I INPUT $(expr ${INPUT_LENGTH} + 1 ) \
        -p tcp -m state --state NEW -m tcp --dport 5101 -j ACCEPT
    iptables -I INPUT $(expr ${INPUT_LENGTH} + 1 ) \
        -p udp -m state --state NEW -m udp --dport 5101 -j ACCEPT
    iptables -I INPUT $(expr ${INPUT_LENGTH} + 1 ) \
        -p tcp -m state --state NEW -m tcp --dport 5000 -j ACCEPT
    service iptables save
%endif
%if 0%{?el7}
    firewall-cmd -q --add-port=5101/tcp --permanent
    firewall-cmd -q --add-port=5101/udp --permanent
    firewall-cmd -q --add-port=5000/tcp --permanent
    systemctl restart firewalld
%endif
fi
pscheduler internal warmboot


%postun
if [ "$1" -eq 0 ]
then
%if 0%{?el6}
    iptables -D INPUT \
        -p tcp -m state --state NEW -m tcp --dport 5101 -j ACCEPT
    iptables -D INPUT \
        -p udp -m state --state NEW -m udp --dport 5101 -j ACCEPT
    iptables -D INPUT \
        -p tcp -m state --state NEW -m tcp --dport 5000 -j ACCEPT
    # TODO: Make this use systemd on CentOS 7
    service iptables save
%endif
%if 0%{?el7}
    firewall-cmd -q --remove-port=5101/tcp --permanent
    firewall-cmd -q --remove-port=5101/udp --permanent
    firewall-cmd -q --remove-port=5000/tcp --permanent
    systemctl restart firewalld
%endif
fi
pscheduler internal warmboot


%files
%defattr(-,root,root,-)
%config(noreplace) %{_pscheduler_tool_confdir}/*
%{dest}
%{_pscheduler_tool_doc}/*
