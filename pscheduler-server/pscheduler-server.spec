#
# RPM Spec for pScheduler Server
#

# TODO: Need to write proper systemd services for this package and
# make the scriptlets use them on CentOS 7.  For now the old-style
# init scripts function just fine.

%define perfsonar_auto_version 4.4.1
%define perfsonar_auto_relnum 0.a1.0

Name:		pscheduler-server
Version:	%{perfsonar_auto_version}
Release:	%{perfsonar_auto_relnum}%{?dist}

Summary:	pScheduler Server
BuildArch:	noarch
License:	ASL 2.0
Vendor:	perfSONAR
Group:		Unspecified

Source0:	%{name}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}


# Database

# NOTE: postgresql-init must be maintained to require the same set of
# PostgreSQL packages so upgrades between versions will work.  See
# comments there for more information.

BuildRequires:	postgresql-init >= %{_pscheduler_postgresql_version}
BuildRequires:	postgresql-load >= 1.2
BuildRequires:	%{_pscheduler_postgresql_package}-server >= %{_pscheduler_postgresql_version}
BuildRequires:	%{_pscheduler_postgresql_package}-contrib >= %{_pscheduler_postgresql_version}
BuildRequires:	%{_pscheduler_postgresql_package}-plpython3 >= %{_pscheduler_postgresql_version}

Requires:	drop-in
Requires:	gzip
Requires:	%{_pscheduler_postgresql_package}-server >= %{_pscheduler_postgresql_version}
# This is for pgcrypto
Requires:	%{_pscheduler_postgresql_package}-contrib >= %{_pscheduler_postgresql_version}
Requires:	%{_pscheduler_postgresql_package}-plpython3 >= %{_pscheduler_postgresql_version}
Requires:	postgresql-load >= 1.2
Requires:	pscheduler-account
Requires:	pscheduler-core
Requires:	postgresql-init
Requires:	random-string >= 1.1

# Daemons
BuildRequires:	m4
Requires:	curl
Requires:	pscheduler-account
# This is from EPEL but doesn't have a python36 prefix
Requires:	%{_pscheduler_python}-daemon
Requires:	%{_pscheduler_python}-flask
Requires:	%{_pscheduler_python}-jsontemplate

# API Server
BuildRequires:	pscheduler-account
BuildRequires:	pscheduler-rpm
BuildRequires:	%{_pscheduler_python}-parse-crontab
BuildRequires:	%{_pscheduler_python}-pscheduler >= 4.4.0
BuildRequires:	m4
Requires:	httpd-wsgi-socket
Requires:	pscheduler-server
# Note that the actual definition of what protocol is used is part of
# python-pscheduler, but this package is what does the serving, so
# mod_ssl is required here.
Requires:	mod_ssl
Requires:	mod_wsgi > 4.0
Requires:	%{_pscheduler_python}-parse-crontab
Requires:	%{_pscheduler_python}-pscheduler >= 4.3.0

%if 0%{?el7}
Requires:	pytz
%endif
%if 0%{?el8}
Requires:	%{_pscheduler_python}-pytz
%endif

# General
BuildRequires:	pscheduler-rpm
BuildRequires:	systemd
%{?systemd_requires: %systemd_requires}


%description
The pScheduler server


# Database

%define daemon_config_dir %{_pscheduler_sysconfdir}/daemons
%define db_config_dir %{_pscheduler_sysconfdir}/database
%define db_user %{_pscheduler_user}
%define password_file %{db_config_dir}/database-password
%define database_name %{db_user}
%define dsn_file %{db_config_dir}/database-dsn
%define pgpass_file %{db_config_dir}/pgpassfile
%define default_archives %{_pscheduler_sysconfdir}/archives
%define rpm_macros %{_pscheduler_rpmmacroprefix}%{name}

%define configurables_file %{_pscheduler_sysconfdir}/configurables.conf

# Daemons
%define archiver_default_dir %{_pscheduler_sysconfdir}/default-archives

# API Server
%define httpd_conf_d   %{_sysconfdir}/httpd/conf.d
%define api_httpd_conf %{httpd_conf_d}/pscheduler-api-server.conf
# TODO: It would be nice if we had a way to automatically find this.
%define apache_user    apache
%define apache_group   apache

%define server_conf_dir %{_pscheduler_sysconfdir}
# Runtime space for PID files and debug flags.
%define run_dir  %{_rundir}/%{name}

# Note that we want this here because it seems to work well without
# assistance on systems where selinux is enabled.  Anywhere else and
# there'd have to be a 'chcon -R -t httpd_user_content_t'.
%define api_dir	     %{_var}/www/%{name}

# Utilities

# (Nothing here.)


# ------------------------------------------------------------------------------

