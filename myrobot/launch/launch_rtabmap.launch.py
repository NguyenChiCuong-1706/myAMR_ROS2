from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch.conditions import IfCondition, UnlessCondition
from launch_ros.actions import Node


def generate_launch_description():

    use_sim_time = LaunchConfiguration('use_sim_time')
    qos = LaunchConfiguration('qos')
    localization = LaunchConfiguration('localization')

    parameters = {
        'frame_id': 'base_footprint',
        'odom_frame_id': 'odom',
        'map_frame_id': 'map',
        'use_sim_time': use_sim_time,

        # Sensors
        'subscribe_depth': True,
        'subscribe_scan': True,        # ← add LiDAR
        'subscribe_scan_cloud': False,
        'subscribe_rgbd': False,

        # QoS
        'qos_image': qos,
        'qos_imu': qos,
        'qos_scan': qos,               # (optional) use same QoS for scan

        # 2D planar constraints
        'Reg/Force3DoF': 'true',
        'Optimizer/GravitySigma': '0'
    }

    remappings = [
        ('rgb/image', '/camera/image_raw'),
        ('rgb/camera_info', '/camera/camera_info'),
        ('depth/image', '/camera/depth/image_raw'),
        ('scan', '/scan')
    ]

    return LaunchDescription([

        DeclareLaunchArgument(
            'use_sim_time', default_value='true',
            description='Use simulation (Gazebo) clock if true'),

        DeclareLaunchArgument(
            'qos', default_value='2',
            description='QoS used for input sensor topics'),

        DeclareLaunchArgument(
            'localization', default_value='false',
            description='Launch in localization mode.'),

        # SLAM mode
        Node(
            condition=UnlessCondition(localization),
            package='rtabmap_slam',
            executable='rtabmap',
            output='screen',
            parameters=[parameters],
            remappings=remappings,
            arguments=['-d'],  # delete previous db
        ),

        # Localization mode
        Node(
            condition=IfCondition(localization),
            package='rtabmap_slam',
            executable='rtabmap',
            output='screen',
            parameters=[parameters, {
                'Mem/IncrementalMemory': 'False',
                'Mem/InitWMWithAllNodes': 'True',
            }],
            remappings=remappings,
        ),

        Node(
            package='rtabmap_viz',
            executable='rtabmap_viz',
            output='screen',
            parameters=[parameters],
            remappings=remappings,
        ),
    ])
