#
# RPM Spec for Python isodate Module
#

%define short	subprocess32
Name:		python-%{short}
Version:	3.2.7
Release:	1%{?dist}
Summary:	Backport of Python 3.2's subprocess for Python 2.x
BuildArch:	%(uname -m)
License:	PSF
Group:		Development/Libraries

Provides:	%{name} = %{version}-%{release}
Prefix:		%{_prefix}

Vendor:		Gregory P. Smith <greg@krypto.org>
Url:		https://github.com/google/python-subprocess32

Source:		%{short}-%{version}.tar.gz


%description
Backport of Python 3.2's subprocess for Python 2.x



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
