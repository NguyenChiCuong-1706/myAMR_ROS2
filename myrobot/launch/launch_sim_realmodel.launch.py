import os
import xacro

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch_ros.actions import Node



def generate_launch_description():

    package_name='myrobot'
    gazebo_params_file = os.path.join(get_package_share_directory(package_name), 'config', 'gazebo_params.yaml')
    robot_localization_params_file = os.path.join(get_package_share_directory(package_name), 'config', 'robot_localization_param.yaml')
    world_path = os.path.join(get_package_share_directory(package_name), 'worlds', 'warehouse.world')

    rsp_node = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory(package_name),'launch','rsp.launch.py'
                )]), launch_arguments={'use_sim_time': 'true'}.items()
    )


    gazebo = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py')]),
                    launch_arguments={'world': world_path}.items()
                    # launch_arguments={'world': world_path, 'extra_gazebo_args': '--ros-args --params-file ' + gazebo_params_file}.items()
             )

    spawn_entity = Node(
        package='gazebo_ros', 
        executable='spawn_entity.py',
        arguments=[
        '-topic', '/robot_description',
        '-entity', 'my_bot',
        '-x', '0',  # X-coordinate
        '-y', '0',  # Y-coordinate
        '-z', '0.5',  # Z-coordinate
        ],
    output='screen'
    )   

    diff_drive_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["diff_cont"],
    )

    joint_broad_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_broad"],
    )


    ekf_localization_odom= Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_localization_odom',
        output='screen',
        parameters=[robot_localization_params_file]
    )


    return LaunchDescription([
        rsp_node,
        gazebo,
        spawn_entity,
        diff_drive_spawner,
        joint_broad_spawner,

        ekf_localization_odom
    ])