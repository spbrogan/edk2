=======
OvmfPkg
=======

This README.rst summarizes the current state of Platform CI for OvmfPkg.
It also describes how to _build_ OvmfPkg using the Pytools build system.
For general documentation on OvmfPkg, refer to the `README <./README>`_.

Platform CI Current Status
---------------------------

IA32 Configuration
``````````````````
=============== ============= ============= =============
 Toolchain      DEBUG         RELEASE       NOOPT
=============== ============= ============= =============
`Win VS2019`_   |ap32d|       |ap32r|       |ap32n|
`Ubuntu GCC5`_  |ap32du|      |ap32ru|      |ap32nu|
=============== ============= ============= =============

X64 Configuration
`````````````````
=============== ============= ============= =============
 Toolchain      DEBUG         RELEASE       NOOPT
=============== ============= ============= =============
`Win VS2019`_   |ap64d|       |ap64r|       |ap64n|
`Ubuntu GCC5`_  |ap64du|      |ap64ru|      |ap64nu|
=============== ============= ============= =============

IA32X64 Configuration
`````````````````````
PEI phase is 32-bit while DXE phase is 64-bit

=============== ============= ============= =============
 Toolchain      DEBUG         RELEASE       NOOPT
=============== ============= ============= =============
`Win VS2019`_   |ap3264d|     |ap3264r|     |ap3264n|
`Ubuntu GCC5`_  |ap3264du|    |ap3264ru|    |ap3264nu|
=============== ============= ============= =============


IA32X64 FULL Configuration
``````````````````````````
PEI phase is 32-bit while DXE phase is 64-bit

Additional Build flags:
  * SECURE_BOOT_ENABLE=1
  * SMM_REQUIRE=1
  * TPM_ENABLE=1
  * TPM_CONFIG_ENABLE=1
  * NETWORK_TLS_ENABLE=1
  * NETWORK_IP6_ENABLE=1
  * NETWORK_HTTP_BOOT_ENABLE=1

=============== ============= ============= =============
 Toolchain      DEBUG         RELEASE       NOOPT
=============== ============= ============= =============
`Win VS2019`_   |ap3264fd|    |ap3264fr|    |ap3264fn|
`Ubuntu GCC5`_  |ap3264fdu|   |ap3264fru|   |ap3264fru|
=============== ============= ============= =============

Setup
-----

The Usual EDK2 Build Setup
``````````````````````````

- `Python 3.8.x - Download & Install <https://www.python.org/downloads/>`_
- `GIT - Download & Install <https://git-scm.com/download/>`_
- `GIT - Configure for EDK II <https://github.com/tianocore/tianocore.github.io/wiki/Windows-systems#github-help>`_
- `QEMU - Download, Install, and add to your path <https://www.qemu.org/download/>`_
- `EDKII Source - Download/Checkout from Github <https://github.com/tianocore/tianocore.github.io/wiki/Windows-systems#download>`_

  - **NOTE:** Do _not_ follow the EDK II Compile Tools and Build instructions, see below...

Differences from EDK Classic Build Setup
````````````````````````````````````````

- Build BaseTools using `python BaseTools/Edk2ToolsBuild.py [-t <ToolChainTag>]`
  - This replaces `edksetup Rebuild`" from the classic build system
  - For Windows `<ToolChainTag>` examples, refer to `Windows ToolChain Matrix <https://github.com/tianocore/tianocore.github.io/wiki/Windows-systems-ToolChain-Matrix>`_, defaults to `VS2017` if not specified
- **No Action:** Submodule initialization and manual installation/setup of NASM and iASL are **not** required, it is handled by the Pytools build system

Install & Configure Pytools for OvmfPkg
```````````````````````````````````````

* Install Pytools

  .. code-block:: bash

    pip install --upgrade -r pip-requirements.txt

* Initialize & Update Submodules

  .. code-block:: bash

    stuart_setup -c OvmfPkg/PlatformCI/PlatformBuild.py

* Initialize & Update Dependencies (e.g. iASL & NASM)

  .. code-block:: bash

    stuart_update -c OvmfPkg/PlatformCI/PlatformBuild.py

Building
--------

OVMF has `3 versions <https://github.com/tianocore/tianocore.github.io/wiki/How-to-build-OVMF#choosing-which-version-of-ovmf-to-build>`_. To build them using Pytools:

First set the `TOOL_CHAIN_TAG` via environment variable, Conf/target.txt, or pass it on the command-lines below using `TOOL_CHAIN_TAG=<value>` syntax.

