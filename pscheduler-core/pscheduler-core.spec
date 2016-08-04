#
# RPM Spec for pScheduler Core
#

Name:		pscheduler-core
Version:	0.0
Release:	1%{?dist}

Summary:	pScheduler Core Programs
BuildArch:	noarch
License:	Apache 2.0
Group:		Unspecified

Source0:	%{name}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

BuildRequires:	pscheduler-rpm
BuildRequires:	m4


%description
Core programs for pScheduler


%prep
%setup -q

%define profile_d %{_sysconfdir}/profile.d

%build
make \
     BINDIR=$RPM_BUILD_ROOT/%{_bindir} \
     COMMANDSDIR=$RPM_BUILD_ROOT/%{_pscheduler_commands} \
     COMMANDSINSTALLED=%{_pscheduler_commands} \
     PROFILEDDIR=$RPM_BUILD_ROOT/%{profile_d} \
     install


%files
%defattr(-,root,root,-)
%{_bindir}/*
%{_pscheduler_commands}
%{_pscheduler_commands}/*
%{profile_d}/*
