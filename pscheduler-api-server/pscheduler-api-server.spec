#
# RPM Spec for pScheduler Server
#

Name:		pscheduler-api-server
Version:	0.0
Release:	1%{?dist}

Summary:	pScheduler REST API Server
BuildArch:	noarch
License:	Apache 2.0
Group:		Unspecified

Source0:	%{name}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

BuildRequires:	pscheduler-account
BuildRequires:	pscheduler-rpm
BuildRequires:	python-pscheduler
BuildRequires:	m4

Requires:	pscheduler-server
Requires:	mod_wsgi
Requires:	python-pscheduler
# TODO: See what else this needs at runtime.


%description
The pScheduler REST API server



%define httpd_conf_d %{_sysconfdir}/httpd/conf.d
%define conf	     %{httpd_conf_d}/%{name}.conf

# Note that we want this here because it seems to work well without
# assistance on systems where selinux is enabled.  Anywhere else and
# there'd have to be a 'chcon -R -t httpd_user_content_t'.
%define api_dir	     %{_var}/www/%{name}

%prep
%setup -q


%install

API_ROOT="$(python -c 'import pscheduler ; print pscheduler.api_root()')"

make \
     'USER_NAME=%{_pscheduler_user}' \
     'GROUP_NAME=%{_pscheduler_group}' \
     "API_ROOT=${API_ROOT}" \
     "API_DIR=%{api_dir}" \
     "CONF_D=%{httpd_conf_d}" \
     "PREFIX=${RPM_BUILD_ROOT}" \
     install


%post
# On systems with SELINUX, allow database connections.
if selinuxenabled
then
    echo "Setting SELinux permissions (may take awhile)"
    setsebool -P httpd_can_network_connect_db 1
fi

chkconfig httpd on

service httpd restart


%postun
# TODO: Determine if we want to shut this off, as other services might
# be using it.
# if selinuxenabled
# then
#     echo "Setting SELinux permissions (may take awhile)"
#     setsebool -P httpd_can_network_connect_db 1
# fi


# TODO: Do we want this or a reload?
service httpd condrestart


%files
%defattr(-,%{_pscheduler_user},%{_pscheduler_group},-)
%{api_dir}
%attr(444,root,root) %{conf}
