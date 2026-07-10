#
# RPM Spec for pscheduler-json-dictionary
#

%define perfsonar_auto_version 5.3.0
%define perfsonar_auto_relnum 0.a1.0

Name:		pscheduler-json-dictionary
Version:	%{perfsonar_auto_version}
Release:	%{perfsonar_auto_relnum}%{?dist}

Summary:	JSON dictionary for pScheduler

BuildArch:	noarch
License:	Apache 2.0
Group:		Unspecified
Vendor:		perfSONAR Development Team
URL:		http://www.perfsonar.net

Source0:	%{name}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

# Requires:	Nothing...

BuildRequires:	pscheduler-rpm
BuildRequires:	%{_pscheduler_python}-jsonschema

%description
JSON dictionary used for validating pScheduler data plus
an internal command to retrieve it.


%prep
%setup -q


%build
make \
     INTERNALSDIR=$RPM_BUILD_ROOT/%{_pscheduler_internals} \
     DATADIR=%{_pscheduler_datadir} \
     INSTALLED_DATADIR=$RPM_BUILD_ROOT/%{_pscheduler_datadir} \
     install


%clean
make clean


%files
%defattr(-,root,root)
%{_pscheduler_internals}/*
%{_pscheduler_datadir}/*
