#
# RPM Spec for Python isodate Module
#

%define short	isodate
Name:		python-%{short}
Version:	0.5.4
Release:	1%{?dist}
Summary:	An ISO 8601 date/time/duration parser and formatter
BuildArch:	noarch
License:	BSD
Group:		Development/Libraries

Provides:	%{name} = %{version}-%{release}
Prefix:		%{_prefix}

Vendor:		Gerhard Weis <gerhard.weis@proclos.com>
Url:		http://cheeseshop.python.org/pypi/isodate

Source:		%{short}-%{version}.tar.gz

Requires:	python

BuildRequires:	python-setuptools

%description
This module implements ISO 8601 date, time and duration parsing. The
implementation follows ISO8601:2004 standard, and implements only
date/time representations mentioned in the standard.



# Don't do automagic post-build things.
%global              __os_install_post %{nil}


%prep
%setup -q -n %{short}-%{version}


%build
python setup.py build


%install
python setup.py install --root=$RPM_BUILD_ROOT --single-version-externally-managed -O1  --record=INSTALLED_FILES


%clean
rm -rf $RPM_BUILD_ROOT


%files -f INSTALLED_FILES
%defattr(-,root,root)
