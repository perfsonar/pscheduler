#
# RPM Spec for rsyslog debug configuration
#

Name:		rsyslog-debug
Version:	1.0
Release:	1%{?dist}

Summary:	Debug configuration for rsyslog
BuildArch:	noarch

License:	Apache 2.0
Group:		Unspecified

# No Source

Provides:	%{name} = %{version}-%{release}

Requires:	rsyslog

%description
Debug configuration for rsyslog.


%define rsyslog_d %{_sysconfdir}/rsyslog.d


%prep
%if 0%{?el6}%{?el7} == 0
echo "This package cannot be built for %{dist}."
false
%endif


%install
mkdir -p $RPM_BUILD_ROOT/%{rsyslog_d}
cat > $RPM_BUILD_ROOT/%{rsyslog_d}/%{name}.conf <<EOF
#
# Debug
#
*.debug		%{_var}/log/messages
EOF


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


%files
%defattr(-,root,root,-)
%{rsyslog_d}/*
