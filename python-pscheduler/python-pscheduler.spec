#
# RPM Spec for Python pScheduler Module
#

%define short	pscheduler
Name:		python-%{short}
Version:	1.3.2.6.1
Release:	1%{?dist}
Summary:	Utility functions for pScheduler
BuildArch:	noarch
License:	Apache 2.0
Group:		Development/Libraries

Provides:	%{name} = %{version}-%{release}
Prefix:		%{_prefix}

Vendor:		The perfSONAR Development Team
Url:		http://www.perfsonar.net

Source0:	%{short}-%{version}.tar.gz

# NOTE: The runtime Python module requirements must be duplicated in
# BuildRequires because they're required to run the tests.

Requires:	iputils
Requires:	python-dateutil
Requires:	python-dns
Requires:	python-isodate
Requires:	python-ipaddr
%if 0%{?el6}
Requires:	python-jsonschema
%endif
%if 0%{?el7}
Requires:	python2-jsonschema
%endif
Requires:	python-netaddr
Requires:	python-netifaces
Requires:	python-ntplib
Requires:	python-psycopg2 >= 2.2.0
Requires:	python-py-radix
# The limit system uses this.
Requires:	pscheduler-jq-library
Requires:	python-pyjq >= 2.0.1
Requires:	python-requests
Requires:	python-subprocess32
Requires:	python-tzlocal
Requires:	pytz
Requires:	rsyslog
Requires:	logrotate

BuildRequires:	pscheduler-rpm
BuildRequires:	python-coverage
BuildRequires:	python-nose
BuildRequires:	python-setuptools

# NOTE:  Cloned from above.
BuildRequires:	iputils
BuildRequires:	python-dateutil
BuildRequires:	python-dns
BuildRequires:	python-isodate
BuildRequires:	python-ipaddr
%if 0%{?el6}
BuildRequires:	python-jsonschema
%endif
%if 0%{?el7}
BuildRequires:	python2-jsonschema
%endif
BuildRequires:	python-netaddr
BuildRequires:	python-netifaces
BuildRequires:	python-ntplib
BuildRequires:	python-psycopg2 >= 2.2.0
BuildRequires:	python-py-radix
# The limit system uses this.
BuildRequires:	pscheduler-jq-library
BuildRequires:	python-pyjq >= 2.0.1
BuildRequires:	python-requests
BuildRequires:	python-subprocess32
BuildRequires:	python-tzlocal
BuildRequires:	pytz


%define limit_config %{_pscheduler_sysconfdir}/limits.conf
%define logdir %{_var}/log/pscheduler
%define logrotate_d %{_sysconfdir}/logrotate.d
%define syslog_d %{_sysconfdir}/rsyslog.d

%define macros %{_pscheduler_rpmmacroprefix}%{name}


%description
Utility functions for pScheduler


# Don't do automagic post-build things.
%global              __os_install_post %{nil}


%prep
%setup -q -n %{short}-%{version}


%build
make


%install
python setup.py install --root=$RPM_BUILD_ROOT -O1  --record=INSTALLED_FILES

mkdir -p $RPM_BUILD_ROOT/%{logrotate_d}
cat > $RPM_BUILD_ROOT/%{logrotate_d}/%{name} <<EOF
# Rotation for logs produced by pScheduler

%{logdir}/pscheduler.log
{
    missingok
    sharedscripts
    postrotate
        /bin/kill -HUP \`cat %{_rundir}/syslogd.pid 2> /dev/null\` 2> /dev/null || true
    endscript
}
EOF

mkdir -p $RPM_BUILD_ROOT/%{syslog_d}
cat > $RPM_BUILD_ROOT/%{syslog_d}/%{name}.conf <<EOF
# Syslog configuration for pScheduler

local4.*  %{logdir}/pscheduler.log
EOF

mkdir -p $RPM_BUILD_ROOT/%{_pscheduler_rpmmacrodir}
cat > $RPM_BUILD_ROOT/%{macros} <<EOF
#
# RPM Macros for %{name} Version %{version}
#

%%_pscheduler_limit_config %{limit_config}
EOF



%clean
rm -rf $RPM_BUILD_ROOT

%post
%if 0%{?el6}
service rsyslog restart
%endif
%if 0%{?el7}
systemctl restart rsyslog
%endif


%postun
%if 0%{?el6}
service rsyslog restart
%endif
%if 0%{?el7}
systemctl restart rsyslog
%endif


%files -f INSTALLED_FILES
%defattr(-,root,root)
%config(noreplace) %{logrotate_d}/*
%config(noreplace) %{syslog_d}/*
%attr(444,root,root) %{_pscheduler_rpmmacroprefix}*
