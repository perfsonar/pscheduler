#
# RPM Spec for pScheduler Minimal Bundle Marker
#

%define perfsonar_auto_version 5.2.0
%define perfsonar_auto_relnum 0.a1.0

Name:		pscheduler-minimal-marker
Version:	%{perfsonar_auto_version}
Release:	%{perfsonar_auto_relnum}%{?dist}

Summary:	Empty package marking the end of the pScheduler minimal bundle.
BuildArch:	noarch
License:	ASL 2.0
Vendor:		perfSONAR
Group:		Unspecified

Provides:	%{name} = %{version}-%{release}

%description
Empty package marking the end of the pScheduler minimal bundle.

%define marker_dir %{_pscheduler_sysconfdir}
%define marker_file %{marker_dir}/.%{name}

%build
mkdir -p "${RPM_BUILD_ROOT}/%{marker_dir}"
cat > "${RPM_BUILD_ROOT}/%{marker_file}" <<EOF
This file serves no function and may be ignored.
EOF


%files
%defattr(-,root,root)
%{marker_file}
