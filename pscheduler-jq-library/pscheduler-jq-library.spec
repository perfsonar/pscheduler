#
# RPM Spec for pScheduler JQ Library
#

Name:		pscheduler-jq-library
Version:	1.0.2
Release:	0.3.b1%{?dist}

Summary:	Library of JQ functions for pScheduler
BuildArch:	noarch
License:	Apache 2.0
Group:		Unspecified

Source0:	%{name}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

Requires:	jq

BuildRequires:	jq

%define jq_prog	%(which jq)
%define jq_bin	%(dirname "%{jq_prog}")
%define jq_lib	%(cd "%{jq_bin}/../lib" && pwd)/jq/pscheduler


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
%{jq_lib}/*
