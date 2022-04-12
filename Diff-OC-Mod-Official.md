# Modify OpenCore To Load ACPI when boot macOS

## source code

```bash
find . -name "*.orig"
```

### Modified for boot os except macOS without ACPI loading --->

```
./Include/Acidanthera/Library/OcConfigurationLib.h
./Library/OcConfigurationLib/OcConfigurationLib.c
./Application/OpenCore/OpenCore.c
```

### Official Version:

```
./Include/Acidanthera/Library/OcConfigurationLib.h.orig
./Library/OcConfigurationLib/OcConfigurationLib.c.orig
./Application/OpenCore/OpenCore.c.orig
```

### Diffs:

```bash
$ diff ./Include/Acidanthera/Library/OcConfigurationLib.h.orig ./Include/Acidanthera/Library/OcConfigurationLib.h
82a83
>   _(BOOLEAN                     , EnableForAll        ,     , FALSE  , ()) \
```

```bash
$ diff ./Library/OcConfigurationLib/OcConfigurationLib.c.orig ./Library/OcConfigurationLib/OcConfigurationLib.c
145a146,148
>   OC_SCHEMA_BOOLEAN_IN ("EnableForAll",     OC_GLOBAL_CONFIG, Acpi.Quirks.EnableForAll),
```

```bash
$ diff ./Application/OpenCore/OpenCore.c.orig ./Application/OpenCore/OpenCore.c
91a92,93
>   CHAR16                           *DevicePathText;
92a95,110
>   if (Chosen->DevicePath != NULL) {
>     DevicePathText = ConvertDevicePathToText (Chosen->DevicePath, FALSE, FALSE);
>     if ((Chosen->Type & OC_BOOT_APPLE_ANY) != 0 || StrStr(DevicePathText, L"\\System\\LibraryCoreServices\\boot.efi") != NULL) {
>       if (!mOpenCoreConfiguration.Acpi.Quirks.EnableForAll) {
>         DEBUG ((DEBUG_INFO, "OC: OcLoadAcpiSupport for macOS...\n"));
>         OcLoadAcpiSupport (&mOpenCoreStorage, &mOpenCoreConfiguration);
>       }
>
>       DEBUG ((DEBUG_INFO, "OC: OcLoadPlatformSupport...\n"));
>       OcLoadPlatformSupport (&mOpenCoreConfiguration, &mOpenCoreCpuInfo);
>       DEBUG ((DEBUG_INFO, "OC: OcLoadDevPropsSupport...\n"));
>       OcLoadDevPropsSupport (&mOpenCoreConfiguration);
>     }
>     FreePool (DevicePathText);
>   }
152,157c170,181
<   DEBUG ((DEBUG_INFO, "OC: OcLoadAcpiSupport...\n"));
<   OcLoadAcpiSupport (&mOpenCoreStorage, &mOpenCoreConfiguration);
<   DEBUG ((DEBUG_INFO, "OC: OcLoadPlatformSupport...\n"));
<   OcLoadPlatformSupport (&mOpenCoreConfiguration, &mOpenCoreCpuInfo);
<   DEBUG ((DEBUG_INFO, "OC: OcLoadDevPropsSupport...\n"));
<   OcLoadDevPropsSupport (&mOpenCoreConfiguration);
---
>   if (mOpenCoreConfiguration.Acpi.Quirks.EnableForAll) {
>     DEBUG ((DEBUG_INFO, "OC: OcLoadAcpiSupport...\n"));
>     OcLoadAcpiSupport (&mOpenCoreStorage, &mOpenCoreConfiguration);
>   }
>   // DEBUG ((DEBUG_INFO, "OC: OcLoadAcpiSupport...\n"));
>   // OcLoadAcpiSupport (&mOpenCoreStorage, &mOpenCoreConfiguration);
>   // DEBUG ((DEBUG_INFO, "OC: OcLoadPlatformSupport...\n"));
>   // OcLoadPlatformSupport (&mOpenCoreConfiguration, &mOpenCoreCpuInfo);
>   // DEBUG ((DEBUG_INFO, "OC: OcLoadDevPropsSupport...\n"));
>   // OcLoadDevPropsSupport (&mOpenCoreConfiguration);
```

### config.plist:

Path: `ACPI/Quirks/EnableForAll/false`

```bash
$ diff ~/Desktop/EFI-Official/OC/config.plist ~/Desktop/EFI-Mod/OC/config.plist
524,525d523
<           <key>EnableForAll</key>
<           <false/>
```

## Following Steps:

1. clone or download OpenCorePkg source code from github;
2. modify differences in files listed above;
3. Install nasm, `brew install nasm`;
4. Assure you can visit github, enable http/https proxy and git proxy;
5. cd ${OpenCoreSourceCodePath}, `./build_oc.cmd`;
6. copy your EFI ACPI/config.plist/kexts to modified OC EFI directory;
7. add EnableForAll to Config.plist(ACPI/Quirks)
7. backup your EFI and replace with modified OC EFI;
8. reboot;
