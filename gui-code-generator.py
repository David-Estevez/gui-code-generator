import os
import logging
import xml.etree.ElementTree as etree
from collections import defaultdict

import begin

ranged_classes = ('QSlider', 'QDoubleSpinBox')

template = """
\"\"\"
{className}
---------------------

Frontend for the {className}
\"\"\"

import os, sys

from PySide import QtCore,QtGui
from PySide import QtUiTools


def load_ui(file_name, where=None):
    \"\"\"
    Loads a .UI file into the corresponding Qt Python object
    :param file_name: UI file path
    :param where: Use this parameter to load the UI into an existing class (i.e. to override methods)
    :return: loaded UI
    \"\"\"
    # Create a QtLoader
    loader = QtUiTools.QUiLoader()

    # Open the UI file
    ui_file = QtCore.QFile(file_name)
    ui_file.open(QtCore.QFile.ReadOnly)

    # Load the contents of the file
    ui = loader.load(ui_file, where)

    # Close the file
    ui_file.close()

    return ui

class {className}(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

{initVariables}

        self.setupUI()
        self.resetValues()


    def setupUI(self):
        # Load UI and set it as main layout
        ui_file_path = os.path.join(os.path.realpath(os.path.dirname(__file__)), 'templates', '{ui_file_name}')
        main_widget = load_ui(ui_file_path, self)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(main_widget)
        self.setLayout(layout)

        # Get a reference to all required widgets
{referenceToWidgets}

        # Configure widget ranges:
        max_float = sys.float_info.max  # Just in case you need to use float max as a limit
{widgetRanges}

        # Connect to signals:
        
        # <<connect to signals here>>

    def resetValues(self):
{resetValues}

def main():
    # Create Qt app
    app = QtGui.QApplication(sys.argv)

    # Create the widget and show it
    gui = {className}()
    gui.show()

    # Run the app
    sys.exit(app.exec_())
    
if __name__ == \'__main__\':
    main()
"""

@begin.start(auto_convert=True)
@begin.logging
def main(ui_file: 'UI to generate python code from'):
    # Parse input file
    tree = etree.parse(ui_file)

    # Get main widget and GUI name
    root = tree.getroot()
    main_widget = root.findall('widget')[0]
    name = main_widget.attrib['name']
    logging.debug(name)

    widgets = defaultdict(list)
    for i, child in enumerate(main_widget.findall('.//widget')):
        widget_name, widget_class = child.attrib['name'], child.attrib['class']
        logging.debug("{}, {}:{}".format(i, widget_name, widget_class))
        widgets[widget_class].append(widget_name)

    # Generate some code (spaces are required to keep Python code indented and happy)
    initVariables = '\n'.join(['        self.{} = None'.format(string) for names in widgets.values() for string in names])
    logging.debug("Init variables: ")
    logging.debug(initVariables)

    referenceToWidgets = '\n'.join(['        self.{} = self.findChild(QtGui.{}, \'{}\')'.format(string, wclass, string)
                                    for wclass, names in widgets.items() for string in names])
    logging.debug("Reference to widgets: ")
    logging.debug(referenceToWidgets)

    widgetRanges = '\n'.join(['        self.{}.setMinimum(0)\n        self.{}.setMaximum(100)'.format(string, string)
                              for wclass, names in widgets.items() for string in names if wclass in ranged_classes])
    logging.debug("Widget ranges: ")
    logging.debug(widgetRanges)

    resetValues = '\n'.join(['        self.{}.setValue(0)'.format(string)
                             for wclass, names in widgets.items() for string in names if wclass in ranged_classes])
    logging.debug("Reset values: ")
    logging.debug(resetValues)

    # Put values in template and write to file
    ui_file_name = os.path.split(ui_file)[-1]
    text = template.format(className=name, ui_file_name=ui_file_name, initVariables=initVariables,
                           referenceToWidgets=referenceToWidgets, widgetRanges=widgetRanges, resetValues=resetValues)

    with open(os.path.basename(ui_file_name)+'.py', 'w') as f:
        f.write(text)