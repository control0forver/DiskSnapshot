
APP_NAME = 'DiskSnapshot'
APP_VERSION = '1.0.0'
APP_TAG = 'Release'

def _get_simplified_tag_string():
    if APP_TAG == 'Release':
        return ''
    else:
        return f'[{APP_TAG}] '

def GetAppTitle():
    return f'{_get_simplified_tag_string()}{APP_NAME} v{APP_VERSION}'

def GetAppDescription(): return f'{GetAppTitle()}\n\n{APP_NAME} - Fast binary snapshot tool for directories.\n\nAuthor: TheLGF\nVersion: {APP_VERSION}'
def GetAppLicenseDescription(): return f'{APP_NAME} is licensed under GPLv3.\nCopyright (c) 2025 TheLGF (LGF-Studio™)'
