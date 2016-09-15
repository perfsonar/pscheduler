#
# RPM Spec for drop-in
#

Name:		drop-in
Version:	1.2
Release:	1%{?dist}

Summary:	Drop and add blocks of text in files

BuildArch:	noarch
License:	Apache 2.0
Group:		Utilities/Text
Vendor:		Mark Feit <mfeit@notonthe.net>
URL:		https://github.com/markfeit/drop-in

Source0:	%{name}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

Requires:	perl >= 5.0

%description
Drop-in adds, replaces or removes blocks of text in text files.  This
is useful for maintaining configurations that are in a single file
instead of a Red Hat .d-style directory.


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
