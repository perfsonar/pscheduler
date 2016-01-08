#
# RPM Spec for pScheduler RPM Macros
#

Name:		pscheduler-rpm
Version:	1.0
Release:	1%{?dist}

Summary:	Macros for use by pScheduler RPM specs
BuildArch:	noarch
License:	Apache 2.0
Group:		Unspecified

Provides:	%{name} = %{version}-%{release}

%description
Macros for use by pScheduler RPM specs


%install
%{__mkdir_p} $RPM_BUILD_ROOT/%{_sysconfdir}/rpm
cat > $RPM_BUILD_ROOT/%{_sysconfdir}/rpm/macros.%{name} <<EOF

#
# Macros used in building pScheduler RPMs  (Version %{version})
#

%%_pscheduler_libexecdir %{_libexecdir}/pscheduler
%%_pscheduler_docdir %{_defaultdocdir}/pscheduler
%%_pscheduler_datadir %{_datadir}/pscheduler

# Where all classes live
%%_pscheduler_classes %{_pscheduler_libexecdir}/classes

# Tests
%%_pscheduler_test_libexec %{_pscheduler_classes}/test
%%_pscheduler_test_doc %{_pscheduler_docdir}/test

# Tools
%%_pscheduler_tool_libexec %{_pscheduler_classes}/tool
%%_pscheduler_tool_doc %{_pscheduler_docdir}/tool

# Archivers
%%_pscheduler_archiver_libexec %{_pscheduler_classes}/archiver
%%_pscheduler_archiver_doc %{_pscheduler_docdir}/archiver

# pScheduler front-end comands
%%_pscheduler_commands %{_pscheduler_libexecdir}/commands

EOF


%files
%attr(444,root,root) %{_sysconfdir}/rpm/*
