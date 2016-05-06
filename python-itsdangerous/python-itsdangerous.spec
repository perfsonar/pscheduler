#
# RPM Spec for Python Itsdangerous
#

%define short	itsdangerous
Name:		python-%{short}
Version:	0.24
Release:	1%{?dist}
Summary:	JSON Signature Module
BuildArch:	noarch
License:	BSD
Group:		Development/Libraries

Provides:	%{name} = %{version}-%{release}
Prefix:		%{_prefix}

Vendor:		Armin Ronacher
URL:		http://pythonhosted.org/itsdangerous

Source:		%{short}-%{version}.tar.gz

Requires:	python

BuildRequires:	python
BuildRequires:	python-setuptools


%description
JSON signature module



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
