import QtQuick
import qs.Common
import qs.Services
import qs.Widgets
import qs.DCommon.Widgets as DCommon

BasePill {
    id: root

    property var widgetData: null

    content: Component {
        Item {
            implicitWidth: root.contentThickness
            implicitHeight: root.contentThickness

            DCommon.DSVGIcon {
                id: archIcon
                anchors.fill: parent
                size: Theme.barIconSize(root.barThickness, -6, root.barConfig?.maximizeWidgetIcons, root.barConfig?.iconScale)
                source: "/usr/share/pixmaps/archlinux-logo.svg"
                colorOverride: Theme.widgetTextColor
            }
        }
    }
}
