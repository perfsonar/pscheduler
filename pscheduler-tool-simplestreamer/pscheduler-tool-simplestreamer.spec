#
# RPM Spec for pScheduler Simple Streamer Tool
#

%define short	simplestreamer
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
Requires:	pscheduler-test-simplestream
requires:	nc

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
if [ "$1" -eq 1 ]
then

    # Put this rule after the last ACCEPT in the input chain
    POSITION=$(iptables -L INPUT \
        | sed -e '1,2d' \
        | awk '$1 ==  "ACCEPT" { print NR, $0 }' \
        | tail -1 \
        | sed -e 's| .*$||')

    iptables -I INPUT $(expr ${POSITION} + 1 ) \
        -p tcp -m state --state NEW -m tcp --dport 10000:10100 -j ACCEPT

fi

%postun
if [ "$1" -eq 0 ]
then
    iptables -D INPUT \
        -p tcp -m state --state NEW -m tcp --dport 10000:10100 -j ACCEPT
    service iptables save
fi


%files
%defattr(-,root,root,-)
%{dest}
%{_pscheduler_tool_doc}/*
