#
# RPM Spec for pScheduler Core
#

%define perfsonar_auto_version 4.3.0
%define perfsonar_auto_relnum 0.a0.0

Name:		pscheduler-core
Version:	%{perfsonar_auto_version}
Release:	%{perfsonar_auto_relnum}%{?dist}

Summary:	pScheduler Core Programs
BuildArch:	noarch
License:	ASL 2.0
Vendor:	perfSONAR
Group:		Unspecified

Source0:	%{name}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

Requires:       bash-completion
# This is for plot-schedule
Requires:       gnuplot-minimal >= 4.6.2
# This is for netstat.
Requires:       net-tools
Requires:       %{_pscheduler_python}-pscheduler >= 1.3.7.1
Requires:       pytz
Requires:	curl
Requires:       dmidecode

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
