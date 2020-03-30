﻿# @file
# Script to Build OVMF UEFI firmware
#
# Copyright (c) Microsoft Corporation.
# SPDX-License-Identifier: BSD-2-Clause-Patent
##
import os
import logging

from edk2toolext.environment import shell_environment
from edk2toolext.environment.uefi_build import UefiBuilder
from edk2toolext.invocables.edk2_platform_build import BuildSettingsManager
from edk2toolext.invocables.edk2_setup import SetupSettingsManager, RequiredSubmodule
from edk2toolext.invocables.edk2_update import UpdateSettingsManager
from edk2toollib.utility_functions import RunCmd


    # ####################################################################################### #
    #                                Common Configuration                                     #
    # ####################################################################################### #
class CommonPlatform():
    ''' Common settings for this platform.  Define static data here and use
        for the different parts of stuart
    '''
    PackagesSupported = ("OvmfPkg",)
    ArchSupported = ("IA32", "X64")
    TargetsSupported = ("DEBUG", "RELEASE", "NOOPT")
    Scopes = ('ovmf', 'edk2-build')
    WorkspaceRoot = os.path.realpath(os.path.join(
        os.path.dirname(os.path.abspath(__file__)), ".."))


    # ####################################################################################### #
    #                         Configuration for Update & Setup                                #
    # ####################################################################################### #
class SettingsManager(UpdateSettingsManager, SetupSettingsManager):

    def GetPackagesSupported(self):
        ''' return iterable of edk2 packages supported by this build.
        These should be edk2 workspace relative paths '''
        return CommonPlatform.PackagesSupported

    def GetArchitecturesSupported(self):
        ''' return iterable of edk2 architectures supported by this build '''
        return CommonPlatform.ArchSupported

    def GetTargetsSupported(self):
        ''' return iterable of edk2 target tags supported by this build '''
        return CommonPlatform.TargetsSupported

    def GetRequiredSubmodules(self):
        ''' return iterable containing RequiredSubmodule objects.
        If no RequiredSubmodules return an empty iterable
        '''
        rs = []
        rs.append(RequiredSubmodule(
            "ArmPkg/Library/ArmSoftFloatLib/berkeley-softfloat-3", False))
        rs.append(RequiredSubmodule(
            "CryptoPkg/Library/OpensslLib/openssl", False))
        return rs

    def SetArchitectures(self, list_of_requested_architectures):
        ''' Confirm the requests architecture list is valid and configure SettingsManager
        to run only the requested architectures.

        Raise Exception if a list_of_requested_architectures is not supported
        '''
        unsupported = set(list_of_requested_architectures) - set(self.GetArchitecturesSupported())
        if(len(unsupported) > 0):
            errorString = ( "Unsupported Architecture Requested: " + " ".join(unsupported))
            logging.critical( errorString )
            raise Exception( errorString )
        self.ActualArchitectures = list_of_requested_architectures

    def GetWorkspaceRoot(self):
        ''' get WorkspacePath '''
        return CommonPlatform.WorkspaceRoot

    def GetActiveScopes(self):
        ''' return tuple containing scopes that should be active for this process '''
        return CommonPlatform.Scopes


    # ####################################################################################### #
    #                         Actual Configuration for Platform Build                         #
    # ####################################################################################### #
