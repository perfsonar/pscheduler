#
# RPM Spec for pScheduler Core
#

%define perfsonar_auto_version 4.4.0
%define perfsonar_auto_relnum 0.10.b1

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
%if 0%{?el7}
Requires:       gnuplot-minimal >= 4.6.2
%endif
%if 0%{?el8}
Requires:       gnuplot >= 4.6.2
%endif

# This is for netstat.
Requires:       net-tools
Requires:       %{_pscheduler_python}-pscheduler >= 4.4.0
%if 0%{?el7}
Requires:       pytz
%endif
%if 0%{?el8}
Requires:       %{_pscheduler_python}-pytz
%endif

Requires:	curl
Requires:       dmidecode
Requires:       lsof

BuildRequires:	pscheduler-rpm
BuildRequires:	m4


%description
Core programs for pScheduler


%prep
%setup -q

%build
make \
     ARCHIVEDEFAULTDIR=%{_pscheduler_archiver_default_dir} \
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
