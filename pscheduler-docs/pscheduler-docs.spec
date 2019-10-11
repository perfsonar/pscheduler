#
# RPM Spec for pScheduler Docs
#

%define perfsonar_auto_version 4.2.2
%define perfsonar_auto_relnum 1

Name:		pscheduler-docs
Version:	%{perfsonar_auto_version}
Release:	%{perfsonar_auto_relnum}%{?dist}

Summary:	pScheduler documentation and samples

BuildArch:	noarch
License:	ASL 2.0
Group:		Unspecified
Vendor:		perfSONAR
URL:		http://www.perfsonar.net

Source0:	%{name}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

BuildRequires:	pscheduler-rpm
# This is for the 'validate-limits' command.
BuildRequires:	pscheduler-core

%description
pScheduler documentation and sample configuration files 


%prep
%setup -q


%build
make \
     DOCDIR=$RPM_BUILD_ROOT/%{_pscheduler_docdir}

make \
     DOCDIR=$RPM_BUILD_ROOT/%{_pscheduler_docdir} \
     install


%clean
make clean


%files
%defattr(-,root,root)
%license LICENSE
%{_pscheduler_docdir}/*