%prep

%if 0%{?el7}%{?el8} == 0
echo "This package cannot be built for %{dist}."
false
%endif
%setup -q


# ------------------------------------------------------------------------------

%build

#
# Database
#
make -C database \
     CHECK_SYNTAX=1 \
     DATABASE=%{db_user} \
     DATADIR=%{_pscheduler_datadir} \
     PASSWORDFILE=%{password_file} \
     DSNFILE=%{dsn_file} \
     PGPASSFILE=%{pgpass_file} \
     ROLE=%{db_user} \
     PGPASSFILE=$RPM_BULID_ROOT/%{pgpass_file}

#
# Daemons
#
make -C daemons \
     CONFIGDIR=%{daemon_config_dir} \
     DAEMONDIR=%{_pscheduler_daemons} \
     DSNFILE=%{dsn_file} \
     LOGDIR=%{_pscheduler_log_dir} \
     PGDATABASE=%{database_name} \
     PGPASSFILE=%{_pscheduler_database_pgpass_file} \
     PGSERVICE=%{_pscheduler_postgresql_service}.service \
     PGUSER=%{_pscheduler_database_user} \
     PSUSER=%{_pscheduler_user} \
     ARCHIVERDEFAULTDIR=%{archiver_default_dir} \
     RUNDIR=%{run_dir} \
     VAR=%{_var}

#
# API Server
#
# (Nothing)


#
# Utilities
#

make -C utilities \
    "CONFIGDIR=%{_pscheduler_sysconfdir}" \
    "CONFIGURABLESFILE=%{configurables_file}" \
    "LIMITSFILE=%{_pscheduler_limit_config}" \
    "LOGDIR=%{_pscheduler_log_dir}" \
    "LOGFILE=%{_pscheduler_log_file}" \
    "PGDATABASE=%{database_name}" \
    "PGPASSFILE=%{pgpass_file}" \
    "TMPDIR=%{_tmppath}" \
    "VERSION=%{version}"



# ------------------------------------------------------------------------------

%install

#
# Database
#
make -C database \
     DATADIR=$RPM_BUILD_ROOT/%{_pscheduler_datadir} \
     INTERNALSDIR=$RPM_BUILD_ROOT/%{_pscheduler_internals} \
     install

mkdir -p $RPM_BUILD_ROOT/%{db_config_dir}

# These will be populated on installation
for FILE in %{password_file} %{dsn_file} %{pgpass_file}
do
    DIR=$(dirname "$RPM_BUILD_ROOT/${FILE}")
    mkdir -p "${DIR}"
    touch "$RPM_BUILD_ROOT/${FILE}"
    chmod 440 "$RPM_BUILD_ROOT/${FILE}"
done

# RPM Macros
mkdir -p $(dirname $RPM_BUILD_ROOT/%{rpm_macros})
cat > $RPM_BUILD_ROOT/%{rpm_macros} <<EOF
# %{name} %{version}

# Archiver
%%_pscheduler_archiver_default_dir %{archiver_default_dir}

# Database
%%_pscheduler_database_user %{db_user}
%%_pscheduler_database_name %{db_user}
%%_pscheduler_database_dsn_file %{dsn_file}
%%_pscheduler_database_password_file %{password_file}
%%_pscheduler_database_pgpass_file %{pgpass_file}
EOF

%define profile_d %{_sysconfdir}/profile.d

# Shell Aliases
mkdir -p $RPM_BUILD_ROOT/%{profile_d}
cat > $RPM_BUILD_ROOT/%{profile_d}/%{name}.sh <<EOF
alias pssql='PGPASSFILE=%{pgpass_file} psql -U pscheduler'
EOF
cat > $RPM_BUILD_ROOT/%{profile_d}/%{name}.csh <<EOF
alias pssql 'setenv PGPASSFILE "%{pgpass_file}" && psql -U pscheduler'
EOF

#
# Daemons
#
make -C daemons \
     CONFIGDIR=$RPM_BUILD_ROOT/%{daemon_config_dir} \
     UNITDIR=$RPM_BUILD_ROOT/%{_unitdir} \
     DAEMONDIR=$RPM_BUILD_ROOT/%{_pscheduler_daemons} \
     COMMANDDIR=$RPM_BUILD_ROOT/%{_pscheduler_commands} \
     install

mkdir -p $RPM_BUILD_ROOT/%{archiver_default_dir}
mkdir -p $RPM_BUILD_ROOT/%{_pscheduler_log_dir}

#
# API Server
#
API_ROOT="$(%{_pscheduler_python} -c 'import pscheduler ; print(pscheduler.api_root())')"

