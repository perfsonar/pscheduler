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
# Note that the actual definition of what protocol is used is part of
# python-pscheduler, but this package is what does the serving, so
# mod_ssl is required here.
Requires:	mod_ssl
Requires:	mod_wsgi
Requires:	python-pscheduler
Requires:	python-requests
Requires:	pytz
# TODO: See what else this needs at runtime.


%description
The pScheduler REST API server



%define httpd_conf_d %{_sysconfdir}/httpd/conf.d
%define conf	     %{httpd_conf_d}/%{name}.conf

%define server_conf_dir %{_pscheduler_sysconfdir}
%define limits_file     %{server_conf_dir}/limits

# Note that we want this here because it seems to work well without
# assistance on systems where selinux is enabled.  Anywhere else and
# there'd have to be a 'chcon -R -t httpd_user_content_t'.
%define api_dir	     %{_var}/www/%{name}

%prep
%if 0%{?el6}%{?el7} == 0
echo "This package cannot be built on %{dist}."
false
%endif

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
     "DSN_FILE=%{_pscheduler_database_dsn_file}" \
     "LIMITS_FILE=%{limits_file}" \
     install

mkdir -p ${RPM_BUILD_ROOT}/%{server_conf_dir}


%post
# On systems with SELINUX, allow database connections.
if selinuxenabled
then
    STATE=$(getsebool httpd_can_network_connect_db | awk '{ print $3 }')
    if [ "${STATE}" != "on" ]
    then
        echo "Setting SELinux permissions (may take awhile)"
        setsebool -P httpd_can_network_connect_db 1
    fi
fi



%if 0%{?el6}
chkconfig httpd on
service httpd restart
%endif
%if 0%{?el7}
systemctl enable httpd
systemctl restart httpd
%endif



%postun
# TODO: Determine if we want to shut this off, as other services might
# be using it.
# if selinuxenabled
# then
#     echo "Setting SELinux permissions (may take awhile)"
#     setsebool -P httpd_can_network_connect_db 1
# fi

%if 0%{?el6}
service httpd restart
%endif
%if 0%{?el7}
systemctl restart httpd
%endif



%files
%defattr(-,%{_pscheduler_user},%{_pscheduler_group},-)
%{api_dir}
%attr(444,root,root) %{conf}
