#!/usr/bin/env python3

import plistlib
import sys, os, shutil, tempfile

'''
format data field to single line;
'''
def format_data_string(plist_text):
    # Helper method to format <data> tags inline
    if not isinstance(plist_text,(list,tuple)):
        # Split it if it's not already a list
        plist_text = plist_text.split("\n")
    new_plist = []
    data_tag = ""
    types = ("</array>","</dict>")
    for i,x in enumerate(plist_text):
        x_stripped = x.strip()
        try:
            type_check = types[types.index(x_stripped)].replace("</","<")
            if plist_text[i-1].strip() == type_check:
                new_plist[-1] = x.replace("</","<").replace(">","/>")
                data_tag = ""
                continue
        except (ValueError, IndexError) as e:
            pass
        if x_stripped == "<data>":
            data_tag = x
            continue
        if not len(data_tag):
            # Not primed, and wasn't <data>
            new_plist.append(x)
            continue
        data_tag += x_stripped
        # Check for the end
        if x_stripped == "</data>":
            # Found the end, append it and reset
            new_plist.append(data_tag)
            data_tag = ""
    return "\n".join(new_plist)

'''
add ACPI > Quirks > EnableForAll False
'''
def add_key_to_plist(path):
    if not os.path.isfile(path):
        print(path, "is not existed.")
        return False

    plist_data = []
    with open(path, 'rb') as fp:
        plist_data = plistlib.load(fp)

    # Add key and value
    plist_data['ACPI']['Quirks']['EnableForAll'] = False

    # Dump to a string first
    plist_bytes = plistlib.dumps(plist_data, sort_keys=False).decode("utf-8")
    plist_text = format_data_string(plist_bytes);
    # At this point, we have a list of lines - with all <data> tags on the same line
    # write to file
    f = tempfile.NamedTemporaryFile(suffix='.plist', delete=False)
    if sys.version_info >= (3,0):
        plist_text = plist_text.encode("utf-8")
    f.write(plist_text)
    f.close()
    # Copy the temp over
    shutil.copy(f.name,path)
    os.unlink(f.name)
    return True


'''
Include/Acidanthera/Library/OcConfigurationLib.h
add line:
  _(BOOLEAN                     , EnableForAll        ,     , FALSE  , ()) \
below line:
#define OC_ACPI_QUIRKS_FIELDS(_, __) \
'''
def OcConfigurationLib_h(path):
    if not os.path.isfile(path):
        print(path, "is not existed.")
        return False
    string1 = '#define OC_ACPI_QUIRKS_FIELDS(_, __) \\'
    string2 = '  _(BOOLEAN                     , EnableForAll        ,     , FALSE  , ()) \\\n'

    file1 = open(path, "r")
    file2 = tempfile.NamedTemporaryFile(suffix='.h', delete=False)
    print(file2.name)

    # Loop through the file line by line
    for line in file1:
        file2.write(line.encode("utf-8"))
        # checking string is present in line or not
        if string1 in line:
            file2.write(string2.encode("utf-8"))

    # closing text file
    file1.close()
    file2.close()
    # Copy the temp over
    shutil.copy(file2.name,path)
    os.unlink(file2.name)


'''
Library/OcConfigurationLib/OcConfigurationLib.c
add line:
  OC_SCHEMA_BOOLEAN_IN ("EnableForAll",     OC_GLOBAL_CONFIG, Acpi.Quirks.EnableForAll),
below line:
mAcpiQuirksSchema[] = {
'''
def OcConfigurationLib_c(path):
    if not os.path.isfile(path):
        print(path, "is not existed.")
        return False
    string1 = 'mAcpiQuirksSchema[] = {'
    string2 = '  OC_SCHEMA_BOOLEAN_IN ("EnableForAll",     OC_GLOBAL_CONFIG, Acpi.Quirks.EnableForAll),\n'

    file1 = open(path, "r")
    file2 = tempfile.NamedTemporaryFile(suffix='.c', delete=False)
    print(file2.name)

    # Loop through the file line by line
    for line in file1:
        file2.write(line.encode("utf-8"))
        # checking string is present in line or not
        if string1 in line:
            file2.write(string2.encode("utf-8"))

    # closing text file
    file1.close()
    file2.close()
    # Copy the temp over
    shutil.copy(file2.name,path)
    os.unlink(file2.name)


