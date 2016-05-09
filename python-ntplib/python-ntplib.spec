#
# RPM Spec for Python isodate Module
#

%define short	ntplib
Name:		python-%{short}
Version:	0.3.3
Release:	1%{?dist}
Summary:	Python library for querying NTP
BuildArch:	noarch
License:	MIT
Group:		Development/Libraries

Provides:	%{name} = %{version}-%{release}
Prefix:		%{_prefix}

Vendor:		Charles-Francois Natali
Url:		https://pypi.python.org/pypi/ntplib

Source:		%{short}-%{version}.tar.gz

Requires:	python

BuildRequires:	python-setuptools



%description 
This module offers a simple interface to query NTP servers from
Python.




# Don't do automagic post-build things.
%global              __os_install_post %{nil}


%prep
%setup -q -n %{short}-%{version}


%build
python setup.py build


%install
python setup.py install --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES -O1


%clean
rm -rf $RPM_BUILD_ROOT


%files -f INSTALLED_FILES
%defattr(-,root,root)
