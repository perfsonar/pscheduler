#
# RPM spec for iperf3
#
# Adpated from ESNet's original
#

Name:	iperf3
Version: 3.16
Release:	1%{?dist}
Summary: Measurement tool for TCP/UDP bandwidth performance

Group:	 Applications/Internet
License: BSD
URL:	 https://github.com/esnet/iperf
Source0: %{name}-%{version}.tar.gz

BuildRequires: autoconf
BuildRequires: gcc
BuildRequires: openssl-devel


%description
iperf3 is a tool for active measurements of the maximum achievable
bandwidth between two IP hosts.  It supports tuning of various
parameters related to timing, protocols, and buffers.  For each test,
it reports the throughput, loss, and other parameters.

%package        devel
Summary:        Development files for %{name}
Group:          Development/Libraries

%description    devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.

%prep
%setup -q -n iperf-%{version}

%build
%configure
make %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT
%makeinstall -C src INSTALL_DIR="%{buildroot}%{_bindir}"
mkdir -p %{buildroot}%{_mandir}/man1

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%%doc README.md INSTALL LICENSE
%{_mandir}/man1/iperf3.1.gz
%{_mandir}/man3/libiperf.3.gz
%{_bindir}/iperf3
%{_libdir}/*.so.*

%files devel
%defattr(-,root,root,-)
%{_includedir}/iperf_api.h
%{_libdir}/libiperf.a
%{_libdir}/libiperf.la
%{_libdir}/*.so
%{_libdir}/*.so.*