class PlatformBuilder( UefiBuilder, BuildSettingsManager):
    def __init__(self):
        UefiBuilder.__init__(self)

    def AddCommandLineOptions(self, parserObj):
        ''' Add command line options to the argparser '''
        parserObj.add_argument('-a', "--arch", dest="build_arch", type=str, default="IA32,X64",
            help="Optional - CSV of architecture to build.  IA32 will use IA32 for Pei & Dxe. "
            "X64 will use X64 for both PEI and DXE.  IA32,X64 will use IA32 for PEI and "
            "X64 for DXE. default is IA32,X64")

    def RetrieveCommandLineOptions(self, args):
        '''  Retrieve command line options from the argparser '''

        shell_environment.GetBuildVars().SetValue("TARGET_ARCH"," ".join(args.build_arch.upper().split(",")), "From CmdLine")

        dsc = "OvmfPkg"
        if "IA32" in args.build_arch.upper().split(","):
            dsc += "Ia32"
        if "X64" in args.build_arch.upper().split(","):
            dsc += "X64"
        dsc += ".dsc"

        shell_environment.GetBuildVars().SetValue("ACTIVE_PLATFORM", f"OvmfPkg/{dsc}", "From CmdLine")

    def GetWorkspaceRoot(self):
        ''' get WorkspacePath '''
        return CommonPlatform.WorkspaceRoot

    def GetPackagesPath(self):
        ''' Return a list of workspace relative paths that should be mapped as edk2 PackagesPath '''
        return ()

    def GetActiveScopes(self):
        ''' return tuple containing scopes that should be active for this process '''
        return CommonPlatform.Scopes

    def GetName(self):
        ''' Get the name of the repo, platform, or product being build '''
        ''' Used for naming the log file, among others '''
        # check the startup nsh flag and if set then rename the log file.
        # this helps in CI so we don't overwrite the build log since running
        # uses the stuart_build command.
        if(shell_environment.GetBuildVars().GetValue("MAKE_STARTUP_NSH", "FALSE") == "TRUE"):
            return "OvmfPkg_With_Run"
        return "OvmfPkg"

    def GetLoggingLevel(self, loggerType):
        ''' Get the logging level for a given type
        base == lowest logging level supported
        con  == Screen logging
        txt  == plain text file logging
        md   == markdown file logging
        '''
        return logging.DEBUG

    def SetPlatformEnv(self):
        logging.debug("PlatformBuilder SetPlatformEnv")
        self.env.SetValue("PRODUCT_NAME", "OVMF", "Platform Hardcoded")
        self.env.SetValue("MAKE_STARTUP_NSH", "FALSE", "Default to false")
        self.env.SetValue("QEMU_HEADLESS", "FALSE", "Default to false")
        return 0

    def PlatformPreBuild(self):
        return 0

    def PlatformPostBuild(self):
        return 0

    def FlashRomImage(self):
        VirtualDrive = os.path.join(self.env.GetValue("BUILD_OUTPUT_BASE"), "VirtualDrive")
        os.makedirs(VirtualDrive, exist_ok=True)
        OutputPath_FV = os.path.join(self.env.GetValue("BUILD_OUTPUT_BASE"), "FV")
        QemuLogFile = os.path.join(self.env.GetValue("BUILD_OUT_TEMP"), "BootLog.txt")
        if os.path.exists(QemuLogFile):
            os.remove(QemuLogFile)

        # should move into plugin since Qemu can be used by lots of
        # platforms.  Issue is --FlashOnly doesn't run prebuild and thus plugin is skipped
        # Discuss this with PyTool project
        if os.path.isdir("\\Program Files\\qemu"):
            shell_environment.GetEnvironment().append_path(os.path.abspath("\\Program Files\\qemu"))
        else:
            logging.critical("QEMU folder not found in program Files")

        cmd = "qemu-system-x86_64"
        args =  "-pflash " + os.path.join(OutputPath_FV, "OVMF.fd")                 # path to firmware
        args += " -debugcon file:" + QemuLogFile                                    # write messages to file
        args += " -global isa-debugcon.iobase=0x402"                                # debug messages out thru virtual io port
        args += " -net none"                                                        # turn off network
        args += f" -drive file=fat:rw:{VirtualDrive},format=raw,media=disk"         # Mount disk with startup.nsh

        if (self.env.GetValue("QEMU_HEADLESS") == "TRUE"):
            args += " -display none"  # no graphics

        if (self.env.GetBuildValue("SMM_REQUIRE") == "1"):
            args += " -machine q35,smm=on" #,accel=(tcg|kvm)"
            #args += " -m ..."
            #args += " -smp ..."
            args += " -global driver=cfi.pflash01,property=secure,value=on"
            args += " -drive if=pflash,format=raw,unit=0,file=" + os.path.join(OutputPath_FV, "OVMF_CODE.fd") + ",readonly=on"
            args += " -drive if=pflash,format=raw,unit=1,file=" + os.path.join(OutputPath_FV, "copy_of_OVMF_VARS.fd")



        if (self.env.GetValue("MAKE_STARTUP_NSH") == "TRUE"):
            f = open(os.path.join(VirtualDrive, "startup.nsh"), "w")
            f.write("BOOT SUCCESS !!! \n")
            ## add commands here
            f.write("reset -s\n")
            f.close()

        RunCmd(cmd, args)
        return 0



