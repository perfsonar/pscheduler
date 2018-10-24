#
# RPM Spec for pScheduler Core
#

Name:		pscheduler-core
Version:	1.1.2
Release:	1%{?dist}

Summary:	pScheduler Core Programs
BuildArch:	noarch
License:	ASL 2.0
Vendor:	perfSONAR
Group:		Unspecified

Source0:	%{name}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

Requires:       bash-completion
# This is for plot-schedule
Requires:       gnuplot-minimal
# This is for netstat.
Requires:       net-tools
Requires:       python-pscheduler >= 1.3.0.4.2
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
     BASHCOMPDIR=$RPM_BUILD_ROOT/%{_datarootdir}/bash-completion/completions \
     install


%files
%defattr(-,root,root,-)
%license LICENSE
%{_bindir}/*
%{_datarootdir}/*
%{_pscheduler_commands}
%{_pscheduler_commands}/*
%{_pscheduler_internals}/*
