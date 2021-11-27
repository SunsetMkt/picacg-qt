import os
import shutil


class SettingValue:
    def __init__(self, tag, defaultV, isNeedReset, des=None):
        self.tag = tag                 # 分类
        self.value = defaultV          # 生效值
        self.setV = defaultV           # 设置的值
        self.defaultV = defaultV       # 默认值
        self.isNeedReset = isNeedReset       # 是否重启生效
        self.des = des          # 描述
        self.autoValue = 0      # 选自动时，自动生效的值
        self.name = ""

    def InitValue(self, value, name):
        value = self.GetSettingV(value, self.defaultV)
        self.value = value
        self.setV = value
        self.name = name
        return

    @staticmethod
    def GetSettingV(v, defV=None):
        try:
            if v:
                if isinstance(defV, int):
                    if v == "true" or v == "True":
                        return 1
                    elif v == "false" or v == "False":
                        return 0
                    return int(v)
                elif isinstance(defV, float):
                    return float(v)
                else:
                    return v
            return defV
        except Exception as es:
            from tools.log import Log
            Log.Error(es)
        return v

    def GetIndexV(self):
        if not isinstance(self.des, list):
            return ""
        if self.value >= len(self.des):
            return ""
        return self.des[self.value]

    def SetValue(self, value):
        if self.setV == value and self.value == value:
            return

        self.setV = value
        if not self.isNeedReset:
            self.value = value
            self.autoValue = 0
        Setting.SaveSettingV(self)

class Setting:
    # 通用设置
    IsUpdate = SettingValue("GeneraSetting", 1, False)
    Language = SettingValue("GeneraSetting", 0, False, ["Auto", "zh", "hk", "en"])  # ch-zh ch-hk eu
    ThemeIndex = SettingValue("GeneraSetting", 0, False, ["Auto", "light", "dark"])  #
    LogIndex = SettingValue("GeneraSetting", 0, False, ["warn", "info", "debug"])  # Warn Info Debug
    CoverSize = SettingValue("GeneraSetting", 100, False)  #
    ScaleLevel = SettingValue("GeneraSetting", 0, True, ["Auto", 100, 125, 150, 175, 200])

    # 代理设置
    IsHttpProxy = SettingValue("ProxySetting", 0, False)
    HttpProxy = SettingValue("ProxySetting", "", False)
    ChatProxy = SettingValue("ProxySetting", 0, False)
    PreferCDNIP = SettingValue("ProxySetting", "104.16.109.107", False)
    IsUseHttps = SettingValue("ProxySetting", 1, False)
    ProxySelectIndex = SettingValue("ProxySetting", 1, False)

    # 下载与缓存
    SavePath = SettingValue("DownloadSetting", "", False)

    # Waifu2x设置
    SelectEncodeGpu = SettingValue("Waifu2xSetting", "", True)
    Waifu2xThread = SettingValue("Waifu2xSetting", 2, True)

    # 封面 Waifu2x
    CoverIsOpenWaifu = SettingValue("Waifu2xSetting", 0, False)
    CoverMaxNum = SettingValue("Waifu2xSetting", 400, False)
    CoverLookModel = SettingValue("Waifu2xSetting", 0, False)
    CoverLookNoise = SettingValue("Waifu2xSetting", 3, False)
    CoverLookScale = SettingValue("Waifu2xSetting", 2.0, False)

    IsOpenWaifu = SettingValue("Waifu2xSetting", 0, False)
    LookMaxNum = SettingValue("Waifu2xSetting", 4096, False)
    LookModel = SettingValue("Waifu2xSetting", 0, False)
    LookNoise = SettingValue("Waifu2xSetting", 3, False)
    LookScale = SettingValue("Waifu2xSetting", 2.0, False)

    DownloadAuto = SettingValue("Waifu2xSetting", 0, False)
    DownloadModel = SettingValue("Waifu2xSetting", 0, False)
    DownloadNoise = SettingValue("Waifu2xSetting", 3, False)
    DownloadScale = SettingValue("Waifu2xSetting", 2.0, False)

    # 看图设置
    LookReadMode = SettingValue("ReadSetting", 1, False)
    LookReadFull = SettingValue("ReadSetting", 0, False)
    TurnSpeed = SettingValue("ReadSetting", 5000, False)
    ScrollSpeed = SettingValue("ReadSetting", 400, False)

    # Other
    UserId = SettingValue("Other", "", False)
    Password = SettingValue("Other", "", False)
    ChatSendAction = SettingValue("Other", 0, False, ["CtrlEnter", "Enter"])
    ScreenIndex = SettingValue("Other", 0, False)

    @staticmethod
    def InitLoadSetting():
        path = os.path.join(Setting.GetConfigPath(), "config.ini")
        from PySide6.QtCore import QSettings
        settings = QSettings(path, QSettings.IniFormat)
        for name in dir(Setting):
            setItem = getattr(Setting, name)
            if isinstance(setItem, SettingValue):
                value = settings.value(setItem.tag + "/" + name, setItem.defaultV)
                setItem.InitValue(value, name)
        from tools.log import Log
        Log.UpdateLoggingLevel()
        return

    @staticmethod
    def SaveSetting():
        path = os.path.join(Setting.GetConfigPath(), "config.ini")
        from PySide6.QtCore import QSettings
        settings = QSettings(path, QSettings.IniFormat)
        for name in dir(Setting):
            setItem = getattr(Setting, name)
            if isinstance(setItem, SettingValue):
                settings.setValue(setItem.tag + "/" + name, setItem.setV)
        return

    @staticmethod
    def SaveSettingV(setItem):
        path = os.path.join(Setting.GetConfigPath(), "config.ini")
        from PySide6.QtCore import QSettings
        settings = QSettings(path, QSettings.IniFormat)
        if isinstance(setItem, SettingValue) and setItem.name:
            settings.setValue(setItem.tag + "/" + setItem.name, setItem.setV)

    @staticmethod
    def Init():
        path = Setting.GetConfigPath()
        if not os.path.isdir(path):
            os.mkdir(path)
        Setting.CheckRepair()
        return

    @staticmethod
    def GetConfigPath():
        from PySide6.QtCore import QDir
        homePath = QDir.homePath()
        projectName = ".picacg"
        return os.path.join(homePath, projectName)

    @staticmethod
    def GetLogPath():
        return os.path.join(Setting.GetConfigPath(), "logs")

    @staticmethod
    def CheckRepair():
        try:
            fileList = ["download.db", "config.ini", "history.db"]
            for file in fileList:
                path = os.path.join(Setting.GetConfigPath(), file)
                if not os.path.isfile(path):
                    if os.path.isfile(file):
                        shutil.copyfile(file, path)
        except Exception as es:

            from tools.log import Log
            Log.Error(es)
