#
# RPM Spec for Generic RPM Makefile
#

Name:		make-generic-package
Version:	2.0
Release:	1%{?dist}

Summary:	Generic Makefile for RPMs
BuildArch:	noarch
License:	Apache 2.0
Group:		Unspecified

Source0:	%{name}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}


# These two sections should be identical since the package uses its
# own code to build itself.

BuildRequires:	make
BuildRequires:	spectool

Requires:	make
Requires:	spectool

# This package's previous name
Obsoletes:	make-generic-rpm


%define directory %{_includedir}/make

%description
Generic Makefile for RPMs.  For documentation, see the Makefile in
%{directory}.


%define docdir %{_docdir}/%{name}

%prep
%setup -q


%install
%{__mkdir_p} $RPM_BUILD_ROOT/%{directory}
%{__install} -m 444 *.make $RPM_BUILD_ROOT/%{directory}

%{__mkdir_p} $RPM_BUILD_ROOT/%{docdir}
%{__install} -m 444 *.md $RPM_BUILD_ROOT/%{docdir}


%files
%defattr(-,root,root,-)
%{directory}/*
%{docdir}/*
