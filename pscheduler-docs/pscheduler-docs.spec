#
# RPM Spec for pScheduler Docs
#

Name:		pscheduler-docs
Version:	1.1
Release:	1%{?dist}

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

