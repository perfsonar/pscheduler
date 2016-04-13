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

%install
mkdir -p $RPM_BUILD_ROOT/%{rsyslog_d}
cat > $RPM_BUILD_ROOT/%{rsyslog_d}/%{name}.conf <<EOF
#
# Debug
#
*.debug		%{_var}/log/messages
EOF


%post
service rsyslog restart


%postun
service rsyslog restart


%files
%defattr(-,root,root,-)
%{rsyslog_d}/*
