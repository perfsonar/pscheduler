#
# RPM Spec for Python Detach Module
#

%define short	detach
Name:		python-%{short}
Version:	1.0
Release:	1%{?dist}
Summary:	Fork and detach the current processe.
BuildArch:	noarch
License:	BSD-derived
Group:		Development/Libraries

Provides:	%{name} = %{version}-%{release}
Prefix:		%{_prefix}

Vendor:		Ryan Bourgeois <bluedragonx@gmail.com>
Url:		https://github.com/bluedragonx/detach

Source:		%{short}-%{version}.tar.gz

# This patch removes the prerequisites for testing
Patch0:		%{name}-00-no-nose.patch

BuildRequires:	python-setuptools

%description
Python module which cleanly forks a child and detaches it.


# Don't do automagic post-build things.
%global              __os_install_post %{nil}


%prep
%setup -q -n %{short}-%{version}
%patch0 -p1


%build
python setup.py build


%install
python setup.py install --root=$RPM_BUILD_ROOT --single-version-externally-managed -O1  --record=INSTALLED_FILES


%clean
rm -rf $RPM_BUILD_ROOT


%files -f INSTALLED_FILES
%defattr(-,root,root)
