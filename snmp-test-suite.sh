cd pscheduler-test-snmpget/; dos2unix snmpget/*; sudo make cbic;
cd ../pscheduler-test-snmpgetbgm/; dos2unix snmpgetbgm/*; sudo make cbic;
cd ../pscheduler-tool-pysnmp/; dos2unix pysnmp/*; sudo make cbic;
clear

function results {
	RES=$(curl -k -s ${ARG} | jq '{succeeded: .result.result.succeeded, data: .result.result.data}' | jq 'if (.succeeded == true) then (if (.data[0][0] | length) == 3 then 1 else 0 end) else 0 end')
	if [ $RES -eq 1 ] 
		then
			echo 'TEST PASSED'
			printf '\n'
		else
			printf 'TEST FAILED\n\n------OUTPUT------\n\n'
			echo ${ARG}
			printf '\n'
	fi
}
# get tests

printf 'TEST 1 - Version 1\n'
ARG=$(pscheduler task snmpget --dest demo.snmplabs.com --version 1 --community public --oid DISMAN-EVENT-MIB::sysUpTimeInstance | egrep '^https?://')
results

printf 'TEST 2 - Version 2c\n'
ARG=$(pscheduler task snmpget --dest demo.snmplabs.com --version 2c --community public --oid DISMAN-EVENT-MIB::sysUpTimeInstance | egrep '^https?://')
results

printf 'TEST 3 - Version 3 (noAuthNoPriv)\n'
ARG=$(pscheduler task snmpget --dest demo.snmplabs.com --version 3 --security-name usr-none-none --security-level noAuthNoPriv --oid DISMAN-EVENT-MIB::sysUpTimeInstance | egrep '^https?://')
results

printf 'TEST 4 - Version 3 (authNoPriv, MD5)\n'
ARG=$(pscheduler task snmpget --dest demo.snmplabs.com --version 3 --security-name usr-md5-none --security-level authNoPriv --auth-protocol MD5 --auth-key authkey1 --oid DISMAN-EVENT-MIB::sysUpTimeInstance | egrep '^https?://')
results

printf 'TEST 5 - Version 3 (authNoPriv, SHA)\n'
ARG=$(pscheduler task snmpget --dest demo.snmplabs.com --version 3 --security-name usr-sha-none --security-level authNoPriv --auth-protocol SHA --auth-key authkey1 --oid DISMAN-EVENT-MIB::sysUpTimeInstance | egrep '^https?://')
results

printf 'TEST 6 - Version 3 (authPriv, MD5, DES)\n'
ARG=$(pscheduler task snmpget --dest demo.snmplabs.com --version 3 --security-name usr-md5-des --security-level authPriv --auth-protocol MD5 --auth-key authkey1 --priv-protocol DES --priv-key privkey1 --oid DISMAN-EVENT-MIB::sysUpTimeInstance | egrep '^https?://')
results

printf 'TEST 7 - Version 3 (authPriv, MD5, 3DES)\n'
ARG=$(pscheduler task snmpget --dest demo.snmplabs.com --version 3 --security-name usr-md5-3des --security-level authPriv --auth-protocol MD5 --auth-key authkey1 --priv-protocol 3DES --priv-key privkey1 --oid DISMAN-EVENT-MIB::sysUpTimeInstance | egrep '^https?://')
results

printf 'TEST 8 - Version 3 (authPriv, MD5, AES)\n'
ARG=$(pscheduler task snmpget --dest demo.snmplabs.com --version 3 --security-name usr-md5-aes --security-level authPriv --auth-protocol MD5 --auth-key authkey1 --priv-protocol AES --priv-key privkey1 --oid DISMAN-EVENT-MIB::sysUpTimeInstance | egrep '^https?://')
results

printf 'TEST 9 - Version 3 (authPriv, MD5, AES128)\n'
ARG=$(pscheduler task snmpget --dest demo.snmplabs.com --version 3 --security-name usr-md5-aes128 --security-level authPriv --auth-protocol MD5 --auth-key authkey1 --priv-protocol AES128 --priv-key privkey1 --oid DISMAN-EVENT-MIB::sysUpTimeInstance | egrep '^https?://')
results

printf 'TEST 10 - Version 3 (authPriv, MD5, AES192)\n'
ARG=$(pscheduler task snmpget --dest demo.snmplabs.com --version 3 --security-name usr-md5-aes192 --security-level authPriv --auth-protocol MD5 --auth-key authkey1 --priv-protocol AES192 --priv-key privkey1 --oid DISMAN-EVENT-MIB::sysUpTimeInstance | egrep '^https?://')
results

printf 'TEST 11 - Version 3 (authPriv, MD5, AES256)\n'
ARG=$(pscheduler task snmpget --dest demo.snmplabs.com --version 3 --security-name usr-md5-aes256 --security-level authPriv --auth-protocol MD5 --auth-key authkey1 --priv-protocol AES256 --priv-key privkey1 --oid DISMAN-EVENT-MIB::sysUpTimeInstance | egrep '^https?://')
results

printf 'TEST 12 - Version 3 (authPriv, SHA, DES)\n'
ARG=$(pscheduler task snmpget --dest demo.snmplabs.com --version 3 --security-name usr-sha-des --security-level authPriv --auth-protocol SHA --auth-key authkey1 --priv-protocol DES --priv-key privkey1 --oid DISMAN-EVENT-MIB::sysUpTimeInstance | egrep '^https?://')
results

printf 'TEST 13 - Version 3 (authPriv, SHA, 3DES)\n'
ARG=$(pscheduler task snmpget --dest demo.snmplabs.com --version 3 --security-name usr-sha-3des --security-level authPriv --auth-protocol SHA --auth-key authkey1 --priv-protocol 3DES --priv-key privkey1 --oid DISMAN-EVENT-MIB::sysUpTimeInstance | egrep '^https?://')
results

printf 'TEST 14 - Version 3 (authPriv, SHA, AES)\n'
ARG=$(pscheduler task snmpget --dest demo.snmplabs.com --version 3 --security-name usr-sha-aes --security-level authPriv --auth-protocol SHA --auth-key authkey1 --priv-protocol AES --priv-key privkey1 --oid DISMAN-EVENT-MIB::sysUpTimeInstance | egrep '^https?://')
results

printf 'TEST 15 - Version 3 (authPriv, SHA, AES128)\n'
ARG=$(pscheduler task snmpget --dest demo.snmplabs.com --version 3 --security-name usr-sha-aes128 --security-level authPriv --auth-protocol SHA --auth-key authkey1 --priv-protocol AES128 --priv-key privkey1 --oid DISMAN-EVENT-MIB::sysUpTimeInstance | egrep '^https?://')
results

printf 'TEST 16 - Version 3 (authPriv, SHA, AES192)\n'
ARG=$(pscheduler task snmpget --dest demo.snmplabs.com --version 3 --security-name usr-sha-aes192 --security-level authPriv --auth-protocol SHA --auth-key authkey1 --priv-protocol AES192 --priv-key privkey1 --oid DISMAN-EVENT-MIB::sysUpTimeInstance | egrep '^https?://')
results

printf 'TEST 17 - Version 3 (authPriv, SHA, AES256)\n'
ARG=$(pscheduler task snmpget --dest demo.snmplabs.com --version 3 --security-name usr-sha-aes256 --security-level authPriv --auth-protocol SHA --auth-key authkey1 --priv-protocol AES256 --priv-key privkey1 --oid DISMAN-EVENT-MIB::sysUpTimeInstance | egrep '^https?://')
results

printf 'TEST 18 - Version 2c with multiple OIDs\n'
ARG=$(pscheduler task snmpget --dest demo.snmplabs.com --version 2c --community public --oid DISMAN-EVENT-MIB::sysUpTimeInstance,IF-MIB::ifInOctets.1 | egrep '^https?://')
results

# invalid arguments tests

printf 'TEST 19 - Unresponsive hostname\n'
ARG=$(pscheduler task snmpget --dest demo.snmplabs.com --version 2c --community 'this will cause unresponiveness' --oid DISMAN-EVENT-MIB::sysUpTimeInstance | egrep '^https?://')

printf 'TEST 20 - Unresolvable hostname\n'
ARG=$(pscheduler task snmpget --dest badhost.com --version 2c --community public --oid DISMAN-EVENT-MIB::sysUpTimeInstance | egrep '^https?://')

printf 'TEST 21 - No such instance\n'
ARG=$(pscheduler task snmpget --dest demo.snmplabs.com --version 2c --community public --oid SNMPv2-MIB::sysORUpTime.10000 | egrep '^https?://')

printf 'TEST 22 - No such object\n'
ARG=$(pscheduler task snmpget --dest demo.snmplabs.com --version 2c --community public --oid SNMPv2-MIB::badObject.0 | egrep '^https?://')

printf 'TEST 23 - No such MIB\n'
ARG=$(pscheduler task snmpget --dest demo.snmplabs.com --version 2c --community public --oid SOME-MIB::sysORUpTime.1 | egrep '^https?://')