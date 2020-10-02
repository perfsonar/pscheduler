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

Provides:	%{name} = %{version}-%{release}

Requires:	httpd


%description
Firewall configuration for allowing access to HTTPD


%prep
%if 0%{?el7}%{?el8} == 0
echo "This package cannot be built on %{dist}."
false
%endif


%post
systemctl enable --now firewalld
firewall-cmd -q --add-service=https --permanent
systemctl reload-or-try-restart firewalld



%files
# No files.