make -C api-server \
     'USER_NAME=%{_pscheduler_user}' \
     'GROUP_NAME=%{_pscheduler_group}' \
     "API_ROOT=${API_ROOT}" \
     "API_DIR=%{api_dir}" \
     "CONF_D=%{httpd_conf_d}" \
     "PREFIX=${RPM_BUILD_ROOT}" \
     "DSN_FILE=%{dsn_file}" \
     "LIMITS_FILE=%{_pscheduler_limit_config}" \
     "PYTHON=%(which %{_pscheduler_python})" \
     "RUN_DIR=%{run_dir}" \
     install

mkdir -p ${RPM_BUILD_ROOT}/%{server_conf_dir}

mkdir -p ${RPM_BUILD_ROOT}/%{run_dir}

#
# Utilities
#
make -C utilities \
    "DESTDIR=${RPM_BUILD_ROOT}/%{_pscheduler_commands}" \
    "INTERNALSDIR=$RPM_BUILD_ROOT/%{_pscheduler_internals}" \
    install


mkdir -p $RPM_BUILD_ROOT/%{_pscheduler_sudoersdir}
cat > $RPM_BUILD_ROOT/%{_pscheduler_sudoersdir}/%{name} <<EOF
#
# %{name}
#
Cmnd_Alias PSCHEDULER_COMMAND_LOG = %{_pscheduler_commands}/log
%%%{_pscheduler_group} ALL = (root) NOPASSWD: PSCHEDULER_COMMAND_LOG
Defaults!PSCHEDULER_COMMAND_LOG !requiretty


EOF




# ------------------------------------------------------------------------------

%pre

#
# Database
#

# (Nothing)


#
# Daemons
#
if [ "$1" -eq 2 ]
then
    for SERVICE in ticker runner archiver scheduler
    do
        NAME="pscheduler-${SERVICE}"
        systemctl stop "${NAME}"
    done
fi

#
# API Server
#
# (Nothing)


#
# Utilities
#
# (Nothing)




# ------------------------------------------------------------------------------

%post

#
# Database
#

# Increase the number of connections to something substantial

%define pgsql_max_connections 500
%define pgsql_deadlock_timeout 5s

%define pgsql_conf %{_pscheduler_postgresql_data}/postgresql.conf

OLD_CONF_DIGEST=$(sha256sum "%{pgsql_conf}" | awk '{ print $1 }')

# Note that this must be dropped in at the end so it overrides
# anything else in the file.
drop-in -n %{name} - "%{pgsql_conf}" <<EOF
#
# pScheduler
#
max_connections = %{pgsql_max_connections}
deadlock_timeout = %{pgsql_deadlock_timeout}
EOF

NEW_CONF_DIGEST=$(sha256sum "%{pgsql_conf}" | awk '{ print $1 }')

systemctl enable --now "%{_pscheduler_postgresql_service}"

# Restart the server only if the configuration has changed as a result
# of what we did to it.  This is more for development convenience than
# anything else since regular releases don't happen often.

if [ "${NEW_CONF_DIGEST}" != "${OLD_CONF_DIGEST}" ]
then
    echo "Restarting PostgreSQL after configuration change."
    systemctl restart "%{_pscheduler_postgresql_service}"
fi


# Load the database

# TODO: Note that if this fails, the scriptlet stops but RPM doesn't
# exit zero.  This is apparently not getting fixed.
#
# Discussion:
#   https://bugzilla.redhat.com/show_bug.cgi?id=569930
#   http://rpm5.org/community/rpm-users/0834.html
#

pscheduler internal db-update

# Note that this is safe to do because all of the daemons are stopped
# at this point and they, along with the web server, will be
# retstarted later.
pscheduler internal db-change-password


#
# Allow the account we created to authenticate locally.
#

HBA_FILE=$( (echo "\t on" ; echo "show hba_file;") \
	    | postgresql-load --log-errors "%{name}-hba-file" \
	    | head -1 \
	    | sed -e 's/^\s*//' )

drop-in -n -t %{name} - "${HBA_FILE}" <<EOF
#
# pScheduler
#
# This user should never need to access the database from anywhere
# other than locally.
#
local     pscheduler      pscheduler                            md5
host      pscheduler      pscheduler     127.0.0.1/32           md5
host      pscheduler      pscheduler     ::1/128                md5
EOF

# Make Pg reload what we just changed.
postgresql-load --log-errors "%{name}-config-reload" <<EOF
DO \$\$
DECLARE
    status BOOLEAN;
BEGIN
    SELECT INTO status pg_reload_conf();
    IF NOT status
    THEN
        RAISE EXCEPTION 'Failed to reload the server configuration';
    END IF;
END;
\$\$ LANGUAGE plpgsql;
EOF


