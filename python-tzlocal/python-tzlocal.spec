#
# RPM Spec for Python isodate Module
#

%define short	tzlocal
Name:		python-%{short}
Version:	1.2.2
Release:	1%{?dist}
Summary:	Local timezone information for Python
BuildArch:	noarch
License:	CC0 1.0 Universal
Group:		Development/Libraries

Provides:	%{name} = %{version}-%{release}
Prefix:		%{_prefix}

Vendor:		Lennart Regebro
Url:		https://github.com/regebro/tzlocal

Source:		%{short}-%{version}.tar.gz

BuildRequires:	python

Requires:	python


%description
This Python module returns a tzinfo object with the local timezone
information under Unix and Win-32.



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
