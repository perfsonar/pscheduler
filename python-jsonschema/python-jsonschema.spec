#
# RPM Spec for Python Jsonschema
#

%define short	jsonschema
Name:		python-%{short}
Version:	2.5.1
Release:	1%{?dist}
Summary:	JSON Schema for Python
BuildArch:	noarch
License:	MIT
Group:		Development/Libraries

Provides:	%{name} = %{version}-%{release}
Prefix:		%{_prefix}

Vendor:		Julian Berman
URL:		https://github.com/Julian/jsonschema

Source:		%{short}-%{version}.tar.gz

Requires:	python
Requires:	python-argparse
Requires:	python-repoze.lru


BuildRequires:	python


%description
JSON Schema for Python



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
