#
# RPM Spec for Python pScheduler Module
#

%define perfsonar_auto_version 5.1.0
%define perfsonar_auto_relnum 0.b1.1

%define short	pscheduler
Name:		python-%{short}
Version:	%{perfsonar_auto_version}
Release:	%{perfsonar_auto_relnum}%{?dist}
Summary:	Utility functions for pScheduler
BuildArch:	noarch
License:        ASL 2.0	
Group:		Development/Libraries

Provides:	%{name} = %{version}-%{release}
Prefix:		%{_prefix}

Vendor:		perfSONAR
Url:		http://www.perfsonar.net

Source0:	%{short}-%{version}.tar.gz

# NOTE: The runtime Python module requirements must be duplicated in
# BuildRequires because they're required to run the tests.

Requires:	iputils

Requires:	python-attrs
Requires:	python-dateutil
Requires:	python-dns
Requires:	python-isodate
Requires:	python-jinja2
Requires:	python-jsonschema >= 3.0
Requires:	python-netaddr
Requires:	python-netifaces
Requires:	python-ntplib
Requires:	python-psutil
Requires:	python-psycopg2 >= 2.6.1
Requires:	python-py-radix
# The limit system uses this.
Requires:	pscheduler-jq-library
Requires:	python-pycurl
Requires:	python-pyjq >= 2.2.0
Requires:	python-tzlocal
Requires:	python-pytz
Requires:	rsyslog
Requires:	logrotate
Requires:       numactl

BuildRequires:	pscheduler-rpm
BuildRequires:  python
BuildRequires:	python-coverage
BuildRequires:	python-nose
BuildRequires:	python-setuptools
# NOTE:  Cloned from above.
BuildRequires:	iputils
BuildRequires:	python-attrs
BuildRequires:	python-dateutil
BuildRequires:	python-dns
BuildRequires:	python-isodate
BuildRequires:	python-jsonschema
BuildRequires:	python-netaddr
BuildRequires:	python-netifaces
BuildRequires:	python-ntplib
BuildRequires:	python-psutil
BuildRequires:	python-psycopg2 >= 2.2.0
BuildRequires:	python-py-radix
# The limit system uses this.
BuildRequires:	pscheduler-jq-library
BuildRequires:	python-pycurl
BuildRequires:	python-pyjq >= 2.2.0
BuildRequires:	python-tzlocal
BuildRequires:	python-pytz
BuildRequires:  numactl

%define limit_config %{_pscheduler_sysconfdir}/limits.conf
%define logdir %{_var}/log/pscheduler
%define logfile pscheduler.log
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

make CLASSES="%{_pscheduler_classes}"


%install
python setup.py install --root=$RPM_BUILD_ROOT -O1  --record=INSTALLED_FILES

mkdir -p $RPM_BUILD_ROOT/%{logrotate_d}
cat > $RPM_BUILD_ROOT/%{logrotate_d}/%{name} <<EOF
# Rotation for logs produced by pScheduler

%{logdir}/%{logfile}
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

local4.*  %{logdir}/%{logfile}
EOF

mkdir -p $RPM_BUILD_ROOT/%{_pscheduler_rpmmacrodir}
cat > $RPM_BUILD_ROOT/%{macros} <<EOF
#
# RPM Macros for %{name} Version %{version}
#

%%_pscheduler_limit_config %{limit_config}

%%_pscheduler_log_dir %{logdir}
%%_pscheduler_log_file %{logfile}
EOF



%clean
rm -rf $RPM_BUILD_ROOT

%post

# This removes a duplicate entry leftover from the Python 2 version.
# TODO: Remove this after we stop supporting 4.2.x.
OLD_LOGROTATE="%{logrotate_d}/python-pscheduler"
if [ -e "${OLD_LOGROTATE}" ]
then
    cat > "${OLD_LOGROTATE}" <<EOF
# Rotation for logs produced by pScheduler

### Removed forcibly by %{name} %{version} to avoid duplicate
### log file names.
EOF
fi

systemctl enable rsyslog
systemctl reload-or-try-restart rsyslog


%postun
systemctl reload-or-try-restart rsyslog


%files -f INSTALLED_FILES
%defattr(-,root,root)
%license LICENSE
%config(noreplace) %{logrotate_d}/*
%config(noreplace) %{syslog_d}/*
%attr(444,root,root) %{_pscheduler_rpmmacroprefix}*
