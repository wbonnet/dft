# Ansible naming rules
This folder contains the Ansible roles provided by the DFT project.
Roles are named according the following rules.

A role name is made of three components or fields which are dashed separated. The fields are :
* The ***name of the project*** it belongs to (ie dft). DFT role names are always prefixed by 'dft' as first field value

* The ***category*** of the role. Roles are available for the following categories:
  * apps (local software applications)
  * bsp (drivers and hardware support)
  * devel (development and compilers)
  * os (operating system and unix system itself)
  * network (system level only, end user apps go to srv)
  * security
  * sysop (administration tasks such as backups)
  * webapps (web and remote software applications)
  * xde (X Desktop Environment)
  * srv (service or server, a service runs on a server)
* The software ***functionality***
  * Definitions coming soon...
