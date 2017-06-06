#
# RPM Spec for pScheduler Server
#

# TODO: Need to write proper systemd services for this package and
# make the scriptlets use them on CentOS 7.  For now the old-style
# init scripts function just fine.

Name:		pscheduler-server
Version:	1.0.0.5
Release:	1%{?dist}

Summary:	pScheduler Server
BuildArch:	noarch
License:	Apache 2.0
Group:		Unspecified

Source0:	%{name}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}


# Database
BuildRequires:	postgresql-init
BuildRequires:	postgresql-load
BuildRequires:	postgresql-server
BuildRequires:	postgresql95-contrib
BuildRequires:	postgresql95-plpython

Requires:	drop-in
# This is for pgcrypto
Requires:	postgresql95-contrib
Requires:	postgresql95-plpython
Requires:	postgresql-load
Requires:	pscheduler-account
Requires:	pscheduler-core
Requires:	pscheduler-database-init
Requires:	random-string >= 1.1

# Daemons
BuildRequires:	m4
Requires:	curl
Requires:	pscheduler-account
Requires:	python-daemon
Requires:	python-flask
Requires:	python-ipaddr
Requires:	python-requests
Requires:	python-jsontemplate

# API Server
BuildRequires:	pscheduler-account
BuildRequires:	pscheduler-rpm
BuildRequires:	python-pscheduler >= 1.1
BuildRequires:	m4
Requires:	httpd-wsgi-socket
Requires:	pscheduler-server
# Note that the actual definition of what protocol is used is part of
# python-pscheduler, but this package is what does the serving, so
# mod_ssl is required here.
Requires:	mod_ssl
Requires:	mod_wsgi
Requires:	python-pscheduler >= 1.1
Requires:	python-requests
Requires:	pytz


# General
BuildRequires:	pscheduler-rpm

%if 0%{?el6}
Requires:	chkconfig
%endif
%if 0%{?el7}
BuildRequires:	systemd
%{?systemd_requires: %systemd_requires}
%endif

%description
The pScheduler server


# Database

%define pgsql_version 9.5
%define pgsql_service postgresql-%{pgsql_version}
%define pg_data %{_sharedstatedir}/pgsql/%{pgsql_version}/data

%define daemon_config_dir %{_pscheduler_sysconfdir}/daemons
%define db_config_dir %{_pscheduler_sysconfdir}/database
%define db_user %{_pscheduler_user}
%define password_file %{db_config_dir}/database-password
%define dsn_file %{db_config_dir}/database-dsn
%define pgpass_file %{db_config_dir}/pgpassfile
%define default_archives %{_pscheduler_sysconfdir}/archives
%define rpm_macros %{_pscheduler_rpmmacroprefix}%{name}

# Daemons
%define log_dir %{_var}/log/pscheduler
%define archiver_default_dir %{_pscheduler_sysconfdir}/default-archives

# API Server
%define httpd_conf_d   %{_sysconfdir}/httpd/conf.d
%define api_httpd_conf %{httpd_conf_d}/pscheduler-api-server.conf

%define server_conf_dir %{_pscheduler_sysconfdir}

# Note that we want this here because it seems to work well without
# assistance on systems where selinux is enabled.  Anywhere else and
# there'd have to be a 'chcon -R -t httpd_user_content_t'.
%define api_dir	     %{_var}/www/%{name}


# ------------------------------------------------------------------------------

%prep

%if 0%{?el6}%{?el7} == 0
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
     ROLE=%{db_user} \
     PGPASSFILE=$RPM_BULID_ROOT/%{pgpass_file}

#
# Daemons
#
make -C daemons \
     CONFIGDIR=%{daemon_config_dir} \
     DAEMONDIR=%{_pscheduler_daemons} \
     DSNFILE=%{dsn_file} \
     LOGDIR=%{log_dir} \
     PGDATABASE=%{_pscheduler_database_name} \
     PGPASSFILE=%{_pscheduler_database_pgpass_file} \
     PGSERVICE=%{pgsql_service}.service \
     PGUSER=%{_pscheduler_database_user} \
     PSUSER=%{_pscheduler_user} \
     ARCHIVERDEFAULTDIR=%{archiver_default_dir} \
     VAR=%{_var}

