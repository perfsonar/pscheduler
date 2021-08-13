#
# RPM Spec for Python Module
#

%define short   vine
Name:           %{_pscheduler_python}-%{short}
Version:        5.0.0
Release:        1%{?dist}
Summary:        A pure Python library implementing promises
BuildArch:      noarch
License:        BSD 3-Clause
Group:          Development/Libraries

Provides:       %{name} = %{version}-%{release}
Prefix:         %{_prefix}

Vendor:         The Celery Project
Url:            https://docs.celeryproject.org/projects/amqp/en/latest/

Source:         %{short}-%{version}.tar.gz

Requires:       %{_pscheduler_python}

BuildRequires:  %{_pscheduler_python}-setuptools

%description
A pure Python library implementing promises


# Don't do automagic post-build things.
%global              __os_install_post %{nil}


%prep
%setup -q -n %{short}-%{version}


%build
%{_pscheduler_python} setup.py build


%install
%{_pscheduler_python} setup.py install --root=$RPM_BUILD_ROOT --single-version-externally-managed -O1  --record=INSTALLED_FILES


%clean
rm -rf $RPM_BUILD_ROOT


%files -f INSTALLED_FILES
%defattr(-,root,root)
