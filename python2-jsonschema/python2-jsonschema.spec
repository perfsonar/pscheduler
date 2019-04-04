#
# RPM Spec for Python Module
#

%define short	jsonschema
Name:		python2-%{short}
Version:	3.0.1
Release:	1%{?dist}
Summary:	JSON Schema library for Python
BuildArch:	%(uname -m)
License:	MIT
Group:		Development/Libraries

Provides:	%{name} = %{version}-%{release}
Provides:	python-%{short} = %{version}-%{release}
Prefix:		%{_prefix}

Vendor:		Julian Berman
URL:		http://pypi.python.org/pypi/jsonschema

Source:		%{short}-%{version}.tar.gz

Requires:       python
Requires:       python2-attrs
Requires:       python-pyrsistent
Requires:       python-functools32


BuildRequires:  python
BuildRequires:  python-setuptools

%description
JSON Schema library for Python



# Don't do automagic post-build things.
%global              __os_install_post %{nil}
%global		     debug_package %{nil}


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
