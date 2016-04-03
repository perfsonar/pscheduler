#
# RPM Spec for rpm-with-deps
#

Name:		rpm-with-deps
Version:	1.0
Release:	1%{?dist}

Summary:	Install RPMs and dependencies

BuildArch:	noarch
License:	Apache 2.0
Group:		Utilities/Text
Vendor:		perfSONAR Development Team
URL:		http://www.perfsonar.net

Source0:	%{name}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

Requires:	bash

%description


%prep
%setup -q


%install
make \
    BINDIR=$RPM_BUILD_ROOT/%{_bindir} \
    MANDIR=$RPM_BUILD_ROOT/%{_mandir}/man1 \
    install


%files
%defattr(-,root,root)
%{_bindir}/*
%{_mandir}/man1/*
