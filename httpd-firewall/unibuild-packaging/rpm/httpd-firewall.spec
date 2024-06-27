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
Requires:	firewalld
Requires:	rpm-post-wrapper


%description
Firewall configuration for allowing access to HTTPD


%post
rpm-post-wrapper '%{name}' "$@" <<'POST-WRAPPER-EOF'
systemctl enable --now firewalld
firewall-cmd -q --add-service=https --permanent
systemctl reload-or-try-restart firewalld
POST-WRAPPER-EOF



%files
# No files.
