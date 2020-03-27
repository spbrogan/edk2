# Building OVMF with EDK2 Pytools

## Summary

This README-pytools.md summarizes how to _build_ OvmfPkg using the Pytools build system.  For general documentation on OvmfPkg, refer to the [local README](./README).

## Setup

### The Usual EDK2 Build Setup

* [Download & Install Python 3.x](https://www.python.org/downloads/)
* [Download & Install git](https://git-scm.com/download/)
* [Configure Git for EDK II](https://github.com/tianocore/tianocore.github.io/wiki/Windows-systems#github-help)
* [Download/Checkout the EDK II source tree from Github](https://github.com/tianocore/tianocore.github.io/wiki/Windows-systems#download)
  * **NOTE:** Do _not_ follow the EDK II Compile Tools and Build instructions, see below...

### Differences from EDK Classic Build Setup

* Build BaseTools using "`C:\git\edk2>python BaseTools\Edk2ToolsBuild.py [-t <ToolChainTag>]`"
  * This replaces "`edksetup Rebuild`" from the classic build system
  * For Windows `<ToolChainTag>` examples, refer to [Windows ToolChain Matrix](https://github.com/tianocore/tianocore.github.io/wiki/Windows-systems-ToolChain-Matrix), defaults to `VS2017` if not specified
* **No Action:** Submodule initialization and manual installation/setup of NASM and iASL is __not__ required, it is handled by the Pytools build system

### Install & Configure Pytools for OvmfPkg

* Install Pytools
  * `pip install --upgrade -r pip-requirements.txt`
* Initialize & Update Submodules
  * `stuart_setup -c OvmfPkg\PlatformBuild.py`
* Initialize & Update Dependencies (e.g. iASL & NASM)
  * `stuart_update -c OvmfPkg\PlatformBuild.py`

## Building

OVMF has [3 versions](https://github.com/tianocore/tianocore.github.io/wiki/How-to-build-OVMF#choosing-which-version-of-ovmf-to-build).  To build them using Pytools:

First set the `TOOL_CHAIN_TAG` via environment variable, Conf/target.txt, or pass it on the command-lines below using "`TOOL_CHAIN_TAG=<value>`" syntax.

| Platform | Commandline |
| -------- | ----------- |
| OvmfPkgIa32X64.dsc | `stuart_build -c OvmfPkg\PlatformBuild.py [TOOL_CHAIN_TAG=<TOOL_CHAIN_TAG>]`<BR>__OR__<BR>`stuart_build -c OvmfPkg\PlatformBuild.py -a IA32,X64 [TOOL_CHAIN_TAG=<TOOL_CHAIN_TAG>]`         |
| OvmfPkgIa32.dsc    | `stuart_build -c OvmfPkg\PlatformBuild.py -a IA32 [TOOL_CHAIN_TAG=<TOOL_CHAIN_TAG>]` |
| OvmfPkgX64.dsc     | `stuart_build -c OvmfPkg\PlatformBuild.py -a X64 [TOOL_CHAIN_TAG=<TOOL_CHAIN_TAG>]`  |

__NOTE:__  configuring ACTIVE_PLATFORM and TARGET_ARCH in Conf/target.txt is _not_ required.  This environment is set by PlatformBuild.py based upon the "```[-a <TARGET_ARCH>]```" parameter.

## Passing Build Defines

To pass build defines through stuart_build, prepend `BLD_*_` to the define name and pass it on the commandline.  
stuart_build [currently requires values to be assigned](https://github.com/tianocore/edk2-pytool-extensions/issues/128), so add an `=1` suffix for bare defines.  
For example, to enable the Intel E1000 NIC, instead of the traditional "-D E1000_ENABLE", the stuart_build command-line would be:

`stuart_build -c OvmfPkg/PlatformBuild.py BLD_*_E1000_ENABLE=1`

## References

* [Installing Pytools](https://github.com/tianocore/edk2-pytool-extensions/blob/master/docs/using.md#installing)
* For each workspace, consider creating & using a [Python Virtual Environment](https://docs.python.org/3/library/venv.html).  For example <https://microsoft.github.io/mu/CodeDevelopment/prerequisites/#workspace-virtual-environment-setup-process>
* [stuart_build commandline parser](https://github.com/tianocore/edk2-pytool-extensions/blob/56f6a7aee09995c2f22da4765e8b0a29c1cbf5de/edk2toolext/edk2_invocable.py#L109)
