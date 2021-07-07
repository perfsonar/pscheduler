#
# RPM Spec for pScheduler JQ Library
#

%define perfsonar_auto_version 4.4.0
%define perfsonar_auto_relnum 1

Name:		pscheduler-jq-library
Version:	%{perfsonar_auto_version}
Release:	%{perfsonar_auto_relnum}%{?dist}

Summary:	Library of JQ functions for pScheduler
BuildArch:	noarch
License:	ASL 2.0
Vendor:	perfSONAR
Group:		Unspecified

Source0:	%{name}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

Requires:	jq

BuildRequires:	jq

# The false here allows for tidy cleanups when jq isn't installed.
%define jq_prog	%(which jq 2>/dev/null || echo /bin/false)
%define jq_bin	%(dirname "%{jq_prog}")
%define jq_lib	%(cd "%{jq_bin}/../lib" 2>/dev/null || true && pwd)/jq/pscheduler

%description
Library of JQ functions for pScheduler


%prep
%setup -q


%build
make \
     DESTDIR=$RPM_BUILD_ROOT/%{jq_lib} \
     install

%files
%defattr(-,root,root,-)
%license LICENSE
%{jq_lib}/*
