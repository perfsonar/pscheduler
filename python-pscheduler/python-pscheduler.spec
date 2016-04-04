#
# RPM Spec for Python pScheduler Module
#

%define short	pscheduler
Name:		python-%{short}
Version:	0.1
Release:	1%{?dist}
Summary:	Utility functions for pScheduler
BuildArch:	noarch
License:	Apache 2.0
Group:		Development/Libraries

Provides:	%{name} = %{version}-%{release}
Prefix:		%{_prefix}

Vendor:		The perfSONAR Development Team
Url:		http://www.perfsonar.net

Source0:	%{short}-%{version}.tar.gz

Requires:	python-dateutil
Requires:	python-detach
Requires:	python-isodate
Requires:	python-psycopg2
Requires:	python-subprocess32


%description
Utility functions for pScheduler


# Don't do automagic post-build things.
%global              __os_install_post %{nil}


%prep
%setup -q -n %{short}-%{version}


%build
python setup.py build


%install
python setup.py install --root=$RPM_BUILD_ROOT -O1  --record=INSTALLED_FILES


%clean
rm -rf $RPM_BUILD_ROOT


%files -f INSTALLED_FILES
%defattr(-,root,root)
