#
# RPM Spec for httpd-firewall
#

%define short	httpd-firewall
Name:		%{short}
Version:	0.0
Release:	1%{?dist}

Summary:	Firewall configuration for allowing access to HTTPD
BuildArch:	noarch
License:	Apache 2.0
Group:		Unspecified

# No sources
# Source0:	%{short}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

Requires:	httpd


%description
Firewall configuration for allowing access to HTTPD


%prep
%if 0%{?el6}%{?el7} == 0
echo "This package cannot be built on %{dist}."
false
%endif


%post
if [ "$1" -eq 1 ]
then

%if 0%{?el6}

    # TODO: It would be nicer if this entry were placed at the end so
    # it doesn't have to be evaluated when processing traffic that
    # needs low latency.
    iptables -I INPUT \
        -p tcp -m state --state NEW -m tcp --dport 80 -j ACCEPT
    iptables -I INPUT \
        -p tcp -m state --state NEW -m tcp --dport 443 -j ACCEPT
    service iptables save
%endif

%if 0%{?el7}
    firewall-cmd -q --add-service=http --permanent
    firewall-cmd -q --add-service=https --permanent
    systemctl restart firewalld
%endif

fi

%postun
if [ "$1" -eq 0 ]
then
%if 0%{?el6}
    iptables -D INPUT \
        -p tcp -m state --state NEW -m tcp --dport 80 -j ACCEPT
    iptables -D INPUT \
        -p tcp -m state --state NEW -m tcp --dport 443 -j ACCEPT
    service iptables save
%endif
%if 0%{?el7}
    firewall-cmd -q --add-service=http --permanent
    firewall-cmd -q --add-service=https --permanent
    systemctl restart firewalld
%endif
fi


%files
# No files.
