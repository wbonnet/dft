Role Name
=========

dft-sysop-playbook-logging

This role creates an execution log file when one or several roles are deployed using the ansible-playbook command.

This role is intended to be used for debugging purposed or installation log creation.
*warning*: Output information may contain sensitive information such as login or even passwordsaccording to your inventory file.

The log file contain all values of bothinternal ansible variables and inventory defined variables.

Requirements
------------

Any pre-requisites that may not be covered by Ansible itself or the role should be mentioned here.
For instance, if the role depends on given versions of kernel, drivers or u-boot.
It should also cover specific reinstalled packages needs when generating a rootfs or firmware image, thus not deploying role on a live system.

Role Variables
--------------

A description of the settable variables for this role should go here, including any variables that are in defaults/main.yml, vars/main.yml, and any variables that can/should be set via parameters to the role. Any variables that are read from other roles and/or the global scope (ie. hostvars, group vars, etc.) should be mentioned here as well.

Dependencies
------------

A list of other roles hosted on github or Galaxy should go here, plus any details in regards to parameters that may need to be set for other roles, or variables that are used from other roles.

Example Playbook
----------------

Including an example of how to use your role (for instance, with variables passed in as parameters) is always nice for users too:

    - hosts: servers
      roles:
         - { role: username.rolename, x: 42 }

License
-------

This role and provided files are subject to the Apache 2.0 license (default DFT License) unless specified differently in distinct files.


Author Information
------------------

Contributors list :
	- William Bonnet     (wllmbnnt@gmail.com, wbonnet@theitmakers.com)
