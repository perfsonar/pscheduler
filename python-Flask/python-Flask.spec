#
# RPM Spec for Dummy Python Flask
#

%define short	Flask
Name:		python-%{short}
Version:	0.11.1
Release:	1%{?dist}
Summary:	Dummy package
BuildArch:	noarch
License:	Apache 2.0
Group:		Development/Libraries

Provides:	%{name} = %{version}-%{release}
Prefix:		%{_prefix}

Vendor:		The perfSONAR development team
URL:		http://www.perfsonar.net

# No sources.
#Source:		%{short}-%{version}.tar.gz


%description
This is a dummy package which installs no files and will be removed
prior to general relase.


%files
# No files.
