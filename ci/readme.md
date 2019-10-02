# Edk2 Continuous Integration

## Current Status

| Package | Status | Known Issues |
| :----   | :----- | :----             |
| MdePkg | Passing |  |
| MdeModulePkg | Passing | DxeIpl dependency on ArmPkg, Missing Visual Studio AARCH64/ARM support |
| CryptoPkg | Passing |  |
|SecurityPkg|Passing||
| UefiCpuPkg | Passing |  |
| NetworkPkg | Passing ||
| PcAtChipsetPkg | Passing ||
| ShellPkg | Passing ||
|FmpDevicePkg|Passing||
|FatPkg|Passing||

## Background

While a number of CI solutions exist, this proposal will focus on the usage of Azure Dev Ops and Build Pipelines. For demonstration, a sample [TianoCore repo](https://github.com/spbrogan/edk2.git) (branch edk2-ci) and [Dev Ops Pipeline](https://dev.azure.com/tianocore/edk2-ci-play/_build?definitionId=14) have been set up.

Furthermore, this proposal will leverage the TianoCore python tools PIP modules: [library](https://pypi.org/project/edk2-pytool-library/) and [extensions](https://pypi.org/project/edk2-pytool-extensions/) (with repos located [here](https://github.com/tianocore/edk2-pytool-library) and [here](https://github.com/tianocore/edk2-pytool-extensions)).

The primary execution flows can be found in the `ci/AzurePipelines/Windows-VS2019-Ci.yml` and `ci/AzurePipelines/Ubuntu-GCC5-Ci.yml` files. These YAML files are consumed by the Azure Dev Ops Build Pipeline and dictate what server resources should be used, how they should be configured, and what processes should be run on them. An overview of this schema can be found [here](https://docs.microsoft.com/en-us/azure/devops/pipelines/yaml-schema?view=azure-devops&tabs=schema).

Inspection of these files reveals the EDKII Tools commands that make up the primary processes for the CI build: 'stuart_setup', 'stuart_update', and 'stuart_ci_build'. These commands come from the EDKII Tools PIP modules and are configured as described below. More documentation on the stuart tools can be found [here](https://github.com/tianocore/edk2-pytool-extensions/blob/master/docs/using.md) and [here](https://github.com/tianocore/edk2-pytool-extensions/blob/master/docs/features/feature_invocables.md).

## Configuration

Configuration of the CI process consists of (in order of precedence):

* command-line arguments passed in via the Pipeline YAML
* a per-package configuration file (e.g. `<package-name>.ci.yaml`) that is detected by the CI system in EDKII Tools.
* a global configuration Python module (e.g. `CISetting.py`) passed in via the command-line

The global configuration file is described in [this readme](https://github.com/tianocore/edk2-pytool-extensions/blob/master/docs/usability/using_settings_manager.md) from the EDKII Tools documentation. This configuration is written as a Python module so that decisions can be made dynamically based on command line parameters and codebase state.

The per-package configuration file can override most settings in the global configuration file, but is not dynamic. This file can be used to skip or customize tests that may be incompatible with a specific package. By default, the global configuration will try to run all tests on all packages.

## Current Test Capabilities

All CI tests are instances of EDKII Tools plugins. Documentation on the plugin system can be found [here](https://github.com/tianocore/edk2-pytool-extensions/blob/master/docs/usability/using_plugin_manager.md) and [here](https://github.com/tianocore/edk2-pytool-extensions/blob/master/docs/features/feature_plugin_manager.md). Upon invocation, each plugin will be passed the path to the current package under test and a dictionary containing its targeted configuration, as assembled from the command line, per-package configuration, and global configuration.

Note: CI plugins are considered unique from build plugins and helper plugins, even though some CI plugins may execute steps of a build.

In the example, these plugins live alongside the code under test (in the `BaseTools` directory), but may be moved to the 'edk2-test' repo if that location makes more sense for the community.

### Module Inclusion Test - DscCompleteCheck

This test scans all available modules (via INF files) and compares them to the package-level DSC file for the package each module is contained within. The test considers it an error if any module does not appear in the `Components` section of at least one package-level DSC (indicating that it would not be built if the package were built).

### Code Compilation Test - CompilerPlugin

Once the Module Inclusion Test has verified that all modules would be built if all package-level DSCs were built, the Code Compilation Test simply runs through and builds every package-level DSC on every toolchain and for every architecture that is supported. Any module that fails to build is considered an error.

### GUID Uniqueness Test - GuidCheck

This test works on the collection of all packages rather than an individual package. It looks at all FILE_GUIDs and GUIDs declared in DEC files and ensures that they are unique for the codebase. This prevents, for example, accidental duplication of GUIDs when using an existing INF as a template for a new module.

### Cross-Package Dependency Test - DependencyCheck

This test compares the list of all packages used in INFs files for a given package against a list of "allowed dependencies" in plugin configuration for that package. Any module that depends on a disallowed package will cause a test failure.

### Library Declaration Test - LibraryClassCheck

This test looks at all library header files found in a package's `Include/Library` directory and ensures that all files have a matching LibraryClass declaration in the DEC file for the package. Any missing declarations will cause a failure.

### Invalid Character Test - CharEncodingCheck

This test scans all files in a package to make sure that there are no invalid Unicode characters that may cause build errors in some character sets/localizations.

## Future investments

* MacOS/xcode support
* clang/LLVM support
* Extensible private/closed source platform reporting
* Platform builds and validation
* Host based unit testing