===================== ===============
Platform              Commandline
===================== ===============
OvmfPkgIa32X64.dsc    `stuart_build -c OvmfPkg/PlatformCI/PlatformBuild.py [TOOL_CHAIN_TAG=<TOOL_CHAIN_TAG>]` |br| `stuart_build -c OvmfPkg/PlatformCI/PlatformBuild.py -a IA32,X64 [TOOL_CHAIN_TAG=<TOOL_CHAIN_TAG>]`
OvmfPkgIa32.dsc       `stuart_build -c OvmfPkg/PlatformCI/PlatformBuild.py -a IA32 [TOOL_CHAIN_TAG=<TOOL_CHAIN_TAG>]`
OvmfPkgX64.dsc        `stuart_build -c OvmfPkg/PlatformCI/PlatformBuild.py -a X64 [TOOL_CHAIN_TAG=<TOOL_CHAIN_TAG>]`
===================== ===============

**NOTE:** configuring ACTIVE_PLATFORM and TARGET_ARCH in Conf/target.txt is **not** required. This environment is set by PlatformBuild.py based upon the `[-a <TARGET_ARCH>]` parameter.

Custom Build Options
````````````````````

**MAKE_STARTUP_NSH=TRUE** will output a _startup.nsh_ file to the location mapped as fs0. This is used in CI in combination with the --FlashOnly feature to run QEMU to the UEFI shell and then execute the contents of startup.nsh.

**QEMU_HEADLESS=TRUE** Since CI servers run headless QEMU must be told to run with no display otherwise an error occurs. Locally you don't need to set this.

Passing Build Defines
`````````````````````
To pass build defines through stuart_build, prepend `BLD_*_` to the define name and pass it on the commandline. stuart_build currently requires values to be assigned, so add a `=1` suffix for bare defines.
For example, to enable the Intel E1000 NIC, instead of the traditional "-D E1000_ENABLE", the stuart_build command-line would be:

.. code-block:: bash

  stuart_build -c OvmfPkg/PlatformCI/PlatformBuild.py BLD_*_E1000_ENABLE=1

Running QEMU Emulator
---------------------

QEMU can be automatically launched using stuart_build.  This makes path management and quick verification easy.
QEMU must be added to your path.  On Windows this is a manual process and not part of the QEMU installer.

1. To run as part of the build but after building add the `--FlashRom` parameter.
2. To run after the build process standalone use your build command mentioned above plus `--FlashOnly`.

**NOTE:** Logging the execution output will be in the normal stuart log as well as to your console.

References
----------
- `Installing Pytools <https://github.com/tianocore/edk2-pytool-extensions/blob/master/docs/using.md#installing>`_
- For each workspace, consider creating & using a `Python Virtual Environment <https://docs.python.org/3/library/venv.html>`_

  * `Sample Layout <https://microsoft.github.io/mu/CodeDevelopment/prerequisites/#workspace-virtual-environment-setup-process>`_

- `stuart_build commandline parser <https://github.com/tianocore/edk2-pytool-extensions/blob/56f6a7aee09995c2f22da4765e8b0a29c1cbf5de/edk2toolext/edk2_invocable.py#L109>`_




.. ===================================================================
.. This is a bunch of directives to make the README file more readable
.. ===================================================================
.. role:: raw-html(raw)
    :format: html

.. _Bugzilla 2661: https://bugzilla.tianocore.org/show_bug.cgi?id=2661

.. _Win VS2019:  https://dev.azure.com/tianocore/edk2-ci-play/_build/latest?definitionId=38&branchName=master/
.. _Ubuntu GCC5: https://dev.azure.com/tianocore/edk2-ci-play/_build/latest?definitionId=37&branchName=master

.. |ap32d| image:: https://dev.azure.com/tianocore/edk2-ci-play/_apis/build/status/OVMF/OVMF%20Windows%20VS2019?branchName=master&jobName=Platform_CI&configuration=Platform_CI%20OVMF_IA32_DEBUG
.. |ap32du| image:: https://dev.azure.com/tianocore/edk2-ci-play/_apis/build/status/OVMF/OVMF%20Ubuntu%20GCC5?branchName=master&jobName=Platform_CI&configuration=Platform_CI%20OVMF_IA32_DEBUG
.. |ap32r| image:: https://dev.azure.com/tianocore/edk2-ci-play/_apis/build/status/OVMF/OVMF%20Windows%20VS2019?branchName=master&jobName=Platform_CI&configuration=Platform_CI%20OVMF_IA32_RELEASE
.. |ap32ru| image:: https://dev.azure.com/tianocore/edk2-ci-play/_apis/build/status/OVMF/OVMF%20Ubuntu%20GCC5?branchName=master&jobName=Platform_CI&configuration=Platform_CI%20OVMF_IA32_RELEASE
.. |ap32n| image:: https://dev.azure.com/tianocore/edk2-ci-play/_apis/build/status/OVMF/OVMF%20Windows%20VS2019?branchName=master&jobName=Platform_CI&configuration=Platform_CI%20OVMF_IA32_NOOPT
.. |ap32nu| image:: https://dev.azure.com/tianocore/edk2-ci-play/_apis/build/status/OVMF/OVMF%20Ubuntu%20GCC5?branchName=master&jobName=Platform_CI&configuration=Platform_CI%20OVMF_IA32_NOOPT

