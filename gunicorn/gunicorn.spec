#
# RPM Spec for Gunicorn
#

%define short	gunicorn
Name:		%{short}
Version:	19.4.5
Release:	1%{?dist}
Summary:	An ISO 8601 date/time/duration parser and formatter
BuildArch:	noarch
License:	MIT
Group:		System Environment/Daemons

Provides:	%{name} = %{version}-%{release}
Prefix:		%{_prefix}

Vendor:		Benoit 
Url:		http://www.gunicorn.org

Source:		%{short}-%{version}.tar.gz

# This removes a file that only works in Python 3.x and causes trouble
# for building with 2.6.
Patch0:         %{name}-00-remove-gaiohttp.patch 


%description
This module implements ISO 8601 date, time and duration parsing. The
implementation follows ISO8601:2004 standard, and implements only
date/time representations mentioned in the standard.



# Don't do automagic post-build things.
%global              __os_install_post %{nil}
%global		     debug_package %{nil}


%prep
%setup -q -n %{short}-%{version}
%patch0 -p1


%build
python setup.py build


%install
python setup.py install --root=$RPM_BUILD_ROOT --single-version-externally-managed -O1  --record=INSTALLED_FILES


%clean
rm -rf $RPM_BUILD_ROOT


%files -f INSTALLED_FILES
%defattr(-,root,root)
