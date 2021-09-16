#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from shutil import copyfile
from conans import ConanFile, VisualStudioBuildEnvironment, AutoToolsBuildEnvironment, MSBuild, tools


class QtWebAppConan(ConanFile):
    name = "QtWebApp"
    version = "1.8.3"
    license = "LGPLv3"
    url = "https://github.com/Tereius/conan-QtWebApp.git"
    description = "QtWebApp HTTP Server in C++"
    author = "Bjoern Stresing"
    homepage = "http://stefanfrings.de/qtwebapp/"
    requires = "Qt/[^5.12]@tereius/stable"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = ("shared=True",
                        "Qt:shared=True",
                        "Qt:openssl=True",
                        "Qt:qtbase=True")

    def source(self):
        tools.get("http://stefanfrings.de/qtwebapp/QtWebApp.zip")
        tools.replace_in_file("QtWebApp/QtWebApp/QtWebApp.pro", "CONFIG(debug, debug|release)", "CONFIG(ignore, debug|release|ignore)")

    def build(self):

        tools.replace_in_file("QtWebApp/QtWebApp/QtWebApp.pro", "QMAKE_MAC_SDK = macosx10.10", "QMAKE_MAC_SDK = macosx%s" % self.settings.os.version)

        with tools.environment_append({"PATH": self.deps_cpp_info["Qt"].bin_paths}):
            if self.settings.compiler == "Visual Studio":
                env_build = VisualStudioBuildEnvironment(self)
                with tools.environment_append(env_build.vars):
                    vcvars = tools.vcvars_command(self.settings)
                    self.run('%s && qmake -r -tp vc QtWebApp.pro' % (vcvars), cwd="QtWebApp/QtWebApp")
                    ms_env = MSBuild(self)
                    ms_env.build(project_file="QtWebApp/QtWebApp/QtWebApp.vcxproj", upgrade_project=False)
            else:
                autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
                envvars = autotools.vars
                envvars["LD_LIBRARY_PATH"] = "".join([i+":" for i in autotools.library_paths])
                envvars["LD_RUN_PATH"] = "".join([i+":" for i in autotools.library_paths])
                with tools.environment_append(envvars):
                    self.run('qmake QtWebApp.pro', win_bash=tools.os_info.is_windows, cwd="QtWebApp/QtWebApp")
                    self.run("make -j %s" % tools.cpu_count(), win_bash=tools.os_info.is_windows, cwd="QtWebApp/QtWebApp")
            

    def package(self):

        build_type = "debug" if self.settings.build_type == "Debug" else "release"
        if self.settings.compiler == "Visual Studio":
            self.copy("QtWebApp/QtWebApp/" + build_type + "*.lib", dst="lib", keep_path=False)
            self.copy("QtWebApp/QtWebApp/" + build_type + "*.dll", dst="lib", keep_path=False)
        else:
            self.copy("QtWebApp/QtWebApp/*.so*", dst="lib", keep_path=False, symlinks=True)
        self.copy("QtWebApp/QtWebApp/httpserver/*.h", dst="include/httpserver", keep_path=False)
        self.copy("QtWebApp/QtWebApp/logging/*.h", dst="include/logging", keep_path=False)
        self.copy("QtWebApp/QtWebApp/templateengine/*.h", dst="include/templateengine", keep_path=False)
