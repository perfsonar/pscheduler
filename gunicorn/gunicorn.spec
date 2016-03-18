#
# RPM Spec for Gunicorn
#

%define short	gunicorn
Name:		%{short}
Version:	19.4.5
Release:	1%{?dist}
Summary:	Python WSGI HTTP Server for UNIX
BuildArch:	noarch
License:	MIT
Group:		System Environment/Daemons

Provides:	%{name} = %{version}-%{release}
Prefix:		%{_prefix}

Vendor:		Benoit Chesneau
Url:		http://www.gunicorn.org

Source:		%{short}-%{version}.tar.gz

# This removes a file that only works in Python 3.x and causes trouble
# for building with 2.6.
Patch0:         %{name}-00-remove-gaiohttp.patch 


BuildRequires:  python2-devel
BuildRequires:  python-setuptools
BuildRequires:  pytest

Requires:       python-setuptools


%description
Gunicorn 'Green Unicorn' is a Python WSGI HTTP Server for UNIX. It's a
pre-fork worker model ported from Ruby's Unicorn project. The Gunicorn
server is broadly compatible with various web frameworks, simply
implemented, light on server resources, and fairly speedy.



# Don't do automagic post-build things.
%global              __os_install_post %{nil}
%global		     debug_package %{nil}


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
