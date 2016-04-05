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

    # Put this rule after the last ACCEPT in the input chain
    POSITION=$(iptables -L INPUT \
        | sed -e '1,2d' \
        | awk '$1 ==  "ACCEPT" { print NR, $0 }' \
        | tail -1 \
        | sed -e 's| .*$||')


    iptables -I INPUT $(expr ${POSITION} + 1 ) \
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