#
# API Server
#
# (Nothing)


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
%if 0%{?el6}
     INITDDIR=$RPM_BUILD_ROOT/%{_initddir} \
%endif
%if 0%{?el7}
     UNITDIR=$RPM_BUILD_ROOT/%{_unitdir} \
%endif
     DAEMONDIR=$RPM_BUILD_ROOT/%{_pscheduler_daemons} \
     COMMANDDIR=$RPM_BUILD_ROOT/%{_pscheduler_commands} \
     install

mkdir -p $RPM_BUILD_ROOT/%{archiver_default_dir}
mkdir -p $RPM_BUILD_ROOT/%{log_dir}

#
# API Server
#
API_ROOT="$(python -c 'import pscheduler ; print pscheduler.api_root()')"

make -C api-server \
     'USER_NAME=%{_pscheduler_user}' \
     'GROUP_NAME=%{_pscheduler_group}' \
     "API_ROOT=${API_ROOT}" \
     "API_DIR=%{api_dir}" \
     "CONF_D=%{httpd_conf_d}" \
     "PREFIX=${RPM_BUILD_ROOT}" \
     "DSN_FILE=%{dsn_file}" \
     "LIMITS_FILE=%{_pscheduler_limit_config}" \
     install

mkdir -p ${RPM_BUILD_ROOT}/%{server_conf_dir}



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
%if 0%{?el6}
        service "${NAME}" stop
%endif
%if 0%{?el7}
        systemctl stop "${NAME}"
%endif
    done
fi

#
# API Server
#
# (Nothing)

# EL6 has an incorrectly packaged python-jinja2, which installs the
# finished code in site-packages/Jinja2-2.6-py2.6.egg/jinja2 where
# Python can't import it as the expected jinja2.  See commentary in
# #215.

%define site_packages /usr/lib/python2.6/site-packages
%define jinja2_symlink %{site_packages}/jinja2

%if 0%{?el6}
if [ "$1" -ge "1" ]
then

    # If RPM left an empty directory, get rid of it.  If the rmdir
    # fails, go quietly because it's not empty.
    [ -d "%{jinja2_symlink}" ] \
	&& rmdir "%{jinja2_symlink}" > /dev/null 2>&1 \
	|| true

    # If there's nothing where the link should be, make it.
    if [ ! -e "%{jinja2_symlink}" ]
    then
	EGG=$((cd %{site_packages} \
	    && find . -type d -name "Jinja2-*-py*.egg") \
	    | head -1 | sed -e 's|^./||')
	ln -s "${EGG}/jinja2" "%{jinja2_symlink}"
    fi

fi
%endif



# ------------------------------------------------------------------------------

%post

#
# Database
#

# Increase the number of connections to something substantial

%define pgsql_max_connections 500

# Note that this must be dropped in at the end so it overrides
# anything else in the file.
drop-in -n %{name} - "%{pg_data}/postgresql.conf" <<EOF
#
# pScheduler
#
max_connections = %{pgsql_max_connections}
EOF


%if 0%{?el6}
chkconfig "%{pgsql_service}" on
service "%{pgsql_service}" start
%endif
%if 0%{?el7}
systemctl enable "%{pgsql_service}"
systemctl start "%{pgsql_service}"
%endif

# Restart the server only if the current maximum connections is less
# than what we just installed.  This is more for development
# convenience than anything else since regular releases don't happen
# often.

SERVER_MAX=$( (echo "\\t" && echo "\\a" && echo "show max_connections") \
    | postgresql-load)

if [ "${SERVER_MAX}" -lt "%{pgsql_max_connections}" ]
then
%if 0%{?el6}
    service "%{pgsql_service}" restart
