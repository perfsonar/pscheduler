#
# RPM Spec for Python Itsdangerous
#

%define short	itsdangerous
Name:		%{_pscheduler_python}-%{short}
Version:	2.2.0
Release:	1%{?dist}
Summary:	JSON Signature Module
BuildArch:	noarch
License:	BSD
Group:		Development/Libraries

Provides:	%{name} = %{version}-%{release}
Prefix:		%{_prefix}

Vendor:		Pallets Projects
URL:		https://palletsprojects.com/p/itsdangerous

Source:		%{short}-%{version}.tar.gz

Requires:	%{_pscheduler_python}

BuildRequires:	%{_pscheduler_python}-devel
# TODO: See if -devel pulls this in on OL8
BuildRequires:	pyproject-rpm-macros
BuildRequires:	%{_pscheduler_python}-flit-core

%generate_buildrequires
%pyproject_buildrequires


%description
JSON signature module


# Don't do automagic post-build things.
%global              __os_install_post %{nil}


%prep
%setup -q -n %{short}-%{version}


%build
%pyproject_wheel


%install
%pyproject_install
%pyproject_save_files '*'


%check
%pyproject_check_import


%clean
rm -rf $RPM_BUILD_ROOT


%files -f %{pyproject_files}
%defattr(-,root,root)
