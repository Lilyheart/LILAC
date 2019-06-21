"""
Export data related to the code in various forms.  Used for debugging only and not part of the code base.
"""
# For excel
from tempfile import TemporaryFile
from xlwt import Workbook
import numpy as np
import pandas as pd
# For code to csv
import os
import inspect
import importlib


def export_scans(scans, filename="Scans"):
    """
    Exports a list of :class:`~scan.Scan` objects to Excel

    :param scans: A list of the scans to export
    :type scans: Scans
    :param filename: The filename to store the file as
    :type filename: str
    """
    np.set_printoptions(linewidth=np.inf)
    book = Workbook()
    for i in range(len(scans)):
        # get scan
        str_scan = repr(scans[i]).splitlines()
        # create sheet
        sheet = book.add_sheet("Sheet " + str(i))
        # store each line
        for j in range(len(str_scan)):
            line = str_scan[j].split(";")
            for k in range(len(line)):
                sheet.write(j, k, str(line[k]))

    book.save(filename + ".xls")
    book.save(TemporaryFile())

    print("Exported Scans (" + filename + ")")


def export_code_structure(filename="CodeStructure"):
    """
    Prints to the console the code structure of the package this export module is located in.  It also saves the
    information as a two csv files (one for top level functions and one for Class.methods) located in this same folder.

    :param filename: The filename suffix to store the file as
    :type filename: str
    """
    print("Exporting data and will save as " + filename)
    if __name__ == '__main__':
        package_path = os.getcwd()
    else:
        print("Not yet coded for import calls")
        return 1

    module_functions_csv = []
    module_class_methods_csv = []
    # for each directory walk to
    for path_root, path_dir, path_file in os.walk(package_path):
        # determine package path
        mod_pkg_path = path_root.replace(package_path, "").replace("/", ".").replace("\\", ".")[1:]
        # add period for subpackages
        if len(mod_pkg_path) > 0:
            mod_pkg_path += "."
        # for each file in each directory walk to
        for f in path_file:
            # test if python file
            if f.endswith('.py'):
                if f == "fast_dp_setup.py":
                    print("pass")
                    continue
                # test file size
                full_file_path = path_root + "/" + f
                if (os.path.getsize(full_file_path)) != 0:
                    # get module name for importing
                    curr_file = (mod_pkg_path + f)[:-3]
                    print(" ========= Information for module \"%s\" =========" % curr_file)
                    # import module for inspection
                    imported_module = importlib.import_module(curr_file)
                    ##################################################
                    # get any top level functions
                    ##################################################
                    functions = inspect.getmembers(imported_module, predicate=inspect.isfunction)
                    if len(functions) != 0:
                        print("    Module Functions:")
                        for top_func_name, top_func_value in functions:
                            if inspect.getfile(top_func_value) == full_file_path:
                                print("        %s" % top_func_name)
                                module_functions_csv.append("%s,%s" % (curr_file, top_func_name))
                    ##################################################
                    # dig through the classes
                    ##################################################
                    classes = inspect.getmembers(imported_module, predicate=inspect.isclass)
                    # Check to see if inherited or in file
                    classes = [(n, v) for (n, v) in classes if inspect.getfile(v) == full_file_path + "c"]
                    # print the class details
                    if len(classes) != 0:
                        print("    Module Classes:")
                        for class_name, class_value in classes:
                            print("        %s" % class_name)
                            module_class_methods_csv.append("%s,%s,%s" % (curr_file, class_name, "-"))
                            # dig through the methods
                            class_methods = inspect.getmembers(class_value, predicate=inspect.ismethod)
                            # Check to see if inherited or in file
                            class_methods = [(n, v) for (n, v) in class_methods if n in class_value.__dict__]
                            if len(class_methods) != 0:
                                print("            Class Methods:")
                                for m_name, m_value in class_methods:
                                    print("                %s" % m_name)
                                    module_class_methods_csv.append("%s,%s,%s" % (curr_file, class_name, m_name))

        header = ["module,module_functions"]
        df = pd.DataFrame(np.asarray(module_functions_csv), columns=header)
        df.to_csv(filename + "_funcs.csv", index=False, quoting=0)

        header = ["module,module_classes,class_methods"]
        df = pd.DataFrame(np.asarray(module_class_methods_csv), columns=header)
        df.to_csv(filename + "_methods.csv", index=False, quoting=0)


# When running script directly
if __name__ == '__main__':
    export_code_structure()
