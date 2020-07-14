#
# RPM Spec for Generic RPM Makefile
#

Name:		make-generic-rpm
Version:	1.0
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


%define directory %{_includedir}/make

%description
Generic Makefile for RPMs.  For documentation, see the Makefile in
%{directory}.



%prep
%setup -q


%install
%{__mkdir_p} $RPM_BUILD_ROOT/%{directory}
%{__install} -m 444 generic-rpm.make $RPM_BUILD_ROOT/%{directory}


%files
%defattr(-,root,root,-)
%{directory}/*
