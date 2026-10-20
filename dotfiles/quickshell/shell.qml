//@ pragma Env QSG_RENDER_LOOP=threaded
//@ pragma UseQApplication
//@ pragma AppId com.danklinux.dms-bar

import QtQuick
import Quickshell
import qs.Common
import qs.DCommon.Common as DC
import qs.Services
import qs.Modules.DBar

ShellRoot {
    id: root

    readonly property var defaultBarConfig: [{
        id: "default",
        name: "Main Bar",
        enabled: true,
        position: 0,
        screenPreferences: ["all"],
        showOnLastDisplay: true,
        leftWidgets: ["archLogo", "workspaceSwitcher", "focusedWindow"],
        centerWidgets: ["weather", "clock"],
        rightWidgets: ["systemTray", "clipboard", "cpuUsage", "memUsage", "notificationButton", "battery", "controlCenterButton"],
        spacing: 1,
        innerPadding: 0,
        widgetPadding: 3,
        fontScale: 0.75,
        iconScale: 0.75,
        bottomGap: 0,
        transparency: 1,
        widgetTransparency: 1,
        squareCorners: false,
        noBackground: false,
        gothCornersEnabled: false,
        borderEnabled: false,
        autoHide: false,
        visible: true,
        popupGapsAuto: true,
        popupGapsManual: 4,
        followInterfaceStyle: true,
        widgetFollowInterfaceStyle: true
    }]

    Component.onCompleted: {
        // Initialize singletons the bar depends on.
        void Theme;
        void SettingsData;
        void CompositorService;
        void BarWidgetService;
        void ShellLayout;
        void Log;
        void I18n;
        void Paths;
        void SessionService;
        void CacheData;
        void FilesService;

        // Wire the DCommon host used by theme/bar widgets.
        DC.Style.theme = Theme;
        DC.Style.settings = SettingsData;
        DC.I18n.backend = I18n;
        DC.Paths.backend = Paths;
        DC.Log.backend = Log;
        DC.Host.session = SessionService;
        DC.Host.cache = CacheData;
        DC.Host.files = FilesService;

        BarWidgetService.dankBarRepeater = barLoader;
    }

    // Load DBar through a Loader (like original DankMaterialShell does with ShellCore)
    Loader {
        id: barLoader
        active: true
        asynchronous: false
        sourceComponent: Component {
            DBar {
                barConfig: SettingsData.barConfigs && SettingsData.barConfigs.length > 0
                    ? SettingsData.barConfigs[0]
                    : root.defaultBarConfig[0]
                hyprlandOverviewLoader: null
            }
        }
        onLoaded: console.log("DEBUG: DBar Loader loaded, item:", item ? "yes" : "no")
        onStatusChanged: {
            if (status === Loader.Error) console.log("DEBUG: DBar Loader ERROR:", errorString);
        }
    }
}
