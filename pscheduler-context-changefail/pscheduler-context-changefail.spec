#
# RPM Spec for a pScheduler context changer
#

%define short	changefail
%define perfsonar_auto_version 4.4.0
%define perfsonar_auto_relnum 0.11.b1

Name:		pscheduler-context-%{short}
Version:	%{perfsonar_auto_version}
Release:	%{perfsonar_auto_relnum}%{?dist}

Summary:	Always-failing context changer class for pScheduler
BuildArch:	noarch
License:	ASL 2.0
Vendor:	perfSONAR
Group:		Unspecified

Source0:	%{short}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

Requires:	pscheduler-server
Requires:	%{_pscheduler_python}-pscheduler

BuildRequires:	pscheduler-rpm >= 1.0.0.5.1


%define directory %{_includedir}/make

%description
Always-failing context changer class for pScheduler


%prep
%setup -q -n %{short}-%{version}


%define dest %{_pscheduler_context_libexec}/%{short}

%build
make \
     DESTDIR=$RPM_BUILD_ROOT/%{dest} \
     install


%post
pscheduler internal warmboot

%postun
pscheduler internal warmboot


%files
%defattr(-,root,root,-)
%license LICENSE
%{dest}
