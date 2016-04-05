#
# RPM Spec for iptables-httpd
#

%define short	httpd-iptables
Name:		%{short}
Version:	0.0
Release:	1%{?dist}

Summary:	Iptables configuration for allowing access to HTTPD
BuildArch:	noarch
License:	Apache 2.0
Group:		Unspecified

# No sources
# Source0:	%{short}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

Requires:	httpd


%description
Iptables configuration for allowing access to HTTPD


%post
if [ "$1" -eq 1 ]
then

    # TODO: It would be nicer if this entry were placed at the end so
    # it doesn't have to be evaluated when processing traffic that
    # needs low latency.
    iptables -I INPUT \
        -p tcp -m state --state NEW -m tcp --dport 80 -j ACCEPT
    service iptables save
fi

%postun
if [ "$1" -eq 0 ]
then
    iptables -D INPUT \
        -p tcp -m state --state NEW -m tcp --dport 80 -j ACCEPT
    service iptables save
fi


%files
# No files.
