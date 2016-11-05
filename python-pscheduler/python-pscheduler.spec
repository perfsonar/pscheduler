#
# RPM Spec for Python pScheduler Module
#

%define short	pscheduler
Name:		python-%{short}
Version:	1.1
Release:	0.15.rc2%{?dist}
Summary:	Utility functions for pScheduler
BuildArch:	noarch
License:	Apache 2.0
Group:		Development/Libraries

Provides:	%{name} = %{version}-%{release}
Prefix:		%{_prefix}

Vendor:		The perfSONAR Development Team
Url:		http://www.perfsonar.net

Source0:	%{short}-%{version}.tar.gz

Requires:	python-dateutil
Requires:	python-dnspython
Requires:	python-isodate
Requires:	python-jsonschema
Requires:	python-netaddr
Requires:	python-netifaces
Requires:	python-ntplib
Requires:	python-psycopg2 >= 2.2.0
Requires:	python-py-radix
Requires:	python-requests
Requires:	python-subprocess32
Requires:	python-tzlocal
Requires:	pytz
Requires:	rsyslog
# This is because the Log class uses debugging.
Requires:	rsyslog-debug
Requires:	logrotate

BuildRequires:	python-setuptools


%define logdir %{_var}/log/pscheduler
%define logrotate_d %{_sysconfdir}/logrotate.d
%define syslog_d %{_sysconfdir}/rsyslog.d


%description
Utility functions for pScheduler


# Don't do automagic post-build things.
%global              __os_install_post %{nil}


%prep
%setup -q -n %{short}-%{version}


%build
python setup.py build


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
        /bin/kill -HUP \`cat /var/run/syslogd.pid 2> /dev/null\` 2> /dev/null || true
    endscript
}
EOF

mkdir -p $RPM_BUILD_ROOT/%{syslog_d}
cat > $RPM_BUILD_ROOT/%{syslog_d}/%{name}.conf <<EOF
# Syslog configuration for pScheduler

local5.*  %{logdir}/pscheduler.log
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
%{logrotate_d}/*
%{syslog_d}/*
