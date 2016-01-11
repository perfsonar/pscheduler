#
# RPM Spec for random-string
#

Name:		random-string
Version:	1.0
Release:	1%{?dist}

Summary:	Create random strings

BuildArch:	noarch
License:	Apache 2.0
Group:		Utilities/Text
Vendor:		The perfSONAR Development Team
URL:		http://www.perfsonar.net

Source0:	%{name}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

Requires:	python

%description
Random-string creates strings of random length that contain only
printable, non-whitespace characters.


%prep
%setup -q


%build
make \
     BINDIR=$RPM_BUILD_ROOT/%{_bindir} \
     MANDIR=$RPM_BUILD_ROOT/%{_mandir} \
     install


%clean
make clean


%files
%defattr(-,root,root)
%{_bindir}/*
%{_mandir}/man1/*