'''
OpenCorePkg-0.8.0/Application/OpenCore/OpenCore.c
'''
def OpenCore_c(path):
    if not os.path.isfile(path):
        print(path, "is not existed.")
        return False

    string1 = '  EFI_CONSOLE_CONTROL_SCREEN_MODE  OldMode;'
    string2 = '''  CHAR16                           *DevicePathText;

  if (Chosen->DevicePath != NULL) {
    DevicePathText = ConvertDevicePathToText (Chosen->DevicePath, FALSE, FALSE);
    if ((Chosen->Type & OC_BOOT_APPLE_ANY) != 0 || StrStr(DevicePathText, L"\\\\System\\\\Library\\\\CoreServices\\\\boot.efi") != NULL) {
      if (!mOpenCoreConfiguration.Acpi.Quirks.EnableForAll) {
        DEBUG ((DEBUG_INFO, "OC: OcLoadAcpiSupport for macOS...\\n"));
        OcLoadAcpiSupport (&mOpenCoreStorage, &mOpenCoreConfiguration);
      }

      DEBUG ((DEBUG_INFO, "OC: OcLoadPlatformSupport...\\n"));
      OcLoadPlatformSupport (&mOpenCoreConfiguration, &mOpenCoreCpuInfo);
      DEBUG ((DEBUG_INFO, "OC: OcLoadDevPropsSupport...\\n"));
      OcLoadDevPropsSupport (&mOpenCoreConfiguration);
    }
    FreePool (DevicePathText);
  }
'''
    string31 = ' OcMiscLoadSystemReport (&mOpenCoreConfiguration, mStorageHandle);'
    string32 = '  DEBUG_CODE_END ();'
    string4 = '''  if (mOpenCoreConfiguration.Acpi.Quirks.EnableForAll) {
    DEBUG ((DEBUG_INFO, "OC: OcLoadAcpiSupport...\\n"));
    OcLoadAcpiSupport (&mOpenCoreStorage, &mOpenCoreConfiguration);
  }
'''
    string_comments = [
            ' DEBUG ((DEBUG_INFO, "OC: OcLoadAcpiSupport...\\n"));',
            ' OcLoadAcpiSupport (&mOpenCoreStorage, &mOpenCoreConfiguration);',
            ' DEBUG ((DEBUG_INFO, "OC: OcLoadPlatformSupport...\\n"));',
            ' OcLoadPlatformSupport (&mOpenCoreConfiguration, &mOpenCoreCpuInfo);',
            ' DEBUG ((DEBUG_INFO, "OC: OcLoadDevPropsSupport...\\n"));',
            ' OcLoadDevPropsSupport (&mOpenCoreConfiguration);'
            ]
    def is_comment_line(line):
        for comment in string_comments:
            if comment in line:
                return True
        return False


    file1 = open(path, "r")
    file2 = tempfile.NamedTemporaryFile(suffix='.c', delete=False)
    print(file2.name)

    flag = False
    # Loop through the file line by line
    for line in file1:
        if is_comment_line(line):
            file2.write(('  //' + line).encode("utf-8"))
        else:
            file2.write(line.encode("utf-8"))

        # checking string is present in line or not
        if string1 in line:
            file2.write(string2.encode("utf-8"))
        if string31 in line:
            flag = True
        if flag and string32 in line:
            file2.write(string4.encode("utf-8"))
            flag = False

    # closing text file
    file1.close()
    file2.close()
    # Copy the temp over
    shutil.copy(file2.name,path)
    os.unlink(file2.name)


if __name__ == '__main__':
    add_key_to_plist('Docs/Sample.plist')
    add_key_to_plist('Docs/SampleCustom.plist')

    OcConfigurationLib_h("Include/Acidanthera/Library/OcConfigurationLib.h")
    OcConfigurationLib_c("Library/OcConfigurationLib/OcConfigurationLib.c")
    OpenCore_c("Application/OpenCore/OpenCore.c")
