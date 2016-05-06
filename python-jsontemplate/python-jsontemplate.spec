#
# RPM Spec for Python isodate Module
#

%define short	jsontemplate
Name:		python-%{short}
Version:	0.87
Release:	1%{?dist}
Summary:	Template system for JSON
BuildArch:	%(uname -m)
License:	Apache 2.0
Group:		Development/Libraries

Provides:	%{name} = %{version}-%{release}
Prefix:		%{_prefix}

Vendor:		Google
Url:		https://code.google.com/archive/p/json-template

Source:		%{short}-%{version}.tar.gz

Requires:	python

BuildRequires:	python-setuptools


%description
Template system for JSON



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
