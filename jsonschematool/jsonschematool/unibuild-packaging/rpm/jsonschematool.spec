#
# RPM Spec for jsonschematool
#

Name:		jsonschematool
Version:	1.0
Release:	1%{?dist}

Summary:	Tool for manipulating JSONSchema files

BuildArch:	noarch
License:	Apache 2.0
Group:		Unspecified
Vendor:		perfSONAR Development Team
URL:		http://www.perfsonar.net

Source0:	%{name}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

Requires:	python > 3.5

BuildRequires:	make

%description
Tool for manipulating JSONSchema files


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
