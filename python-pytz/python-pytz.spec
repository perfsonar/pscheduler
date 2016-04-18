#
# RPM Spec for Python isodate Module
#

%define short	pytz
Name:		python-%{short}
Version:	2016.3
Release:	1%{?dist}
Summary:	Olson timezone database for Python
BuildArch:	noarch
License:	MIT
Group:		Development/Libraries

Provides:	%{name} = %{version}-%{release}
Prefix:		%{_prefix}

Vendor:		Stuart Bishop <stuart@stuartbishop.net>
Url:		https://pypi.python.org/pypi/pytz

Source:		%{short}-%{version}.tar.gz

BuildRequires:	python

Requires:	python


%description
Olson timezone database for Python



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
