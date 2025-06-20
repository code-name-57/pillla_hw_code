from setuptools import find_packages, setup

package_name = 'pilla_hw'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='vish',
    maintainer_email='vish@wychar.com',
    description='ROS 2 nodes to interface with odrive nodes and the control algorithm',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'odrive_interface = pilla_hw.odrive_interface:main'
        ],
    },
)