%endif
%if 0%{?el7}
    systemctl restart "%{pgsql_service}"
%endif
fi


# Generate a password if the file is empty, which is the case after
# the first install.
#
# TODO: This might be annoying if someone intentionally sets the
# password up as empty.
if [ ! -s '%{password_file}' ]
then
    random-string --safe --length 60 --randlength > '%{password_file}'
fi

# Check our assumptions
if [ "$(wc -l < '%{password_file}')" -ne 1 ]
then
    echo "INTERNAL ERROR: " \
        "Password file %{password_file} must contain exactly one line." 1>&2
    exit 1
fi

ROLE="%{_pscheduler_user}"

# Generate the DSN file
awk -v "ROLE=${ROLE}" '{ printf "host=127.0.0.1 dbname=pscheduler user=%s password=%s\n", ROLE, $1 }' \
    "%{password_file}" \
    > "${RPM_BUILD_ROOT}/%{dsn_file}"

# Generate a PostgreSQL password file
# Format is hostname:port:database:username:password
awk -v "ROLE=${ROLE}" '{ printf "*:*:pscheduler:%s:%s\n", ROLE, $1 }' \
    "%{password_file}" \
    > "${RPM_BUILD_ROOT}/%{pgpass_file}"
chmod 400 "${RPM_BUILD_ROOT}/%{pgpass_file}"



# Load the database

# TODO: Note that if this fails, the scriptlet stops but RPM doesn't
# exit zero.  This is apparently not getting fixed.
#
# Discussion:
#   https://bugzilla.redhat.com/show_bug.cgi?id=569930
#   http://rpm5.org/community/rpm-users/0834.html
#

pscheduler internal db-update

# Securely set the password for the role to match the one we generated.

ROLESQL="${TMP:-/tmp}/%{name}.$$"
touch "${ROLESQL}"
chmod 400 "${ROLESQL}"

printf "ALTER ROLE ${ROLE} WITH UNENCRYPTED PASSWORD '" > "${ROLESQL}"
tr -d "\n" < "%{password_file}" >> "${ROLESQL}"
printf "';\n"  >> "${ROLESQL}"

postgresql-load "${ROLESQL}"
rm -f "${ROLESQL}"

#
# Allow the account we created to authenticate locally.
#

HBA_FILE=$( (echo "\t on" ; echo "show hba_file;") \
	    | postgresql-load \
	    | head -1 \
	    | sed -e 's/^\s*//' )

drop-in -n -t %{name} - "${HBA_FILE}" <<EOF
#
# pScheduler
#
# This user should never need to access the database from anywhere
# other than locally.
#
%if 0%{?el6}
# TODO: SECURITY: The password method doesn't seem to work on pg 9.5
# when installed on el6.  Find out why and how to fix that.
# Followup: The md5 method does seem to work on the pS toolkit.  Check
# to see if it works on 6.8.
local     pscheduler      pscheduler                            trust
host      pscheduler      pscheduler     127.0.0.1/32           trust
host      pscheduler      pscheduler     ::1/128                trust
%endif
%if 0%{?el7}
local     pscheduler      pscheduler                            md5
host      pscheduler      pscheduler     127.0.0.1/32           md5
host      pscheduler      pscheduler     ::1/128                md5
%endif
EOF

# Make Pg reload what we just changed.
postgresql-load <<EOF
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
for SERVICE in ticker runner archiver scheduler
do
    NAME="pscheduler-${SERVICE}"
%if 0%{?el6}
    chkconfig "${NAME}" on
    service "${NAME}" start
%endif
%if 0%{?el7}
    systemctl enable "${NAME}"
    systemctl start "${NAME}"
%endif
done


