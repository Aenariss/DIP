# Comparison of privacy-preserving web browsers and extensions
## Author: Vojtěch Fiala (xfiala61)

This repository contains source codes and other files used for the thesis ``Comparison of privacy-preserving web browsers and extensions`` by Vojtěch Fiala

The folder structure is as follows:
- ``content-blocking/`` -- the implementation source codes and other implementation-related things
- ``excel/`` -- contains abstract, poster and the thumbnail for the Excel@FIT student conference
- ``sep/`` -- contains first part of the thesis and presentation for semestral project
- ``thesis_text/`` -- the LaTeX source codes of the Thesis and the final .pdf files

To run in a virtual machine, you will need to use virtualization software that supports nested virtualization since the evaluation includes a DNS server that  uses docker (I tested it on Virtual Box, **DOES NOT WORK**).
If you are using the included OVF image of virtual machine, use preferrably VMWare Workstation Pro 17, I tested that it works there. The default account is ``user`` with password ``user``.
