#
# RPM Spec for HTTPD WSGI Socket Configuration
#

Name:		httpd-wsgi-socket
Version:	1.0
Release:	1%{?dist}

Summary:	WSGI socket configuration for Apache HTTPD
BuildArch:	noarch

License:	Apache 2.0
Group:		Unspecified

# No Source:

Provides:	%{name} = %{version}-%{release}

Requires:	mod_wsgi

%description
WSGI socket configuration for Apache HTTPD


%define httpd_conf_d %{_sysconfdir}/httpd/conf.d
%define conf         %{httpd_conf_d}/%{name}.conf

%install
mkdir -p $RPM_BUILD_ROOT/%{httpd_conf_d}
cat > $RPM_BUILD_ROOT/%{conf} <<EOF
#
# System-Wide WSGI socket configuration for Apache HTTPD
#
WSGISocketPrefix /tmp/%{name}
EOF


%post
service httpd reload


%files
%{conf}
