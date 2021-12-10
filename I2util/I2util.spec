%define perfsonar_auto_relnum 0.a1.0

%define perfsonar_auto_version 4.4.1
%define perfsonar_auto_relnum 0.a1.0

Name:           I2util
Version:        %{perfsonar_auto_version}
Release:        %{perfsonar_auto_relnum}%{?dist}
Summary:        I2 Utility Library
License:        ASL 2.0 
Group:          Development/Libraries
Source0:        I2util.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%description
I2 Utility library. Currently contains:
	* error logging
	* command-line parsing
	* threading
	* random number support
	* hash table support

The error logging and command-line parsing are taken from a utility library
that is distributed with the "volsh" code from UCAR.

http://www.scd.ucar.edu/vets/vg/Software/volsh


%global debug_package %{nil}


%prep
%setup -q -n "%{name}"

%build
sh ./bootstrap.sh
%configure

%install
rm -rf $RPM_BUILD_ROOT
%makeinstall

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
#%doc Changes LICENSE README
%license LICENSE
%doc README
%{_bindir}/*
%{_libdir}/libI2util.a
%{_mandir}/man1/*
%{_includedir}/*

%changelog
* Fri Aug 20 2010 Tom Throckmorton <throck@mcnc.org> 1.1-1
- minor spec changes only

* Fri Jan 11 2008 aaron@internet2.edu 1.0-1
- Initial RPM
