#
# RPM Spec for Python Module
#

%define short	jsonschema
Name:		%{_pscheduler_python}-%{short}
Version:	3.0.1
Release:	1%{?dist}
Summary:	JSON Schema library for Python
BuildArch:	%(uname -m)
License:	MIT
Group:		Development/Libraries

Provides:	%{name} = %{version}-%{release}
Provides:	python-%{short} = %{version}-%{release}
Provides:	%{_pscheduler_python}-%{short} = %{version}-%{release}
Prefix:		%{_prefix}

Vendor:		Julian Berman
URL:		http://pypi.python.org/pypi/jsonschema

Source:		%{short}-%{version}.tar.gz

Requires:       %{_pscheduler_python}
Requires:       %{_pscheduler_python_epel}-attrs
Requires:       %{_pscheduler_python}-pyrsistent
# This is required for some reason.
Requires:       %{_pscheduler_python}-setuptools

BuildRequires:  %{_pscheduler_python}
BuildRequires:  %{_pscheduler_python}-setuptools

%description
JSON Schema library for Python



# Don't do automagic post-build things.
%global              __os_install_post %{nil}
%global		     debug_package %{nil}


%prep
%setup -q -n %{short}-%{version}


%build
%{_pscheduler_python} setup.py build


%install
%{_pscheduler_python} setup.py install --root=$RPM_BUILD_ROOT -O1  --record=INSTALLED_FILES


%clean
rm -rf $RPM_BUILD_ROOT


%files -f INSTALLED_FILES
%defattr(-,root,root)
