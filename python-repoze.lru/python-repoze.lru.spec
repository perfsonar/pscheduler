#
# RPM Spec for repoze.lru
#

%define short	repoze.lru
Name:		python-%{short}
Version:	0.6
Release:	1%{?dist}
Summary:	Python LRU cache
BuildArch:	noarch
License:	BSD-derived (http://www.repoze.org/LICENSE.txt)
Group:		Development/Libraries

Provides:	%{name} = %{version}-%{release}
Prefix:		%{_prefix}

Vendor:		Agendaless Consulting
URL:		http://www.repoze.org

Source:		%{short}-%{version}.tar.gz

Requires:	python

BuildRequires:	python
BuildRequires:	python-setuptools


%description
Python LRU cache



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
