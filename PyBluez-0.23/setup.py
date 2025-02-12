#!/usr/bin/env python
import os
import platform
import sys
from setuptools import setup, Extension
from wheel.bdist_wheel import bdist_wheel as _bdist_wheel  # Ensure platform-specific wheel

try:
    from wheel.bdist_wheel import bdist_wheel as _bdist_wheel

    class impure_bdist_wheel(_bdist_wheel):
        def finalize_options(self):
            _bdist_wheel.finalize_options(self)
            self.root_is_pure = False

except ImportError:
    # If the wheel module isn't available, no problem
    impure_bdist_wheel = None

packages = ['bluetooth']
package_dir = {}
ext_modules = []
install_requires = []
package_data = {}
eager_resources = []
zip_safe = True

if sys.platform == 'win32':
    msbt_modules = (
            '_msbt',
            include_dirs:=[".\\port3"],
            libraries:=["WS2_32", "Irprops", "bthprops", "bthport", "bluetoothapis"],
            sources:=['msbt\\_msbt.c'],
    )

    # widcomm
    WC_BASE = os.path.join(os.getenv('ProgramFiles'), r"Widcomm\BTW DK\SDK")
    if os.path.exists(WC_BASE):
        ext_modules.append(
            Extension(
                'bluetooth._widcomm',
                include_dirs=["%s\\Inc" % WC_BASE, ".\\port3"],
                define_macros=[('_BTWLIB', None)],
                library_dirs=["%s\\Release" % WC_BASE],
                libraries=[
                    "WidcommSdklib",
                    "ws2_32",
                    "version",
                    "user32",
                    "Advapi32",
                    "Winspool",
                    "ole32",
                    "oleaut32",
                ],
                sources=[
                    "widcomm\\_widcomm.cpp",
                    "widcomm\\inquirer.cpp",
                    "widcomm\\rfcommport.cpp",
                    "widcomm\\rfcommif.cpp",
                    "widcomm\\l2capconn.cpp",
                    "widcomm\\l2capif.cpp",
                    "widcomm\\sdpservice.cpp",
                    "widcomm\\util.cpp",
                ],
            )
        )

elif sys.platform.startswith('linux'):
    ext_modules.append(
        Extension(
            'bluetooth._bluetooth',
            include_dirs=["./port3"],
            libraries=['bluetooth'],
            # extra_compile_args=['-O0'],  # Uncomment for debugging
            sources=['bluez/btmodule.c', 'bluez/btsdp.c'],
        )
    )

elif sys.platform.startswith("darwin"):
    packages.append('lightblue')
    package_dir['lightblue'] = 'macos'
    zip_safe = False

    if sys.version_info >= (3, 6):
        install_requires += ['pyobjc-core>=6', 'pyobjc-framework-Cocoa>=6']
    else:
        install_requires += ['pyobjc-core>=3.1,<6', 'pyobjc-framework-Cocoa>=3.1,<6']

    # Build the framework on macOS during build
    build_cmds = set(['bdist', 'bdist_egg', 'bdist_wheel'])
    if build_cmds & set(sys.argv):
        import subprocess

        subprocess.check_call([
            'xcodebuild',
            'install',
            '-project',
            'macos/LightAquaBlue/LightAquaBlue.xcodeproj',
            '-scheme',
            'LightAquaBlue',
            'DSTROOT=' + os.path.join(os.getcwd(), 'macos'),
            'INSTALL_PATH=/',
            'DEPLOYMENT_LOCATION=YES',
        ])

        # Collect framework files for inclusion in the package
        package_data['lightblue'] = []
        for path, _, files in os.walk('macos/LightAquaBlue.framework'):
            for f in files:
                include = os.path.join(path, f)[6:]  # Trim off 'macos/'
                package_data['lightblue'].append(include)

        # Allow using the framework from an egg
        eager_resources.append('macos/LightAquaBlue.framework')

else:
    raise Exception(
        f"This platform ({sys.platform}) is currently not supported by pybluez."
    )

setup(
    name='PyBluez',
    version='0.23',
    description='Bluetooth Python extension module',
    author="Albert Huang",
    author_email="ashuang@alum.mit.edu",
    url="http://pybluez.github.io/",
    ext_modules=ext_modules,
    packages=packages,
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Communications',
    ],
    download_url='https://github.com/pybluez/pybluez',
    long_description=(
        'Bluetooth Python extension module to allow Python developers to use '
        'system Bluetooth resources. PyBluez works with GNU/Linux, macOS, '
        'and Windows.'
    ),
    maintainer='Piotr Karulis',
    license='GPL',
    extras_require={'ble': ['gattlib==0.20150805']},
    package_dir=package_dir,
    install_requires=install_requires,
    package_data=package_data,
    eager_resources=eager_resources,
    zip_safe=zip_safe,
    cmdclass={'bdist_wheel': impure_bdist_wheel},
)
