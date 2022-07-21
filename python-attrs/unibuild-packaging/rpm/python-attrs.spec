#
# RPM Spec for a Python Module
#

# DEBIAN:  This may need to be packaged for Debian

%define short	attrs
%define long	python-%{short}
Name:		%{_pscheduler_python}-%{short}
Version:	21.4.0
Release:	1%{?dist}
Summary:	Relieves the drudgery of implementing object protocols
BuildArch:	%(uname -m)
License:	MIT
Group:		Development/Libraries

Provides:	%{name} = %{version}-%{release}
Prefix:		%{_prefix}

Vendor:		Glyph <glyph@twistedmatrix.com>
Url:		https://github.com/glyph/Automat

Source:		%{short}-%{version}.tar.gz

Requires:	%{_pscheduler_python}

BuildRequires:	%{_pscheduler_python}-setuptools

%description
Attrs is the Python package that will bring back the joy of writing
classes by relieving you from the drudgery of implementing object
protocols (aka dunder methods). Trusted by NASA for Mars missions
since 2020!  Its main goal is to help you to write concise and correct
software without slowing down your code.


# Don't do automagic post-build things.
%global              __os_install_post %{nil}


%prep
%setup -q -n %{short}-%{version}



%build
%{_pscheduler_python} setup.py build


%install
%{_pscheduler_python} setup.py install \
    --root=$RPM_BUILD_ROOT \
    --single-version-externally-managed \
    -O1 \
    --record=INSTALLED_FILES


%clean
rm -rf $RPM_BUILD_ROOT


%files -f INSTALLED_FILES
%defattr(-,root,root)
