# Comparison of Privacy Preserving Tools in Web Browsers and Extensions
## Author: Vojtěch Fiala (xfiala61)

This repository contains source codes and other files used for the thesis ``Comparison of Privacy Preserving Tools in Web Browsers and Extensions`` by Vojtěch Fiala.
The submitted version is available on [nextcloud](https://nextcloud.fit.vutbr.cz/s/WLts28GDwC4qeq2).

The folder structure is as follows:
- ``content-blocking/`` -- the implementation source codes and other implementation-related things
- ``content-blocking-virtual-machine`` -- folder with the exported virtual machine in .ovf format
- ``excel_at_fit/`` -- contains abstract, poster and the thumbnail for the Excel@FIT student conference
- ``semestral_project/`` -- contains first part of the thesis and presentation for semestral project
- ``thesis_text/`` -- the LaTeX source codes of the Thesis and the final .pdf files

To run in a virtual machine, you will need to use virtualization software that supports nested virtualization since the evaluation includes a DNS server that uses docker, which needs WSL to run. 
Use preferrably VMWare Workstation Pro 17, I tested that it works there. The default account is ``user`` with password ``user``. 
Virtual Box was tried too and it **DID NOT WORK**.

In case you run into any issues, feel free to contact me: 
- School email: ``xfiala61@stud.fit.vut.cz``
- Private email: ``vojtechfiala32@gmail.com`` 