#
# Daemons
#
systemctl daemon-reload
for SERVICE in ticker runner archiver scheduler
do
    NAME="pscheduler-${SERVICE}"
    systemctl enable "${NAME}"
    systemctl start "${NAME}"
done

# Some old installations ended up with root-owned files in the run
# directory.  Make their ownership correct.
# Note that this uses options specific to GNU Findutils.
find %{_rundir} -name "pscheduler-*" ! -user "%{_pscheduler_user}" -print0 \
    | xargs -0 -r chown "%{_pscheduler_user}.%{_pscheduler_group}"



#
# API Server
#
# On systems with SELINUX, allow database connections.
if selinuxenabled
then
    echo "Setting SELinux permissions (may take awhile)"
    # TODO: connect_db may be redundant redundant.
    # nis_enabled allows binding
    for SWITCH in \
	httpd_can_network_connect \
	httpd_can_network_connect_db \
	nis_enabled
    do
	STATE=$(getsebool "${SWITCH}" | awk '{ print $3 }')
        if [ "${STATE}" != "on" ]
        then
    	    setsebool -P "${SWITCH}" 1
	fi
    done
fi

systemctl enable httpd
systemctl start httpd


#
# Utilities
#

pscheduler internal service restart


# ------------------------------------------------------------------------------

%preun
#
# Daemons
#

# This must happen first
pscheduler internal service stop

# Have to stop this while we're uninstalling so connections to the
# database go away.
systemctl stop httpd


#
# API Server
#
# (Nothing)

#
# Database  (This has to be done after all services are stopped.)
#
if [ "$1" = "0" ]
then
    # Have to do this before the files are erased.
    postgresql-load  --log-errors "%{name}-teardown" %{_pscheduler_datadir}/database-teardown.sql
fi


#
# Utilities
#
# (Nothing)


# ------------------------------------------------------------------------------

%postun

#only do this stuff if we are actually uninstalling
if [ "$1" = "0" ]; then
    #
    # Database
    #
    HBA_FILE=$( (echo "\t on" ; echo "show hba_file;") \
            | postgresql-load --log-errors "%{name}-postun-hba-file" \
            | head -1 \
            | sed -e 's/^\s*//' )

    drop-in -r %{name} /dev/null $HBA_FILE

    drop-in -r %{name} /dev/null "%{_pscheduler_postgresql_data}/postgresql.conf"

    # Removing the max_connections change requires a restart, which
    # will also catch the HBA changes.
    systemctl reload-or-try-restart "%{_pscheduler_postgresql_service}"



    #
    # Daemons
    #
    # (Nothing)
    systemctl daemon-reload


    #
    # API Server
    #
    # TODO: Determine if we want to shut this off, as other services might
    # be using it.
    # if selinuxenabled
    # then
    #     echo "Setting SELinux permissions (may take awhile)"
    #     setsebool -P httpd_can_network_connect_db 1
    # fi
    # Assume this stays on.
    systemctl start httpd
else
    # We're doing an update so restart services
    pscheduler internal service restart
fi





#
# Utilities
#
# (Nothing)


# ------------------------------------------------------------------------------

# Triggers

# Any upgrade of python-pscheduler needs to force a database restart
# because Pg doesn't see module upgrades.

%triggerin -- %{_pscheduler_python}-pscheduler
systemctl reload-or-try-restart "%{_pscheduler_postgresql_service}"

# ------------------------------------------------------------------------------
%files

#
# Database
#
%defattr(-,%{_pscheduler_user},%{_pscheduler_group},-)
%license LICENSE
%{_pscheduler_datadir}/*
%attr(400,-,-)%verify(user group mode) %{db_config_dir}/*
%{_pscheduler_internals}/*
%{rpm_macros}
%{profile_d}/*

#
# Daemons
#

%defattr(-,root,root,-)
%license LICENSE
%attr(755,%{_pscheduler_user},%{_pscheduler_group})%verify(user group mode) %{daemon_config_dir}
%attr(600,%{_pscheduler_user},%{_pscheduler_group})%verify(user group mode) %config(noreplace) %{daemon_config_dir}/*
%{_unitdir}/*
%{_pscheduler_daemons}/*
%{_pscheduler_commands}/*
%attr(750,%{_pscheduler_user},%{_pscheduler_group}) %{archiver_default_dir}
%attr(750,%{_pscheduler_user},%{_pscheduler_group}) %{_pscheduler_log_dir}

#
# API Server
#
%defattr(-,%{_pscheduler_user},%{_pscheduler_group},-)
%license LICENSE
%{api_dir}
%config(noreplace) %{api_httpd_conf}

#
# Utilities
#

%attr(440,root,root) %{_pscheduler_sudoersdir}/*

