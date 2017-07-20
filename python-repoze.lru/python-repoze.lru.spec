#
# RPM Spec for repoze.lru
#

# NOTE: This package builds normally on EL6 but builds as a dummy with
# a high version number and no files on EL7.  This is to allow
# upgrades to use EPEL's version of this module (which is named
# repoze-lru) without file conflicts.


%define short	repoze.lru
Name:		python-%{short}
%if 0%{?el6}
Version:	0.6
Summary:	Python LRU cache
%else
Version:	999.9
Summary:	Python LRU cache - DUMMY VERSION
%endif
Release:	1%{?dist}

BuildArch:	noarch
License:	BSD-derived (http://www.repoze.org/LICENSE.txt)
Group:		Development/Libraries

Provides:	%{name} = %{version}-%{release}
Prefix:		%{_prefix}

Vendor:		Agendaless Consulting
URL:		http://www.repoze.org

%if 0%{?el6}
Source:		%{short}-%{version}.tar.gz

Requires:	python

BuildRequires:	python
BuildRequires:	python-setuptools
%endif


%description
Python LRU cache



# Don't do automagic post-build things.
%global              __os_install_post %{nil}


%if 0%{?el6}

%prep
%setup -q -n %{short}-%{version}


%build
python setup.py build


%install
python setup.py install --root=$RPM_BUILD_ROOT --single-version-externally-managed -O1  --record=INSTALLED_FILES


%clean
rm -rf $RPM_BUILD_ROOT

%endif


%if 0%{?el6}
%files -f INSTALLED_FILES
%defattr(-,root,root)
%else
%files
# No files.
%endif

