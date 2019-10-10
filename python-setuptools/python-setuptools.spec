#
# RPM Spec for Python isodate Module
#

%define short	setuptools
Name:		python-%{short}
Version:	40.8.0
Release:	1%{?dist}
Summary:	Easily build and distribute Python packages
BuildArch:	noarch
License:	MIT
Group:		Applications/System

Provides:	%{name} = %{version}-%{release}
Provides:	python-%{short} = %{version}-%{release}
Prefix:		%{_prefix}

Vendor:		Python Packaging Authority
URL:		http://pypi.python.org/pypi/setuptools

Source:		%{short}-%{version}.tar.gz

Requires:	python

BuildRequires:	python-setuptools



%description 
Setuptools is a collection of enhancements to the Python distutils that allow
you to more easily build and distribute Python packages, especially ones that
have dependencies on other packages.

This package contains the runtime components of setuptools, necessary to
execute the software that requires pkg_resources.py.

This package contains the distribute fork of setuptools.




# Don't do automagic post-build things.
%global              __os_install_post %{nil}


%prep
%setup -q -n %{short}-%{version}

%build
python bootstrap.py
#python setup.py build


%install
python setup.py install --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES -O1
sed -i -e 's/^/"/g; s/$/"/g' INSTALLED_FILES

%clean
rm -rf $RPM_BUILD_ROOT


%files -f INSTALLED_FILES
# %defattr(-,root,root)