#
# API Server
#
# On systems with SELINUX, allow database connections.
if selinuxenabled
then
    STATE=$(getsebool httpd_can_network_connect_db | awk '{ print $3 }')
    if [ "${STATE}" != "on" ]
    then
        echo "Setting SELinux permissions (may take awhile)"
        setsebool -P httpd_can_network_connect_db 1
    fi

    # TODO: Remove when BWCTL backward compatibility is removed.  See #107.
    STATE=$(getsebool httpd_can_network_connect | awk '{ print $3 }')
    if [ "${STATE}" != "on" ]
    then
        echo "Setting SELinux permissions (may take awhile)"
        setsebool -P httpd_can_network_connect 1
    fi

fi


%if 0%{?el6}
chkconfig httpd on
service httpd restart
%endif
%if 0%{?el7}
systemctl enable httpd
systemctl restart httpd
%endif


# ------------------------------------------------------------------------------

%preun
#
# Daemons
#
for SERVICE in ticker runner archiver scheduler
do
    NAME="pscheduler-${SERVICE}"
%if 0%{?el6}
    service "${NAME}" stop
%endif
%if 0%{?el7}
    systemctl stop "${NAME}"
%endif
done

# Have to stop this while we're uninstalling so connections to the
# database go away.
%if 0%{?el6}
service httpd stop
%endif
%if 0%{?el7}
systemctl stop httpd
%endif


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
    postgresql-load %{_pscheduler_datadir}/database-teardown.sql
fi



# ------------------------------------------------------------------------------

%postun

#only do this stuff if we are actually uninstalling
if [ "$1" = "0" ]; then
    #
    # Database
    #
    HBA_FILE=$( (echo "\t on" ; echo "show hba_file;") \
            | postgresql-load \
            | head -1 \
            | sed -e 's/^\s*//' )

    drop-in -r %{name} /dev/null $HBA_FILE

    drop-in -r %{name} /dev/null "%{pg_data}/postgresql.conf"

    # Removing the max_connections change requires a restart, which
    # will also catch the HBA changes.
%if 0%{?el6}
    service "%{pgsql_service}" restart
%endif
%if 0%{?el7}
    systemctl restart "%{pgsql_service}"
%endif



    #
    # Daemons
    #
    # (Nothing)



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
else
    #we're doing an update so restart services
    for SERVICE in ticker runner archiver scheduler
    do
        NAME="pscheduler-${SERVICE}"
%if 0%{?el6}
        service "${NAME}" restart
%endif
%if 0%{?el7}
        systemctl restart "${NAME}"
%endif
    done
fi


# Correction for bad packaging in EL6; see %post for commentary.
%if 0%{?el6}
if [ "$1" -eq "0" -a -L "%{jinja2_symlink}" ]
then
    rm -f "%{jinja2_symlink}"
fi
%endif


%if 0%{?el6}
service httpd start
%endif
%if 0%{?el7}
systemctl start httpd
%endif


# ------------------------------------------------------------------------------

%files

#
# Database
#
%defattr(-,%{_pscheduler_user},%{_pscheduler_group},-)
%{_pscheduler_datadir}/*
%attr(400,-,-)%verify(user group mode) %{db_config_dir}/*
%{_pscheduler_internals}/*
%{rpm_macros}
%{profile_d}/*

#
# Daemons
#

%defattr(-,root,root,-)
%attr(755,%{_pscheduler_user},%{_pscheduler_group})%verify(user group mode) %{daemon_config_dir}
%attr(600,%{_pscheduler_user},%{_pscheduler_group})%verify(user group mode) %config(noreplace) %{daemon_config_dir}/*
%if 0%{?el6}
%{_initddir}/*
%endif
%if 0%{?el7}
%{_unitdir}/*
%endif
%{_pscheduler_daemons}/*
%{_pscheduler_commands}/*
%attr(750,%{_pscheduler_user},%{_pscheduler_group}) %{archiver_default_dir}
%attr(750,%{_pscheduler_user},%{_pscheduler_group}) %{log_dir}

#
# API Server
#
%defattr(-,%{_pscheduler_user},%{_pscheduler_group},-)
%{api_dir}
%config(noreplace) %{api_httpd_conf}