.. |ap64d| image:: https://dev.azure.com/tianocore/edk2-ci-play/_apis/build/status/OVMF/OVMF%20Windows%20VS2019?branchName=master&jobName=Platform_CI&configuration=Platform_CI%20OVMF_X64_DEBUG
.. |ap64du| image:: https://dev.azure.com/tianocore/edk2-ci-play/_apis/build/status/OVMF/OVMF%20Ubuntu%20GCC5?branchName=master&jobName=Platform_CI&configuration=Platform_CI%20OVMF_X64_DEBUG
.. |ap64r| image:: https://dev.azure.com/tianocore/edk2-ci-play/_apis/build/status/OVMF/OVMF%20Windows%20VS2019?branchName=master&jobName=Platform_CI&configuration=Platform_CI%20OVMF_X64_RELEASE
.. |ap64ru| image:: https://dev.azure.com/tianocore/edk2-ci-play/_apis/build/status/OVMF/OVMF%20Ubuntu%20GCC5?branchName=master&jobName=Platform_CI&configuration=Platform_CI%20OVMF_X64_RELEASE
.. |ap64n| image:: https://dev.azure.com/tianocore/edk2-ci-play/_apis/build/status/OVMF/OVMF%20Windows%20VS2019?branchName=master&jobName=Platform_CI&configuration=Platform_CI%20OVMF_X64_NOOPT
.. |ap64nu| image:: https://dev.azure.com/tianocore/edk2-ci-play/_apis/build/status/OVMF/OVMF%20Ubuntu%20GCC5?branchName=master&jobName=Platform_CI&configuration=Platform_CI%20OVMF_X64_NOOPT


.. |ap3264d| image:: https://dev.azure.com/tianocore/edk2-ci-play/_apis/build/status/OVMF/OVMF%20Windows%20VS2019?branchName=master&jobName=Platform_CI&configuration=Platform_CI%20OVMF_IA32X64_DEBUG
.. |ap3264du| image:: https://dev.azure.com/tianocore/edk2-ci-play/_apis/build/status/OVMF/OVMF%20Ubuntu%20GCC5?branchName=master&jobName=Platform_CI&configuration=Platform_CI%20OVMF_IA32X64_DEBUG
.. |ap3264r| image:: https://dev.azure.com/tianocore/edk2-ci-play/_apis/build/status/OVMF/OVMF%20Windows%20VS2019?branchName=master&jobName=Platform_CI&configuration=Platform_CI%20OVMF_IA32X64_RELEASE
.. |ap3264ru| image:: https://dev.azure.com/tianocore/edk2-ci-play/_apis/build/status/OVMF/OVMF%20Ubuntu%20GCC5?branchName=master&jobName=Platform_CI&configuration=Platform_CI%20OVMF_IA32X64_RELEASE
.. |ap3264n| image:: https://dev.azure.com/tianocore/edk2-ci-play/_apis/build/status/OVMF/OVMF%20Windows%20VS2019?branchName=master&jobName=Platform_CI&configuration=Platform_CI%20OVMF_IA32X64_NOOPT
.. |ap3264nu| image:: https://dev.azure.com/tianocore/edk2-ci-play/_apis/build/status/OVMF/OVMF%20Ubuntu%20GCC5?branchName=master&jobName=Platform_CI&configuration=Platform_CI%20OVMF_IA32X64_NOOPT

.. |ap3264fd| image:: https://dev.azure.com/tianocore/edk2-ci-play/_apis/build/status/OVMF/OVMF%20Windows%20VS2019?branchName=master&jobName=Platform_CI&configuration=Platform_CI%20OVMF_IA32X64_FULL_DEBUG
.. |ap3264fdu| image:: https://dev.azure.com/tianocore/edk2-ci-play/_apis/build/status/OVMF/OVMF%20Ubuntu%20GCC5?branchName=master&jobName=Platform_CI&configuration=Platform_CI%20OVMF_IA32X64_FULL_DEBUG
.. |ap3264fr| image:: https://dev.azure.com/tianocore/edk2-ci-play/_apis/build/status/OVMF/OVMF%20Windows%20VS2019?branchName=master&jobName=Platform_CI&configuration=Platform_CI%20OVMF_IA32X64_FULL_RELEASE
.. |ap3264fru| image:: https://dev.azure.com/tianocore/edk2-ci-play/_apis/build/status/OVMF/OVMF%20Ubuntu%20GCC5?branchName=master&jobName=Platform_CI&configuration=Platform_CI%20OVMF_IA32X64_FULL_RELEASE
.. |ap3264fn| replace:: Fails - Wontfix - `Bugzilla 2661`_
.. |ap3264fnu| image:: https://dev.azure.com/tianocore/edk2-ci-play/_apis/build/status/OVMF/OVMF%20Ubuntu%20GCC5?branchName=master&jobName=Platform_CI&configuration=Platform_CI%20OVMF_IA32X64_FULL_NOOPT

.. |br| replace:: :raw-html:`<br />`