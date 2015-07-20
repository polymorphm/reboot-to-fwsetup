# -*- mode: python; coding: utf-8 -*-
#
# Copyright (c) 2015 Andrej Antonov <polymorphm@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

assert str is not bytes

import os, os.path
import struct

EFI_VARIABLE_NON_VOLATILE = 0x00000001
EFI_VARIABLE_BOOTSERVICE_ACCESS = 0x00000002
EFI_VARIABLE_RUNTIME_ACCESS = 0x00000004
EFI_VARIABLE_HARDWARE_ERROR_RECORD = 0x00000008
EFI_VARIABLE_AUTHENTICATED_WRITE_ACCESS = 0x00000010

EFI_STRUCT_FORMAT = '=IQ'

EFI_OS_INDICATIONS_VAR_PATH = '/sys/firmware/efi/efivars/OsIndications-8be4df61-93ca-11d2-aa0d-00e098032b8c'
EFI_OS_INDICATIONS_SUPPORTED_VAR_PATH = '/sys/firmware/efi/efivars/OsIndicationsSupported-8be4df61-93ca-11d2-aa0d-00e098032b8c'
EFI_OS_INDICATIONS_BOOT_TO_FW_UI = 0x0000000000000001

class NotSupportedError(Exception):
    pass

def support_check():
    error_text = 'firmware is not supported for rebooting to UEFI Setup UI'
    
    if not os.path.isfile(EFI_OS_INDICATIONS_SUPPORTED_VAR_PATH):
        raise NotSupportedError(error_text)
    
    with open(EFI_OS_INDICATIONS_SUPPORTED_VAR_PATH, mode='rb') as fd:
        raw_efi_value = fd.read()
    
    efi_prefix, efi_value = struct.unpack(EFI_STRUCT_FORMAT, raw_efi_value)
    if efi_value & EFI_OS_INDICATIONS_BOOT_TO_FW_UI != EFI_OS_INDICATIONS_BOOT_TO_FW_UI:
        raise NotSupportedError(error_text)

def reboot_to_fwsetup():
    if os.path.isfile(EFI_OS_INDICATIONS_VAR_PATH):
        with open(EFI_OS_INDICATIONS_VAR_PATH, mode='rb') as fd:
            raw_efi_value = fd.read()
        
        efi_prefix, efi_value = struct.unpack(EFI_STRUCT_FORMAT, raw_efi_value)
    else:
        efi_prefix = 0
        efi_value = 0
    
    new_efi_prefix = \
            efi_prefix | \
            EFI_VARIABLE_NON_VOLATILE | \
            EFI_VARIABLE_BOOTSERVICE_ACCESS | \
            EFI_VARIABLE_RUNTIME_ACCESS
    new_efi_value = efi_value | EFI_OS_INDICATIONS_BOOT_TO_FW_UI
    new_raw_efi_value = struct.pack(EFI_STRUCT_FORMAT, new_efi_prefix, new_efi_value)
    
    with open(EFI_OS_INDICATIONS_VAR_PATH, mode='wb') as fd:
        fd.write(new_raw_efi_value)
