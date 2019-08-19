#
# RPM Spec for Python kafka-python Module
#

%define short   kafka
Name:           python-%{short}
Version:        1.4.6
Release:        1%{?dist}
Summary:        A pure Python library for Apache Kafka
BuildArch:      noarch
License:        BSD
Group:          Development/Libraries

Provides:       %{name} = %{version}-%{release}
Prefix:         %{_prefix}

Vendor:         Dana Powers <dana.powers@gmail.com>
Url:            https://pypi.org/project/kafka-python/#files

Source:         %{short}-python-%{version}.tar.gz

Requires:       python


BuildRequires:  python-setuptools

%description
This module implements Apache Kafka producers and consumers in pure python, which can be used to interact with a pre existing Apache Kafka message bus.



# Don't do automagic post-build things.
%global              __os_install_post %{nil}


%prep
%setup -q -n %{short}-python-%{version}


%build
python setup.py build


%install
python setup.py install --root=$RPM_BUILD_ROOT --single-version-externally-managed -O1  --record=INSTALLED_FILES


%clean
rm -rf $RPM_BUILD_ROOT


%files -f INSTALLED_FILES
%defattr(-,root,root)
