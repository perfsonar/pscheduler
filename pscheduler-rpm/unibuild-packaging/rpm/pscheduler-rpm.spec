#
# RPM Spec for pScheduler RPM Macros
#

%define perfsonar_auto_version 5.1.0
%define perfsonar_auto_relnum 0.b1.5

Name:		pscheduler-rpm
Version:	%{perfsonar_auto_version}
Release:	%{perfsonar_auto_relnum}%{?dist}

Summary:	Macros for use by pScheduler RPM specs
BuildArch:	noarch
License:	ASL 2.0
Vendor:	perfSONAR
Group:		Unspecified

Provides:	%{name} = %{version}-%{release}

%description
Macros for use by pScheduler RPM specs

# Where macros live
%define macro_dir %{_sysconfdir}/rpm
%define macro_prefix %{macro_dir}/macros.

# No punctuation between these is intentional.
%define macro_file %{macro_prefix}%{name}

%install
%{__mkdir_p} $RPM_BUILD_ROOT/%{macro_dir}
cat > $RPM_BUILD_ROOT/%{macro_prefix}%{name} <<EOF
#
# Macros used in building pScheduler RPMs  (Version %{version})
#



#
# Python
#

# This is the version we like.
%%_pscheduler_python_version_major 3

%if 0%{?el7}
%%error EL7 is no longer supported.  Try something newer.
%endif

%if 0%{?el8}%{?ol8}
# EL8 standardized on just the major version, as did EPEL.
%%_pscheduler_python python%%{_pscheduler_python_version_major}
%%_pscheduler_python_epel python%%{_pscheduler_python_version_major}

%else

# EL9+ has everyting as just plain python
%%_pscheduler_python python
%%_pscheduler_python_epel python

%endif


#
# PostgreSQL
#

# Minimum-required PostgreSQL version.
%%_pscheduler_postgresql_version_major 10
%%_pscheduler_postgresql_version_minor 17

%%_pscheduler_postgresql_version %%{_pscheduler_postgresql_version_major}.%%{_pscheduler_postgresql_version_minor}
%%_pscheduler_postgresql_data %%{_sharedstatedir}/pgsql/data


#
# pScheduler
#

%%_pscheduler_libexecdir %%{_libexecdir}/pscheduler
%%_pscheduler_sysconfdir %%{_sysconfdir}/pscheduler
%%_pscheduler_sudoersdir %%{_sysconfdir}/sudoers.d
%%_pscheduler_docdir %%{_defaultdocdir}/pscheduler
%%_pscheduler_datadir %%{_datadir}/pscheduler
%%_pscheduler_vardir %%{_var}/lib/pscheduler

# Where RPM Macros live
%%_pscheduler_rpmmacrodir %{macro_dir}
# Prefix for all macro files.  Use as %{_pscheduler_rpmmacroprefix}foo
%%_pscheduler_rpmmacroprefix %{macro_prefix}

# Internal commands
%%_pscheduler_internals %%{_pscheduler_libexecdir}/internals

# Where all classes live
%%_pscheduler_classes %%{_pscheduler_libexecdir}/classes

# Tests
%%_pscheduler_test_libexec %%{_pscheduler_classes}/test
%%_pscheduler_test_doc %%{_pscheduler_docdir}/test
%%_pscheduler_test_confdir %%{_pscheduler_sysconfdir}/test

# Tools
%%_pscheduler_tool_libexec %%{_pscheduler_classes}/tool
%%_pscheduler_tool_doc %%{_pscheduler_docdir}/tool
%%_pscheduler_tool_confdir %%{_pscheduler_sysconfdir}/tool
%%_pscheduler_tool_vardir %%{_pscheduler_vardir}/tool

# Archivers
%%_pscheduler_archiver_libexec %%{_pscheduler_classes}/archiver
%%_pscheduler_archiver_doc %%{_pscheduler_docdir}/archiver

# Context Changers
%%_pscheduler_context_libexec %%{_pscheduler_classes}/context
%%_pscheduler_context_doc %%{_pscheduler_docdir}/context

# pScheduler front-end comands
%%_pscheduler_commands %%{_pscheduler_libexecdir}/commands

# pScheduler daemons
%%_pscheduler_daemons %%{_pscheduler_libexecdir}/daemons

EOF


%files
%attr(444,root,root) %{macro_prefix}*
