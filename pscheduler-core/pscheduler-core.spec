#
# RPM Spec for pScheduler Core
#

Name:		pscheduler-core
Version:	1.0
Release:	0.22.rc2%{?dist}

Summary:	pScheduler Core Programs
BuildArch:	noarch
License:	Apache 2.0
Group:		Unspecified

Source0:	%{name}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

# This is for netstat.
Requires:       net-tools
Requires:       python-pscheduler >= 1.2
Requires:       pytz
Requires:	curl

BuildRequires:	pscheduler-rpm
BuildRequires:	m4


%description
Core programs for pScheduler


%prep
%setup -q

%build
make \
     BINDIR=$RPM_BUILD_ROOT/%{_bindir} \
     COMMANDSDIR=$RPM_BUILD_ROOT/%{_pscheduler_commands} \
     COMMANDSINSTALLED=%{_pscheduler_commands} \
     CLASSESDIR=$RPM_BUILD_ROOT/%{_pscheduler_classes} \
     CLASSESINSTALLED=%{_pscheduler_classes} \
     INTERNALSDIR=$RPM_BUILD_ROOT/%{_pscheduler_internals} \
     INTERNALSINSTALLED=%{_pscheduler_internals} \
     LIMITSFILE=%{_pscheduler_limit_config} \
     TOOLCONFIGDIR=%{_pscheduler_tool_confdir} \
     install


%files
%defattr(-,root,root,-)
%{_bindir}/*
%{_pscheduler_commands}
%{_pscheduler_commands}/*
%{_pscheduler_internals}/*
