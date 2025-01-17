"""
Ongoing exploration:

1. Is it possible to use the default VPC? That would save a lot of money.
2. Can we point the UI at a database in lightsail?
3. By default, is the sagemaker notebook protected? Should we add an option to set up a VPN for it?
"""

from aws_cdk import Stack
from cdk_metaflow.config import MetaflowStackConfig
from constructs import Construct

from aws_cdk import aws_ec2 as ec2


class MetaflowStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, config: MetaflowStackConfig, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        vpc = ec2.Vpc(
            self,
            "vpc",
            enable_dns_support=True,
            enable_dns_hostnames=True,
            cidr=config.vpc_cidr,
            subnet_configuration=ec2.SubnetConfiguration(),
        )

        subnet1 = ec2.Subnet(
            self,
            "subnet-1",
            availability_zone=self.availability_zones[0],
            vpc_id=vpc.vpc_id,
            cidr_block=config.subnet_1_cidr,
            map_public_ip_on_launch=True,
        )

        subnet2 = ec2.Subnet(
            self,
            "subnet-2",
            availability_zone=self.availability_zones[1],
            vpc_id=vpc.vpc_id,
            cidr_block=config.subnet_2_cidr,
            map_public_ip_on_launch=True,
        )


# Resources:

#   InternetGateway:
#     Type: AWS::EC2::InternetGateway
#   GatewayAttachement:
#     Type: AWS::EC2::VPCGatewayAttachment
#     Properties:
#       VpcId: !Ref 'VPC'
#       InternetGatewayId: !Ref 'InternetGateway'
#   PublicRouteTable:
#     Type: AWS::EC2::RouteTable
#     Properties:
#       VpcId: !Ref 'VPC'
#   DefaultGateway:
#     Type: AWS::EC2::Route
#     DependsOn: GatewayAttachement
#     Properties:
#       RouteTableId: !Ref 'PublicRouteTable'
#       DestinationCidrBlock: '0.0.0.0/0'
#       GatewayId: !Ref 'InternetGateway'
#   Subnet1RTA:
#     Type: AWS::EC2::SubnetRouteTableAssociation
#     Properties:
#       SubnetId: !Ref Subnet1
#       RouteTableId: !Ref PublicRouteTable
#   Subnet2RTA:
#     Type: AWS::EC2::SubnetRouteTableAssociation
#     Properties:
#       SubnetId: !Ref Subnet2
#       RouteTableId: !Ref PublicRouteTable
#   ECSCluster:
#     Type: AWS::ECS::Cluster
#     Properties:
#       ClusterSettings:
#         - Name: containerInsights
#           Value: enabled
#   FargateSecurityGroup:
#     Type: AWS::EC2::SecurityGroup
#     Properties:
#       GroupDescription: Security Group for Fargate
#       VpcId: !Ref 'VPC'
#   NLBIngressRule:
#    Type: 'AWS::EC2::SecurityGroupIngress'
#    Properties:
#       Description: 'Allow API Calls Internally'
#       GroupId: !Ref FargateSecurityGroup
#       IpProtocol: tcp
#       FromPort: 8080
#       ToPort: 8080
#       CidrIp: !GetAtt 'VPC.CidrBlock'
#   NLBIngressRuleDBMigrate:
#     Type: 'AWS::EC2::SecurityGroupIngress'
#     Properties:
#         Description: 'Allow API Calls Internally'
#         GroupId: !Ref FargateSecurityGroup
#         IpProtocol: tcp
#         FromPort: 8082
#         ToPort: 8082
#         CidrIp: !GetAtt 'VPC.CidrBlock'
#   FargateInternalRule:
#     Type: AWS::EC2::SecurityGroupIngress
#     Properties:
#       Description: Internal Communication
#       GroupId: !Ref 'FargateSecurityGroup'
#       IpProtocol: -1
#       SourceSecurityGroupId: !Ref 'FargateSecurityGroup'
#   FargateAlbRule:
#     Type: AWS::EC2::SecurityGroupIngress
#     Condition: EnableUI
#     Properties:
#       Description: Internal Communication
#       GroupId: !Ref 'FargateSecurityGroup'
#       IpProtocol: -1
#       SourceSecurityGroupId: !Ref 'LoadBalancerSecurityGroupUI'
#   NLB:
#     Type: AWS::ElasticLoadBalancingV2::LoadBalancer
#     Properties:
#       Scheme: internal
#       Type: network
#       Subnets:
#         - !Ref Subnet1
#         - !Ref Subnet2
#   NLBListener:
#     Type: AWS::ElasticLoadBalancingV2::Listener
#     DependsOn:
#       - NLB
#     Properties:
#       DefaultActions:
#         - TargetGroupArn: !Ref 'NLBTargetGroup'
#           Type: 'forward'
#       LoadBalancerArn: !Ref 'NLB'
#       Port: 80
#       Protocol: TCP
#   NLBListenerDBMigrate:
#     Type: AWS::ElasticLoadBalancingV2::Listener
#     DependsOn:
#       - NLB
#     Properties:
#       DefaultActions:
#         - TargetGroupArn: !Ref 'NLBTargetGroupDBMigrate'
#           Type: 'forward'
#       LoadBalancerArn: !Ref 'NLB'
#       Port: 8082
#       Protocol: TCP
#   ECSRole:
#     Type: AWS::IAM::Role
#     Properties:
#       AssumeRolePolicyDocument:
#         Statement:
#         - Effect: Allow
#           Principal:
#             Service: [ecs.amazonaws.com]
#           Action: ['sts:AssumeRole']
#       Path: /
#       Policies:
#       - PolicyName: ecs-service
#         PolicyDocument:
#           Statement:
#           - Effect: Allow
#             Action:
#               - 'ec2:AttachNetworkInterface'
#               - 'ec2:CreateNetworkInterface'
#               - 'ec2:CreateNetworkInterfacePermission'
#               - 'ec2:DeleteNetworkInterface'
#               - 'ec2:DeleteNetworkInterfacePermission'
#               - 'ec2:Describe*'
#               - 'ec2:DetachNetworkInterface'
#               - 'elasticloadbalancing:DeregisterInstancesFromLoadBalancer'
#               - 'elasticloadbalancing:DeregisterTargets'
#               - 'elasticloadbalancing:Describe*'
#               - 'elasticloadbalancing:RegisterInstancesWithLoadBalancer'
#               - 'elasticloadbalancing:RegisterTargets'
#             Resource: '*'
#   ECSTaskExecutionRole:
#     Type: AWS::IAM::Role
#     Properties:
#       AssumeRolePolicyDocument:
#         Statement:
#         - Effect: Allow
#           Principal:
#             Service: [ecs-tasks.amazonaws.com]
#           Action: ['sts:AssumeRole']
#       Path: /
#       Policies:
#         - PolicyName: AmazonECSTaskExecutionRolePolicy
#           PolicyDocument:
#             Statement:
#             - Effect: Allow
#               Action:
#                 - 'ecr:GetAuthorizationToken'
#                 - 'ecr:BatchCheckLayerAvailability'
#                 - 'ecr:GetDownloadUrlForLayer'
#                 - 'ecr:BatchGetImage'
#                 - 'logs:CreateLogStream'
#                 - 'logs:PutLogEvents'
#               Resource: '*'
#   MetadataSvcECSTaskRole:
#     Type: AWS::IAM::Role
#     Properties:
#       AssumeRolePolicyDocument:
#         Version: '2012-10-17'
#         Statement:
#           Effect: Allow
#           Principal:
#             Service:
#               - ecs-tasks.amazonaws.com
#           Action:
#             - sts:AssumeRole
#       Path: /
#       Policies:
#         - PolicyName: CustomS3Batch
#           PolicyDocument:
#             Version: '2012-10-17'
#             Statement:
#               - Sid: ObjectAccessMetadataService
#                 Effect: Allow
#                 Action:
#                   - s3:GetObject
#                 Resource: !Join ['', [ !GetAtt 'MetaflowS3Bucket.Arn', '/*' ]]
#               - Sid: ObjectAccessMetadataServiceNonExistentKeys
#                 Effect: Allow
#                 Action:
#                   - s3:ListBucket
#                 Resource: !GetAtt 'MetaflowS3Bucket.Arn'
#         - PolicyName: DenyPresignedBatch
#           PolicyDocument:
#             Version: '2012-10-17'
#             Statement:
#               Sid: DenyPresignedBatch
#               Effect: Deny
#               Action: s3:*
#               Resource: '*'
#               Condition:
#                 StringNotEquals:
#                   s3:authType: REST-HEADER
#   ECSInstanceProfile:
#     Type: AWS::IAM::InstanceProfile
#     Properties:
#       Path: /
#       Roles:
#         - !Ref ECSInstanceRole
#   ECSInstanceRole:
#     Type: AWS::IAM::Role
#     Properties:
#       AssumeRolePolicyDocument:
#         Statement:
#         - Effect: Allow
#           Principal:
#             Service:
#               - 'ec2.amazonaws.com'
#           Action:
#             - 'sts:AssumeRole'
#       Path: /
#       ManagedPolicyArns:
#         - !Sub arn:${IAMPartition}:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role
#   TaskDefinition:
#     Type: AWS::ECS::TaskDefinition
#     Properties:
#       Family: !FindInMap ['ServiceInfo', 'ServiceName', 'value']
#       Cpu: !FindInMap ['ServiceInfo', 'ContainerCpu', 'value']
#       Memory: !FindInMap ['ServiceInfo', 'ContainerMemory', 'value']
#       NetworkMode: awsvpc
#       RequiresCompatibilities:
#         - FARGATE
#       ExecutionRoleArn: !Ref 'ECSTaskExecutionRole'
#       TaskRoleArn: !GetAtt 'MetadataSvcECSTaskRole.Arn'
#       ContainerDefinitions:
#         - Name: !FindInMap ['ServiceInfo', 'ServiceName', 'value']
#           Environment:
#             - Name: "MF_METADATA_DB_HOST"
#               Value: !GetAtt 'RDSMasterInstance.Endpoint.Address'
#             - Name: "MF_METADATA_DB_PORT"
#               Value: "5432"
#             - Name: "MF_METADATA_DB_USER"
#               Value: "master"
#             - Name: "MF_METADATA_DB_PSWD"
#               Value: !Join ['', ['{{resolve:secretsmanager:', !Ref MyRDSSecret, ':SecretString:password}}' ]]
#             - Name: "MF_METADATA_DB_NAME"
#               Value: "metaflow"
#           Cpu: !FindInMap ['ServiceInfo', 'ContainerCpu', 'value']
#           Memory: !FindInMap ['ServiceInfo', 'ContainerMemory', 'value']
#           Image: !FindInMap ['ServiceInfo', 'ImageUrl', 'value']
#           PortMappings:
#             - ContainerPort: !FindInMap ['ServiceInfo', 'ContainerPort', 'value']
#             - ContainerPort: 8082
#           LogConfiguration:
#             LogDriver: awslogs
#             Options:
#               awslogs-group: !Join ['', ['/ecs/', !Ref 'AWS::StackName', '-', !FindInMap ['ServiceInfo', 'ServiceName', 'value']]]
#               awslogs-region: !Ref 'AWS::Region'
#               awslogs-stream-prefix: 'ecs'
#   MetadataServiceLogGroup:
#     Type: AWS::Logs::LogGroup
#     Properties:
#       LogGroupName: !Join ['', ['/ecs/', !Ref 'AWS::StackName', '-', !FindInMap ['ServiceInfo', 'ServiceName', 'value']]]
#   ECSFargateService:
#     Type: AWS::ECS::Service
#     Properties:
#       ServiceName: !FindInMap ['ServiceInfo', 'ServiceName', 'value']
#       Cluster: !Ref 'ECSCluster'
#       LaunchType: FARGATE
#       DeploymentConfiguration:
#         MaximumPercent: 200
#         MinimumHealthyPercent: 75
#       DesiredCount: !FindInMap ['ServiceInfo', 'DesiredCount', 'value']
#       NetworkConfiguration:
#         AwsvpcConfiguration:
#           AssignPublicIp: ENABLED
#           SecurityGroups:
#             - !Ref 'FargateSecurityGroup'
#           Subnets:
#             - !Ref 'Subnet1'
#             - !Ref 'Subnet2'
#       TaskDefinition: !Ref 'TaskDefinition'
#       LoadBalancers:
#         - ContainerName: !FindInMap ['ServiceInfo', 'ServiceName', 'value']
#           ContainerPort: !FindInMap ['ServiceInfo', 'ContainerPort', 'value']
#           TargetGroupArn: !Ref 'NLBTargetGroup'
#         - ContainerName: !FindInMap ['ServiceInfo', 'ServiceName', 'value']
#           ContainerPort: 8082
#           TargetGroupArn: !Ref 'NLBTargetGroupDBMigrate'
#   LambdaECSExecuteRole:
#     Type: AWS::IAM::Role
#     Properties:
#       AssumeRolePolicyDocument:
#         Version: '2012-10-17'
#         Statement:
#           Effect: Allow
#           Principal:
#             Service:
#               - lambda.amazonaws.com
#           Action:
#             - sts:AssumeRole
#       Path: /
#       Policies:
#         - PolicyName: Cloudwatch
#           PolicyDocument:
#             Version: '2012-10-17'
#             Statement:
#             - Sid: CreateLogGroup
#               Effect: Allow
#               Action: logs:CreateLogGroup
#               Resource: !Join [ "", [ !Sub 'arn:${IAMPartition}:logs:', !Ref 'AWS::Region', ':', !Ref 'AWS::AccountId', ':*' ] ]
#             - Sid: LogEvents
#               Effect: Allow
#               Action:
#                 - logs:PutLogEvents
#                 - logs:CreateLogStream
#               Resource: !Join [ "", [ !Sub 'arn:${IAMPartition}:logs:', !Ref 'AWS::Region', ':', !Ref 'AWS::AccountId', ':log-group:/aws/lambda/', !Ref 'AWS::StackName', '-migrate-db:*'] ]
#         - PolicyName: VPC
#           PolicyDocument:
#             Version: '2012-10-17'
#             Statement:
#             - Sid: NetInts
#               Effect: Allow
#               Action:
#                 - ec2:CreateNetworkInterface
#                 - ec2:DescribeNetworkInterfaces
#                 - ec2:DeleteNetworkInterface
#               Resource: '*'
#   ExecuteDBMigration:
#     Type: AWS::Lambda::Function
#     Properties:
#       Runtime: python3.7
#       Role: !GetAtt LambdaECSExecuteRole.Arn
#       Handler: index.handler
#       Environment:
#         Variables:
#           MD_LB_ADDRESS: !Join ['', ['http://', !GetAtt 'NLB.DNSName', ':8082'] ]
#       Code:
#         ZipFile: |
#           import os, json
#           from urllib import request
#           def handler(event, context):
#             response = {}
#             status_endpoint = "{}/db_schema_status".format(os.environ.get('MD_LB_ADDRESS'))
#             upgrade_endpoint = "{}/upgrade".format(os.environ.get('MD_LB_ADDRESS'))
#             with request.urlopen(status_endpoint) as status:
#               response['init-status'] = json.loads(status.read())
#             upgrade_patch = request.Request(upgrade_endpoint, method='PATCH')
#             with request.urlopen(upgrade_patch) as upgrade:
#               response['upgrade-result'] = upgrade.read().decode()
#             with request.urlopen(status_endpoint) as status:
#               response['final-status'] = json.loads(status.read())
#             print(response)
#             return(response)
#       Description: Trigger DB Migration
#       FunctionName: !Join ['-', [!Ref 'AWS::StackName', 'migrate-db'] ]
#       Timeout: 900
#       VpcConfig:
#         SecurityGroupIds:
#           - !GetAtt VPC.DefaultSecurityGroup
#         SubnetIds:
#           - !Ref Subnet1
#           - !Ref Subnet2
#   NLBTargetGroup:
#     Type: AWS::ElasticLoadBalancingV2::TargetGroup
#     Properties:
#       HealthCheckIntervalSeconds: 10
#       HealthCheckProtocol: TCP
#       HealthCheckTimeoutSeconds: 10
#       HealthyThresholdCount: 2
#       TargetType: ip
#       Port: !FindInMap ['ServiceInfo', 'ContainerPort', 'value']
#       Protocol: TCP
#       UnhealthyThresholdCount: 2
#       VpcId: !Ref 'VPC'
#   NLBTargetGroupDBMigrate:
#     Type: AWS::ElasticLoadBalancingV2::TargetGroup
#     Properties:
#       HealthCheckIntervalSeconds: 10
#       HealthCheckProtocol: TCP
#       HealthCheckTimeoutSeconds: 10
#       HealthCheckPort: 8080
#       HealthyThresholdCount: 2
#       TargetType: ip
#       Port: 8082
#       Protocol: TCP
#       UnhealthyThresholdCount: 2
#       VpcId: !Ref 'VPC'
#   DBSubnetGroup:
#     Type: AWS::RDS::DBSubnetGroup
#     Properties:
#       DBSubnetGroupDescription: DBSubnetGroup for RDS instances
#       SubnetIds:
#         - Ref: Subnet1
#         - Ref: Subnet2
#   RDSSecurityGroup:
#     Type: AWS::EC2::SecurityGroup
#     Properties:
#       GroupDescription: Security Group for RDS
#       VpcId: !Ref 'VPC'
#   PostgresIngressRule:
#     Type: AWS::EC2::SecurityGroupIngress
#     Properties:
#       GroupId: !Ref 'RDSSecurityGroup'
#       SourceSecurityGroupId: !Ref 'FargateSecurityGroup'
#       IpProtocol: tcp
#       FromPort: 5432
#       ToPort: 5432
#   RDSMasterInstance:
#     Type: AWS::RDS::DBInstance
#     Properties:
#       DBName: 'metaflow'
#       AllocatedStorage: 20
#       DBInstanceClass: 'db.t2.small'
#       DeleteAutomatedBackups: 'true'
#       StorageType: 'gp2'
#       Engine: 'postgres'
#       EngineVersion: '11'
#       MasterUsername: !Join ['', ['{{resolve:secretsmanager:', !Ref MyRDSSecret, ':SecretString:username}}' ]]
#       MasterUserPassword: !Join ['', ['{{resolve:secretsmanager:', !Ref MyRDSSecret, ':SecretString:password}}' ]]
#       VPCSecurityGroups:
#         - !Ref 'RDSSecurityGroup'
#       DBSubnetGroupName: !Ref 'DBSubnetGroup'
#   MyRDSSecret:
#     Type: "AWS::SecretsManager::Secret"
#     Properties:
#       Description: "This is a Secrets Manager secret for an RDS DB instance"
#       GenerateSecretString:
#         SecretStringTemplate: '{"username": "master"}'
#         GenerateStringKey: "password"
#         PasswordLength: 16
#         ExcludeCharacters: '"@/\'
#   SecretRDSInstanceAttachment:
#     Type: "AWS::SecretsManager::SecretTargetAttachment"
#     Properties:
#       SecretId: !Ref MyRDSSecret
#       TargetId: !Ref RDSMasterInstance
#       TargetType: AWS::RDS::DBInstance
#   MetaflowS3Bucket:
#     Type: 'AWS::S3::Bucket'
#     DeletionPolicy: Retain
#     Properties:
#       AccessControl: Private
#       BucketEncryption:
#         ServerSideEncryptionConfiguration:
#           - ServerSideEncryptionByDefault:
#               SSEAlgorithm: AES256
#       PublicAccessBlockConfiguration:
#         BlockPublicAcls: true
#         BlockPublicPolicy: true
#         IgnorePublicAcls: true
#         RestrictPublicBuckets: true
#   SagemakerSecurityGroup:
#     Condition: 'EnableSagemaker'
#     Type: "AWS::EC2::SecurityGroup"
#     Properties:
#       GroupDescription: 'Security Group for Sagemaker'
#       VpcId: !Ref VPC
#       SecurityGroupIngress:
#         - CidrIp: "0.0.0.0/0"
#           IpProtocol: "TCP"
#           FromPort: 8080
#           ToPort: 8080
#   SageMakerExecutionRole:
#     Condition: 'EnableSagemaker'
#     Type: AWS::IAM::Role
#     Properties:
#       AssumeRolePolicyDocument:
#         Version: '2012-10-17'
#         Statement:
#           Effect: Allow
#           Principal:
#             Service:
#               - sagemaker.amazonaws.com
#           Action:
#             - sts:AssumeRole
#       Path: /
#       Policies:
#         - PolicyName: IAM_PASS_ROLE
#           PolicyDocument:
#             Version: '2012-10-17'
#             Statement:
#               Sid: AllowPassRole
#               Effect: Allow
#               Action: iam:PassRole
#               Resource: '*'
#               Condition:
#                 StringEquals:
#                   iam:PassedToService: sagemaker.amazonaws.com
#         - PolicyName: MISC_PERMISSIONS
#           PolicyDocument:
#             Version: '2012-10-17'
#             Statement:
#               Sid: MiscPermissions
#               Effect: Allow
#               Action:
#                 - cloudwatch:PutMetricData
#                 - ecr:GetDownloadUrlForLayer
#                 - ecr:BatchGetImage
#                 - ecr:GetAuthorizationToken
#                 - ecr:BatchCheckLayerAvailability
#               Resource: '*'
#         - PolicyName: log_roles_policy
#           PolicyDocument:
#             Version: '2012-10-17'
#             Statement:
#             - Sid: CreateLogStream
#               Effect: Allow
#               Action:
#                 - logs:CreateLogStream
#               Resource:
#                 - !Join [ "", [ !Sub 'arn:${IAMPartition}:logs:', !Ref 'AWS::Region', ':', !Ref 'AWS::AccountId', ':log-group:/aws/batch/job:log-stream:*' ] ]
#                 - !Join [ "", [ !Sub 'arn:${IAMPartition}:logs:', !Ref 'AWS::Region', ':', !Ref 'AWS::AccountId', ':log-group:/aws/sagemaker/NotebookInstances:log-stream:*' ] ]
#             - Sid: LogEvents
#               Effect: Allow
#               Action:
#                 - logs:PutLogEvents
#                 - logs:GetLogEvents
#               Resource:
#                 - !Join [ "", [ !Sub 'arn:${IAMPartition}:logs:', !Ref 'AWS::Region', ':', !Ref 'AWS::AccountId', ':log-group:/aws/sagemaker/NotebookInstances:log-stream:', !Ref 'AWS::StackName', '-NotebookInstance-', '{{resolve:secretsmanager:', !Ref RandomString, ':SecretString:password}}', '/jupyter.log' ] ]
#                 - !Join [ "", [ !Sub 'arn:${IAMPartition}:logs:', !Ref 'AWS::Region', ':', !Ref 'AWS::AccountId', ':log-group:/aws/sagemaker/NotebookInstances:log-stream:', !Ref 'AWS::StackName', '-NotebookInstance-', '{{resolve:secretsmanager:', !Ref RandomString, ':SecretString:password}}', '/LifecycleConfigOnCreate' ] ]
#                 - !Join [ "", [ !Sub 'arn:${IAMPartition}:logs:', !Ref 'AWS::Region', ':', !Ref 'AWS::AccountId', ':log-group:/aws/batch/job:log-stream:job-queue-' ] ]
#             - Sid: LogGroup
#               Effect: Allow
#               Action:
#                 - logs:DescribeLogGroups
#                 - logs:DescribeLogStreams
#                 - logs:CreateLogGroup
#               Resource: '*'
#         - PolicyName: SageMakerPermissions
#           PolicyDocument:
#             Version: '2012-10-17'
#             Statement:
#               Sid: SageMakerNotebook
#               Effect: "Allow"
#               Action:
#                 - "sagemaker:DescribeNotebook*"
#                 - "sagemaker:StartNotebookInstance"
#                 - "sagemaker:StopNotebookInstance"
#                 - "sagemaker:UpdateNotebookInstance"
#                 - "sagemaker:CreatePresignedNotebookInstanceUrl"
#               Resource:
#                 - !Sub "arn:${IAMPartition}:sagemaker:${AWS::Region}:${AWS::AccountId}:notebook-instance/${AWS::StackName}*"
#                 - !Sub "arn:${IAMPartition}:sagemaker:${AWS::Region}:${AWS::AccountId}:notebook-instance-lifecycle-config/basic*"
#         - PolicyName: CustomS3ListAccess
#           PolicyDocument:
#             Version: '2012-10-17'
#             Statement:
#               Sid: BucketAccess
#               Effect: Allow
#               Action: s3:ListBucket
#               Resource: !GetAtt 'MetaflowS3Bucket.Arn'
#         - PolicyName: CustomS3Access
#           PolicyDocument:
#             Version: '2012-10-17'
#             Statement:
#               Sid: ObjectAccess
#               Effect: Allow
#               Action:
#                 - s3:PutObject
#                 - s3:GetObject
#                 - s3:DeleteObject
#               Resource: !Join ['', [ !GetAtt 'MetaflowS3Bucket.Arn', '/*' ]]
#         - PolicyName: DenyPresigned
#           PolicyDocument:
#             Version: '2012-10-17'
#             Statement:
#               Sid: DenyPresigned
#               Effect: Deny
#               Action: s3:*
#               Resource: '*'
#               Condition:
#                 StringNotEquals:
#                   s3:authType: REST-HEADER
#   MetaflowUserRole:
#     Condition: 'EnableRole'
#     Type: AWS::IAM::Role
#     Properties:
#       AssumeRolePolicyDocument:
#         Version: '2012-10-17'
#         Statement:
#           Effect: Allow
#           Principal:
#             AWS:
#               - !GetAtt 'MetadataSvcECSTaskRole.Arn'
#           Action:
#             - sts:AssumeRole
#       Path: /
#       Policies:
#         - PolicyName: "Metaflow-Policy"
#           PolicyDocument:
#             Version: "2012-10-17"
#             Statement:
#               - Effect: "Allow"
#                 Action:
#                   - "cloudformation:DescribeStacks"
#                   - "cloudformation:*Stack"
#                   - "cloudformation:*ChangeSet"
#                 Resource:
#                   - !Sub "arn:${IAMPartition}:cloudformation:${AWS::Region}:${AWS::AccountId}:stack/${AWS::StackName}-*"
#               - Effect: "Allow"
#                 Action:
#                   - "s3:*Object"
#                 Resource:
#                   - !GetAtt 'MetaflowS3Bucket.Arn'
#                   - !Join ['', [ !GetAtt 'MetaflowS3Bucket.Arn', '/*' ]]
#               - Effect: "Allow"
#                 Action:
#                   - "sagemaker:DescribeNotebook*"
#                   - "sagemaker:StartNotebookInstance"
#                   - "sagemaker:StopNotebookInstance"
#                   - "sagemaker:UpdateNotebookInstance"
#                   - "sagemaker:CreatePresignedNotebookInstanceUrl"
#                 Resource:
#                   - !Sub "arn:${IAMPartition}:sagemaker:${AWS::Region}:${AWS::AccountId}:notebook-instance/${AWS::StackName}-*"
#                   - !Sub "arn:${IAMPartition}:sagemaker:${AWS::Region}:${AWS::AccountId}:notebook-instance-lifecycle-config/basic*"
#               - Effect: "Allow"
#                 Action:
#                   - "iam:PassRole"
#                 Resource:
#                   - !Sub "arn:${IAMPartition}:iam::${AWS::AccountId}:role/${AWS::StackName}-*"
#               - Effect: "Allow"
#                 Action:
#                   - "kms:Decrypt"
#                   - "kms:Encrypt"
#                 Resource:
#                   - !Sub "arn:${IAMPartition}:kms:${AWS::Region}:${AWS::AccountId}:key/"
#         - PolicyName: BatchPerms
#           PolicyDocument:
#             Version: '2012-10-17'
#             Statement:
#             - Sid: JobsPermissions
#               Effect: Allow
#               Action:
#                 - "batch:TerminateJob"
#                 - "batch:DescribeJobs"
#                 - "batch:DescribeJobDefinitions"
#                 - "batch:DescribeJobQueues"
#                 - "batch:RegisterJobDefinition"
#                 - "batch:DescribeComputeEnvironments"
#               Resource: '*'
#             - Sid: DefinitionsPermissions
#               Effect: Allow
#               Action:
#                 - "batch:SubmitJob"
#               Resource:
#                 - !Ref "JobQueue"
#                 - !Sub arn:${IAMPartition}:batch:${AWS::Region}:${AWS::AccountId}:job-definition/*:*
#         - PolicyName: CustomS3ListAccess
#           PolicyDocument:
#             Version: '2012-10-17'
#             Statement:
#               Sid: BucketAccess
#               Effect: Allow
#               Action: s3:ListBucket
#               Resource: !GetAtt 'MetaflowS3Bucket.Arn'
#         - PolicyName: LogPerms
#           PolicyDocument:
#             Version: '2012-10-17'
#             Statement:
#               Sid: GetLogs
#               Effect: Allow
#               Action: logs:GetLogEvents
#               Resource: !Sub arn:${IAMPartition}:logs:${AWS::Region}:${AWS::AccountId}:log-group:*:log-stream:*
#         - PolicyName: AllowSagemaker
#           PolicyDocument:
#             Version: '2012-10-17'
#             Statement:
#             - Sid: AllowSagemakerCreate
#               Effect: Allow
#               Action: sagemaker:CreateTrainingJob
#               Resource: !Sub arn:${IAMPartition}:sagemaker:${AWS::Region}:${AWS::AccountId}:training-job/*
#             - Sid: AllowSagemakerDescribe
#               Effect: Allow
#               Action: sagemaker:DescribeTrainingJob
#               Resource: !Sub arn:${IAMPartition}:sagemaker:${AWS::Region}:${AWS::AccountId}:training-job/*
#         - PolicyName: AllowStepFunctions
#           PolicyDocument:
#             Version: '2012-10-17'
#             Statement:
#             - Sid: TasksAndExecutionsGlobal
#               Effect: Allow
#               Action:
#                 - "states:ListStateMachines"
#               Resource: '*'
#             - Sid: StateMachines
#               Effect: Allow
#               Action:
#                 - "states:DescribeStateMachine"
#                 - "states:UpdateStateMachine"
#                 - "states:StartExecution"
#                 - "states:CreateStateMachine"
#                 - "states:ListExecutions"
#                 - "states:StopExecution"
#               Resource: !Sub 'arn:${IAMPartition}:states:${AWS::Region}:${AWS::AccountId}:stateMachine:*'
#         - PolicyName: AllowEventBridge
#           PolicyDocument:
#             Version: '2012-10-17'
#             Statement:
#               - Sid: RuleMaintenance
#                 Effect: Allow
#                 Action:
#                   - "events:PutTargets"
#                   - "events:DisableRule"
#                 Resource: !Sub "arn:${IAMPartition}:events:${AWS::Region}:${AWS::AccountId}:rule/*"
#               - Sid: PutRule
#                 Effect: Allow
#                 Action:
#                   - "events:PutRule"
#                 Resource: !Sub "arn:${IAMPartition}:events:${AWS::Region}:${AWS::AccountId}:rule/*"
#                 Condition:
#                   "Null":
#                     events:source: true
#   MetaflowUserPolicy:
#     Condition: 'EnableRole'
#     Type: AWS::IAM::ManagedPolicy
#     Properties:
#       PolicyDocument:
#         Version: "2012-10-17"
#         Statement:
#           - Effect: "Allow"
#             Action:
#               - "cloudformation:DescribeStacks"
#               - "cloudformation:*Stack"
#               - "cloudformation:*ChangeSet"
#             Resource:
#               - !Sub "arn:${IAMPartition}:cloudformation:${AWS::Region}:${AWS::AccountId}:stack/${AWS::StackName}-*"
#           - Effect: "Allow"
#             Action:
#               - "s3:*Object"
#             Resource:
#               - !GetAtt 'MetaflowS3Bucket.Arn'
#               - !Join ['', [ !GetAtt 'MetaflowS3Bucket.Arn', '/*' ]]
#           - Effect: "Allow"
#             Action:
#               - "sagemaker:DescribeNotebook*"
#               - "sagemaker:StartNotebookInstance"
#               - "sagemaker:StopNotebookInstance"
#               - "sagemaker:UpdateNotebookInstance"
#               - "sagemaker:CreatePresignedNotebookInstanceUrl"
#             Resource:
#               - !Sub "arn:${IAMPartition}:sagemaker:${AWS::Region}:${AWS::AccountId}:notebook-instance/${AWS::StackName}-*"
#               - !Sub "arn:${IAMPartition}:sagemaker:${AWS::Region}:${AWS::AccountId}:notebook-instance-lifecycle-config/basic*"
#           - Effect: "Allow"
#             Action:
#               - "iam:PassRole"
#             Resource:
#               - !Sub "arn:${IAMPartition}:iam::${AWS::AccountId}:role/${AWS::StackName}-*"
#           - Effect: "Allow"
#             Action:
#               - "kms:Decrypt"
#               - "kms:Encrypt"
#             Resource:
#               - !Sub "arn:${IAMPartition}:kms:${AWS::Region}:${AWS::AccountId}:key/"
#           - Sid: JobsPermissions
#             Effect: Allow
#             Action:
#               - "batch:TerminateJob"
#               - "batch:DescribeJobs"
#               - "batch:DescribeJobDefinitions"
#               - "batch:DescribeJobQueues"
#               - "batch:RegisterJobDefinition"
#               - "batch:DescribeComputeEnvironments"
#             Resource: '*'
#           - Sid: DefinitionsPermissions
#             Effect: Allow
#             Action:
#               - "batch:SubmitJob"
#             Resource:
#               - !Ref "JobQueue"
#               - !Sub arn:${IAMPartition}:batch:${AWS::Region}:${AWS::AccountId}:job-definition/*:*
#           - Sid: BucketAccess
#             Effect: Allow
#             Action: s3:ListBucket
#             Resource: !GetAtt 'MetaflowS3Bucket.Arn'
#           - Sid: GetLogs
#             Effect: Allow
#             Action: logs:GetLogEvents
#             Resource: !Sub arn:${IAMPartition}:logs:${AWS::Region}:${AWS::AccountId}:log-group:*:log-stream:*
#           - Sid: AllowSagemakerCreate
#             Effect: Allow
#             Action: sagemaker:CreateTrainingJob
#             Resource: !Sub arn:${IAMPartition}:sagemaker:${AWS::Region}:${AWS::AccountId}:training-job/*
#           - Sid: AllowSagemakerDescribe
#             Effect: Allow
#             Action: sagemaker:DescribeTrainingJob
#             Resource: !Sub arn:${IAMPartition}:sagemaker:${AWS::Region}:${AWS::AccountId}:training-job/*
#           - Sid: TasksAndExecutionsGlobal
#             Effect: Allow
#             Action:
#               - "states:ListStateMachines"
#             Resource: '*'
#           - Sid: StateMachines
#             Effect: Allow
#             Action:
#               - "states:DescribeStateMachine"
#               - "states:UpdateStateMachine"
#               - "states:StartExecution"
#               - "states:CreateStateMachine"
#               - "states:ListExecutions"
#               - "states:StopExecution"
#             Resource: !Sub 'arn:${IAMPartition}:states:${AWS::Region}:${AWS::AccountId}:stateMachine:*'
#           - Sid: RuleMaintenance
#             Effect: Allow
#             Action:
#               - "events:PutTargets"
#               - "events:DisableRule"
#             Resource: !Sub "arn:${IAMPartition}:events:${AWS::Region}:${AWS::AccountId}:rule/*"
#           - Sid: PutRule
#             Effect: Allow
#             Action:
#               - "events:PutRule"
#             Resource: !Sub "arn:${IAMPartition}:events:${AWS::Region}:${AWS::AccountId}:rule/*"
#             Condition:
#               "Null":
#                 events:source: true
#   EventBridgeRole:
#     Type: AWS::IAM::Role
#     Properties:
#       AssumeRolePolicyDocument:
#         Version: '2012-10-17'
#         Statement:
#           Effect: Allow
#           Principal:
#             Service:
#               - events.amazonaws.com
#           Action:
#             - sts:AssumeRole
#       Path: /
#       Policies:
#         - PolicyName: AllowStepFunctions
#           PolicyDocument:
#             Version: '2012-10-17'
#             Statement:
#               - Sid: ExecuteStepFunction
#                 Effect: Allow
#                 Action:
#                   - 'states:StartExecution'
#                 Resource: !Sub 'arn:${IAMPartition}:states:${AWS::Region}:${AWS::AccountId}:stateMachine:*'
#   StepFunctionsRole:
#     Type: AWS::IAM::Role
#     Properties:
#       AssumeRolePolicyDocument:
#         Version: '2012-10-17'
#         Statement:
#           Effect: Allow
#           Principal:
#             Service:
#               - states.amazonaws.com
#           Action:
#             - sts:AssumeRole
#       Path: /
#       Policies:
#         - PolicyName: BatchPerms
#           PolicyDocument:
#             Version: '2012-10-17'
#             Statement:
#             - Sid: JobsPermissions
#               Effect: Allow
#               Action:
#                 - "batch:TerminateJob"
#                 - "batch:DescribeJobs"
#                 - "batch:DescribeJobDefinitions"
#                 - "batch:DescribeJobQueues"
#                 - "batch:RegisterJobDefinition"
#               Resource: '*'
#             - Sid: DefinitionsPermissions
#               Effect: Allow
#               Action:
#                 - "batch:SubmitJob"
#               Resource:
#                 - !Ref "JobQueue"
#                 - !Sub arn:${IAMPartition}:batch:${AWS::Region}:${AWS::AccountId}:job-definition/*:*
#         - PolicyName: CustomS3Access
#           PolicyDocument:
#             Version: '2012-10-17'
#             Statement:
#             - Sid: BucketAccess
#               Effect: Allow
#               Action: s3:ListBucket
#               Resource: !GetAtt 'MetaflowS3Bucket.Arn'
#             - Sid: ObjectAccess
#               Effect: "Allow"
#               Action:
#                 - "s3:*Object"
#               Resource:
#                 - !GetAtt 'MetaflowS3Bucket.Arn'
#                 - !Join ['', [ !GetAtt 'MetaflowS3Bucket.Arn', '/*' ]]
#         - PolicyName: AllowCloudwatch
#           PolicyDocument:
#             Version: '2012-10-17'
#             Statement:
#               - Sid: CloudwatchLogDelivery
#                 Effect: Allow
#                 Action:
#                   - "logs:CreateLogDelivery"
#                   - "logs:GetLogDelivery"
#                   - "logs:UpdateLogDelivery"
#                   - "logs:DeleteLogDelivery"
#                   - "logs:ListLogDeliveries"
#                   - "logs:PutResourcePolicy"
#                   - "logs:DescribeResourcePolicies"
#                   - "logs:DescribeLogGroups"
#                 Resource: '*'
#         - PolicyName: AllowEventBridge
#           PolicyDocument:
#             Version: '2012-10-17'
#             Statement:
#               - Sid: RuleMaintenance
#                 Effect: Allow
#                 Action:
#                   - "events:PutTargets"
#                   - "events:DescribeRule"
#                 Resource: !Sub "arn:${IAMPartition}:events:${AWS::Region}:${AWS::AccountId}:rule/StepFunctionsGetEventsForBatchJobsRule"
#               - Sid: PutRule
#                 Effect: Allow
#                 Action:
#                   - "events:PutRule"
#                 Resource: !Sub "arn:${IAMPartition}:events:${AWS::Region}:${AWS::AccountId}:rule/StepFunctionsGetEventsForBatchJobsRule"
#                 Condition:
#                   StringEquals:
#                     events:detail-type: "Batch Job State Change"
#         - PolicyName: DynamoDB
#           PolicyDocument:
#             Version: '2012-10-17'
#             Statement:
#             - Sid: Items
#               Effect: Allow
#               Action:
#                 - "dynamodb:PutItem"
#                 - "dynamodb:GetItem"
#                 - "dynamodb:UpdateItem"
#               Resource: !Sub arn:${IAMPartition}:dynamodb:${AWS::Region}:${AWS::AccountId}:table/${StepFunctionsStateDDB}
#   BasicNotebookInstanceLifecycleConfig:
#     Condition: 'EnableSagemaker'
#     Type: "AWS::SageMaker::NotebookInstanceLifecycleConfig"
#     Properties:
#       OnCreate:
#         - Content:
#             Fn::Base64:
#               !Sub |
#                 #!/bin/bash
#                 echo 'export METAFLOW_DATASTORE_SYSROOT_S3=s3://${MetaflowS3Bucket}/metaflow/' >> /etc/profile.d/jupyter-env.sh
#                 echo 'export METAFLOW_DATATOOLS_S3ROOT=s3://${MetaflowS3Bucket}/data/' >> /etc/profile.d/jupyter-env.sh
#                 echo 'export METAFLOW_SERVICE_URL=http://${NLB.DNSName}/' >> /etc/profile.d/jupyter-env.sh
#                 echo 'export AWS_DEFAULT_REGION=${AWS::Region}' >> /etc/profile.d/jupyter-env.sh
#                 echo 'export METAFLOW_DEFAULT_DATASTORE=s3' >> /etc/profile.d/jupyter-env.sh
#                 echo 'export METAFLOW_DEFAULT_METADATA=service' >> /etc/profile.d/jupyter-env.sh
#                 initctl restart jupyter-server --no-wait
#       OnStart:
#         - Content:
#             Fn::Base64:
#               !Sub |
#                 #!/bin/bash
#                 set -e
#                 sudo -u ec2-user -i <<'EOF'
#                 echo "THIS IS A PLACE HOLDER TO EXECUTE - USER LEVEL" >> ~/.customrc
#                 EOF
#   SageMakerNotebookInstance:
#     Condition: 'EnableSagemaker'
#     Type: AWS::SageMaker::NotebookInstance
#     Properties:
#       NotebookInstanceName: !Join ['', [!Ref 'AWS::StackName', '-NotebookInstance-', '{{resolve:secretsmanager:', !Ref RandomString, ':SecretString:password}}' ]]
#       InstanceType: !Ref SagemakerInstance
#       RoleArn: !GetAtt 'SageMakerExecutionRole.Arn'
#       LifecycleConfigName: !GetAtt 'BasicNotebookInstanceLifecycleConfig.NotebookInstanceLifecycleConfigName'
#       SubnetId: !Ref Subnet1
#       SecurityGroupIds:
#         - !Ref 'SagemakerSecurityGroup'
#   RandomString:
#     Type: AWS::SecretsManager::Secret
#     Properties:
#       Description: 'Random String'
#       GenerateSecretString:
#         SecretStringTemplate: '{"username": "admin"}'
#         GenerateStringKey: 'password'
#         ExcludePunctuation: 'true'
#         PasswordLength: 8
#         ExcludeCharacters: '"@/\'
#   BatchS3TaskRole:
#     Type: AWS::IAM::Role
#     Properties:
#       AssumeRolePolicyDocument:
#         Version: '2012-10-17'
#         Statement:
#           Effect: Allow
#           Principal:
#             Service:
#               - ecs-tasks.amazonaws.com
#           Action:
#             - sts:AssumeRole
#       Path: /
#       ManagedPolicyArns:
#         - !If
#           - EnableAddtionalWorkerPolicy
#           - !Ref 'AdditionalWorkerPolicyArn'
#           - !Ref AWS::NoValue
#       Policies:
#         - PolicyName: CustomS3ListBatch
#           PolicyDocument:
#             Version: '2012-10-17'
#             Statement:
#               Sid: BucketAccessBatch
#               Effect: Allow
#               Action: s3:ListBucket
#               Resource: !GetAtt 'MetaflowS3Bucket.Arn'
#         - PolicyName: CustomS3Batch
#           PolicyDocument:
#             Version: '2012-10-17'
#             Statement:
#               Sid: ObjectAccessBatch
#               Effect: Allow
#               Action:
#                 - s3:PutObject
#                 - s3:GetObject
#                 - s3:DeleteObject
#               Resource: !Join ['', [ !GetAtt 'MetaflowS3Bucket.Arn', '/*' ]]
#         - PolicyName: DenyPresignedBatch
#           PolicyDocument:
#             Version: '2012-10-17'
#             Statement:
#               Sid: DenyPresignedBatch
#               Effect: Deny
#               Action: s3:*
#               Resource: '*'
#               Condition:
#                 StringNotEquals:
#                   s3:authType: REST-HEADER
#         - PolicyName: AllowSagemaker
#           PolicyDocument:
#             Version: '2012-10-17'
#             Statement:
#             - Sid: AllowSagemakerCreate
#               Effect: Allow
#               Action: sagemaker:CreateTrainingJob
#               Resource: !Sub arn:${IAMPartition}:sagemaker:${AWS::Region}:${AWS::AccountId}:training-job/*
#             - Sid: AllowSagemakerDescribe
#               Effect: Allow
#               Action: sagemaker:DescribeTrainingJob
#               Resource: !Sub arn:${IAMPartition}:sagemaker:${AWS::Region}:${AWS::AccountId}:training-job/*
#             - Sid: AllowSagemakerDeploy
#               Effect: Allow
#               Action:
#                 - "sagemaker:CreateModel"
#                 - "sagemaker:CreateEndpointConfig"
#                 - "sagemaker:CreateEndpoint"
#                 - "sagemaker:DescribeModel"
#                 - "sagemaker:DescribeEndpoint"
#                 - "sagemaker:InvokeEndpoint"
#               Resource:
#                 - !Sub "arn:${IAMPartition}:sagemaker:${AWS::Region}:${AWS::AccountId}:endpoint/*"
#                 - !Sub "arn:${IAMPartition}:sagemaker:${AWS::Region}:${AWS::AccountId}:model/*"
#                 - !Sub "arn:${IAMPartition}:sagemaker:${AWS::Region}:${AWS::AccountId}:endpoint-config/*"
#         - PolicyName: IAM_PASS_ROLE
#           PolicyDocument:
#             Version: '2012-10-17'
#             Statement:
#               Sid: AllowPassRole
#               Effect: Allow
#               Action: iam:PassRole
#               Resource: '*'
#               Condition:
#                 StringEquals:
#                   iam:PassedToService: sagemaker.amazonaws.com
#         - PolicyName: DynamoDB
#           PolicyDocument:
#             Version: '2012-10-17'
#             Statement:
#             - Sid: Items
#               Effect: Allow
#               Action:
#                 - "dynamodb:PutItem"
#                 - "dynamodb:GetItem"
#                 - "dynamodb:UpdateItem"
#               Resource: !Sub arn:${IAMPartition}:dynamodb:${AWS::Region}:${AWS::AccountId}:table/${StepFunctionsStateDDB}
#         - PolicyName: Cloudwatch
#           PolicyDocument:
#             Version: '2012-10-17'
#             Statement:
#             - Sid: AllowPutLogs
#               Effect: Allow
#               Action:
#                 - 'logs:CreateLogStream'
#                 - 'logs:PutLogEvents'
#               Resource: '*'
#   BatchExecutionRole:
#     Type: AWS::IAM::Role
#     Properties:
#       AssumeRolePolicyDocument:
#         Version: '2012-10-17'
#         Statement:
#           Effect: Allow
#           Principal:
#             Service:
#               - batch.amazonaws.com
#           Action:
#             - sts:AssumeRole
#       Path: /
#       Policies:
#         - PolicyName: IAM_PASS_ROLE
#           PolicyDocument:
#             Version: '2012-10-17'
#             Statement:
#               Sid: VisualEditor0
#               Effect: Allow
#               Action: iam:PassRole
#               Resource: '*'
#               Condition:
#                 StringEquals:
#                   iam:PassedToService:
#                     - ec2.amazonaws.com
#                     - ec2.amazonaws.com.cn
#                     - ecs-tasks.amazonaws.com
#         - PolicyName: custom_access_policy
#           PolicyDocument:
#             Version: '2012-10-17'
#             Statement:
#               Sid: VisualEditor2
#               Effect: Allow
#               Action:
#                 - ec2:DescribeAccountAttributes
#                 - ec2:DescribeInstances
#                 - ec2:DescribeInstanceAttribute
#                 - ec2:DescribeSubnets
#                 - ec2:DescribeSecurityGroups
#                 - ec2:DescribeKeyPairs
#                 - ec2:DescribeImages
#                 - ec2:DescribeImageAttribute
#                 - ec2:DescribeSpotInstanceRequests
#                 - ec2:DescribeSpotFleetInstances
#                 - ec2:DescribeSpotFleetRequests
#                 - ec2:DescribeSpotPriceHistory
#                 - ec2:DescribeVpcClassicLink
#                 - ec2:DescribeLaunchTemplateVersions
#                 - ec2:CreateLaunchTemplate
#                 - ec2:DeleteLaunchTemplate
#                 - ec2:RequestSpotFleet
#                 - ec2:CancelSpotFleetRequests
#                 - ec2:ModifySpotFleetRequest
#                 - ec2:TerminateInstances
#                 - ec2:RunInstances
#                 - autoscaling:DescribeAccountLimits
#                 - autoscaling:DescribeAutoScalingGroups
#                 - autoscaling:DescribeLaunchConfigurations
#                 - autoscaling:DescribeAutoScalingInstances
#                 - autoscaling:CreateLaunchConfiguration
#                 - autoscaling:CreateAutoScalingGroup
#                 - autoscaling:UpdateAutoScalingGroup
#                 - autoscaling:SetDesiredCapacity
#                 - autoscaling:DeleteLaunchConfiguration
#                 - autoscaling:DeleteAutoScalingGroup
#                 - autoscaling:CreateOrUpdateTags
#                 - autoscaling:SuspendProcesses
#                 - autoscaling:PutNotificationConfiguration
#                 - autoscaling:TerminateInstanceInAutoScalingGroup
#                 - ecs:DescribeClusters
#                 - ecs:DescribeContainerInstances
#                 - ecs:DescribeTaskDefinition
#                 - ecs:DescribeTasks
#                 - ecs:ListClusters
#                 - ecs:ListContainerInstances
#                 - ecs:ListTaskDefinitionFamilies
#                 - ecs:ListTaskDefinitions
#                 - ecs:ListTasks
#                 - ecs:CreateCluster
#                 - ecs:DeleteCluster
#                 - ecs:RegisterTaskDefinition
#                 - ecs:DeregisterTaskDefinition
#                 - ecs:RunTask
#                 - ecs:StartTask
#                 - ecs:StopTask
#                 - ecs:UpdateContainerAgent
#                 - ecs:DeregisterContainerInstance
#                 - logs:CreateLogGroup
#                 - logs:CreateLogStream
#                 - logs:PutLogEvents
#                 - logs:DescribeLogGroups
#                 - iam:GetInstanceProfile
#                 - iam:GetRole
#               Resource: '*'
#         - PolicyName: iam_custom_policies
#           PolicyDocument:
#             Version: '2012-10-17'
#             Statement:
#               Sid: VisualEditor3
#               Effect: Allow
#               Action: iam:CreateServiceLinkedRole
#               Resource: '*'
#               Condition:
#                 StringEquals:
#                   iam:AWSServiceName:
#                   - autoscaling.amazonaws.com
#                   - ecs.amazonaws.com
#         - PolicyName: ec2_custom_policies
#           PolicyDocument:
#             Version: '2012-10-17'
#             Statement:
#               Sid: VisualEditor4
#               Effect: Allow
#               Action: ec2:CreateTags
#               Resource: '*'
#               Condition:
#                 StringEquals:
#                   ec2:CreateAction: RunInstances
#   ComputeEnvironment:
#     Type: AWS::Batch::ComputeEnvironment
#     Properties:
#       Type: MANAGED
#       ServiceRole: !GetAtt 'BatchExecutionRole.Arn'
#       ComputeResources:
#         MaxvCpus: !Ref MaxVCPUBatch
#         SecurityGroupIds:
#           - !GetAtt VPC.DefaultSecurityGroup
#         Type: !If [EnableFargateOnBatch, 'FARGATE', 'EC2']
#         Subnets:
#           - !Ref Subnet1
#           - !Ref Subnet2
#         MinvCpus: !If [EnableFargateOnBatch, !Ref AWS::NoValue, !Ref MinVCPUBatch]
#         InstanceRole: !If [EnableFargateOnBatch, !Ref AWS::NoValue, !GetAtt 'ECSInstanceProfile.Arn']
#         InstanceTypes: !If [EnableFargateOnBatch, !Ref AWS::NoValue, !Ref ComputeEnvInstanceTypes]
#         DesiredvCpus: !If [EnableFargateOnBatch, !Ref AWS::NoValue, !Ref DesiredVCPUBatch]
#       State: ENABLED
#   JobQueue:
#     DependsOn: ComputeEnvironment
#     Type: AWS::Batch::JobQueue
#     Properties:
#       ComputeEnvironmentOrder:
#         - Order: 1
#           ComputeEnvironment: !Ref ComputeEnvironment
#       State: ENABLED
#       Priority: 1
#       JobQueueName: !Join [ "-", [ 'job-queue', !Ref 'AWS::StackName' ] ]
#   Api:
#     DependsOn: VpcLink
#     Type: 'AWS::ApiGateway::RestApi'
#     Properties:
#       EndpointConfiguration:
#         Types:
#           - !If [ IsGov, 'REGIONAL', 'EDGE' ]
#       Name: !Join ['-', [!Ref 'AWS::StackName', 'api'] ]
#   ApiResource:
#     Type: 'AWS::ApiGateway::Resource'
#     Properties:
#       ParentId: !GetAtt Api.RootResourceId
#       RestApiId: !Ref Api
#       PathPart: '{proxy+}'
#   DBApiResource:
#     Type: 'AWS::ApiGateway::Resource'
#     Properties:
#       ParentId: !GetAtt Api.RootResourceId
#       RestApiId: !Ref Api
#       PathPart: 'db_schema_status'
#   VpcLink:
#       Type: AWS::ApiGateway::VpcLink
#       Properties:
#           Name: !Join ['-', [!Ref 'AWS::StackName', 'vpclink'] ]
#           TargetArns:
#               - !Ref NLB
#   ProxyMethod:
#     Type: 'AWS::ApiGateway::Method'
#     Properties:
#       HttpMethod: ANY
#       ApiKeyRequired: !If [ EnableAuth, 'true', !Ref "AWS::NoValue" ]
#       ResourceId: !Ref ApiResource
#       RestApiId: !Ref Api
#       AuthorizationType: NONE
#       RequestParameters:
#         method.request.path.proxy: true
#       Integration:
#         ConnectionType: VPC_LINK
#         ConnectionId: !Ref VpcLink
#         CacheKeyParameters:
#           - 'method.request.path.proxy'
#         RequestParameters:
#           integration.request.path.proxy: 'method.request.path.proxy'
#         IntegrationHttpMethod: ANY
#         Type: HTTP_PROXY
#         Uri: !Join ['', ['http://', !GetAtt 'NLB.DNSName', '/{proxy}'] ]
#         PassthroughBehavior: WHEN_NO_MATCH
#         IntegrationResponses:
#           - StatusCode: 200
#   DBMethod:
#     Type: 'AWS::ApiGateway::Method'
#     Properties:
#       HttpMethod: GET
#       ApiKeyRequired: !If [ EnableAuth, 'true', !Ref "AWS::NoValue" ]
#       ResourceId: !Ref DBApiResource
#       RestApiId: !Ref Api
#       AuthorizationType: NONE
#       Integration:
#         ConnectionType: VPC_LINK
#         ConnectionId: !Ref VpcLink
#         IntegrationHttpMethod: GET
#         Type: HTTP_PROXY
#         Uri: !Join ['', ['http://', !GetAtt 'NLB.DNSName', ':8082/db_schema_status'] ]
#         PassthroughBehavior: WHEN_NO_MATCH
#         IntegrationResponses:
#           - StatusCode: 200
#   ApiDeployment:
#     DependsOn:
#       - ProxyMethod
#     Type: 'AWS::ApiGateway::Deployment'
#     Properties:
#       RestApiId: !Ref Api
#       StageName: api
#   ApiKey:
#     Condition: 'EnableAuth'
#     Type: 'AWS::ApiGateway::ApiKey'
#     DependsOn:
#       - Api
#       - ApiDeployment
#     Properties:
#       Name: !Join ['-', [!Ref 'AWS::StackName', ApiKey] ]
#       Enabled: 'true'
#   ApiUsagePlan:
#     Condition: 'EnableAuth'
#     Type: "AWS::ApiGateway::UsagePlan"
#     DependsOn:
#       - Api
#       - ApiDeployment
#     Properties:
#       ApiStages:
#       - ApiId: !Ref Api
#         Stage: api
#       UsagePlanName: !Join ["", [{"Ref": "AWS::StackName"}, "-usage-plan"]]
#   ApiUsagePlanKey:
#     Condition: 'EnableAuth'
#     Type: "AWS::ApiGateway::UsagePlanKey"
#     DependsOn:
#       - Api
#       - ApiDeployment
#     Properties:
#       KeyId: !Ref ApiKey
#       KeyType: API_KEY
#       UsagePlanId: !Ref ApiUsagePlan
#   StepFunctionsStateDDB:
#     Type: AWS::DynamoDB::Table
#     Properties:
#       BillingMode: PAY_PER_REQUEST
#       AttributeDefinitions:
#         - AttributeName: "pathspec"
#           AttributeType: "S"
#       KeySchema:
#         - AttributeName: "pathspec"
#           KeyType: "HASH"
#       TimeToLiveSpecification:
#         AttributeName: ttl
#         Enabled: true

# # --- Metaflow UI resources begin ---

#   LoadBalancerUI:
#     Type: 'AWS::ElasticLoadBalancingV2::LoadBalancer'
#     Condition: EnableUI
#     Properties:
#       SecurityGroups:
#       - !Ref LoadBalancerSecurityGroupUI
#       Subnets:
#         - !Ref Subnet1
#         - !Ref Subnet2
#       Type: application
#   ListenerUI:
#     Type: 'AWS::ElasticLoadBalancingV2::Listener'
#     Condition: EnableUI
#     DependsOn:
#       - LoadBalancerUI
#     Properties:
#       Certificates:
#       - CertificateArn: !Ref CertificateArn
#       DefaultActions: # 1. Authenticate against Cognito User Pool
#       - Type: 'authenticate-cognito'
#         AuthenticateCognitoConfig:
#           OnUnauthenticatedRequest: 'authenticate' # Redirect unauthenticated clients to Cognito login page
#           Scope: 'openid'
#           UserPoolArn: !GetAtt 'UserPoolUI.Arn'
#           UserPoolClientId: !Ref UserPoolClientUI
#           UserPoolDomain: !Ref UserPoolDomainUI
#         Order: 1
#       - Type: forward # 2. Forward request to target group (e.g., EC2 instances)
#         TargetGroupArn: !Ref ALBTargetGroupUIStatic
#         Order: 100
#       LoadBalancerArn: !Ref LoadBalancerUI
#       Port: 443
#       Protocol: 'HTTPS'
#   ListenerRuleUIService:
#     Type: 'AWS::ElasticLoadBalancingV2::ListenerRule'
#     Condition: EnableUI
#     Properties:
#       ListenerArn: !Ref ListenerUI
#       Priority: 2
#       Actions:
#         - Type: 'authenticate-cognito'
#           AuthenticateCognitoConfig:
#             OnUnauthenticatedRequest: 'authenticate' # Redirect unauthenticated clients to Cognito login page
#             Scope: 'openid'
#             UserPoolArn: !GetAtt 'UserPoolUI.Arn'
#             UserPoolClientId: !Ref UserPoolClientUI
#             UserPoolDomain: !Ref UserPoolDomainUI
#           Order: 1
#         - Type: forward # 2. Forward request to target group (e.g., EC2 instances)
#           TargetGroupArn: !Ref ALBUITargetGroupUIService
#           Order: 2
#       Conditions:
#         - Field: path-pattern
#           PathPatternConfig:
#             Values:
#               - "/api/*"
#   ALBTargetGroupUIStatic:
#     Type: 'AWS::ElasticLoadBalancingV2::TargetGroup'
#     Condition: EnableUI
#     Properties:
#       Port:  !FindInMap ['ServiceInfoUIStatic', 'ContainerPort', 'value']
#       Protocol: HTTP
#       TargetType: ip
#       VpcId: !Ref 'VPC'
#   ALBUITargetGroupUIService:
#     Type: 'AWS::ElasticLoadBalancingV2::TargetGroup'
#     Condition: EnableUI
#     Properties:
#       Port:  !FindInMap ['ServiceInfoUIService', 'ContainerPort', 'value']
#       Protocol: HTTP
#       TargetType: ip
#       HealthCheckPath: "/api/ping"
#       HealthCheckIntervalSeconds: 10
#       VpcId: !Ref 'VPC'
#   TaskDefinitionUIService:
#     Type: AWS::ECS::TaskDefinition
#     Condition: EnableUI
#     Properties:
#       Family: !FindInMap ["ServiceInfoUIService", "ServiceName", "value"]
#       Cpu: !FindInMap ["ServiceInfoUIService", "ContainerCpu", "value"]
#       Memory: !FindInMap ["ServiceInfoUIService", "ContainerMemory", "value"]
#       NetworkMode: awsvpc
#       EphemeralStorage:
#         SizeInGiB: 100
#       RequiresCompatibilities:
#         - FARGATE
#       ExecutionRoleArn: !Ref 'ECSTaskExecutionRole'
#       TaskRoleArn: !GetAtt 'MetadataSvcECSTaskRole.Arn'
#       ContainerDefinitions:
#         - Name: !FindInMap ["ServiceInfoUIService", "ServiceName", "value"]
#           Environment:
#             - Name: "MF_METADATA_DB_HOST"
#               Value: !GetAtt 'RDSMasterInstance.Endpoint.Address'
#             - Name: "MF_METADATA_DB_PORT"
#               Value: "5432"
#             - Name: "MF_METADATA_DB_USER"
#               Value: !Join ['', ['{{resolve:secretsmanager:', !Ref MyRDSSecret, ':SecretString:username}}' ]]
#             - Name: "MF_METADATA_DB_PSWD"
#               Value: !Join ['', ['{{resolve:secretsmanager:', !Ref MyRDSSecret, ':SecretString:password}}' ]]
#             - Name: "MF_METADATA_DB_NAME"
#               Value: "metaflow"
#             - Name: "UI_ENABLED"
#               Value: "1"
#             - Name: PATH_PREFIX
#               Value: "/api/"
#             - Name: MF_DATASTORE_ROOT
#               Value: !Sub "s3://${MetaflowS3Bucket}/metaflow"
#             - Name: LOGLEVEL
#               Value: 'DEBUG'
#             - Name: METAFLOW_DATASTORE_SYSROOT_S3
#               Value: !Sub "s3://${MetaflowS3Bucket}/metaflow"
#             - Name: METAFLOW_SERVICE_URL
#               Value: !Join ['', [ "http://localhost:", !FindInMap ['ServiceInfoUIService', 'ContainerPort', 'value'], "/api/metadata" ]]
#             - Name: METAFLOW_DEFAULT_DATASTORE
#               Value: 's3'
#             - Name: METAFLOW_DEFAULT_METADATA
#               Value: 'service'
#           Cpu: !FindInMap ['ServiceInfoUIService', 'ContainerCpu', 'value']
#           Memory: !FindInMap ['ServiceInfoUIService', 'ContainerMemory', 'value']
#           Image: !FindInMap ['ServiceInfoUIService', 'ImageUrl', 'value']
#           Command:
#             [
#               "/opt/latest/bin/python3",
#               "-m",
#               "services.ui_backend_service.ui_server",
#             ]
#           PortMappings:
#             - ContainerPort:
#                 !FindInMap ["ServiceInfoUIService", "ContainerPort", "value"]
#           LogConfiguration:
#             LogDriver: awslogs
#             Options:
#               awslogs-group:
#                 !Join [
#                   "",
#                   [
#                     "/ecs/",
#                     !Ref "AWS::StackName",
#                     "-",
#                     !FindInMap ["ServiceInfoUIService", "ServiceName", "value"],
#                   ],
#                 ]
#               awslogs-region: !Ref "AWS::Region"
#               awslogs-stream-prefix: "ecs"
#   ServiceLogGroupUIService:
#     Type: AWS::Logs::LogGroup
#     Condition: EnableUI
#     Properties:
#       LogGroupName:
#         !Join [
#           "",
#           [
#             "/ecs/",
#             !Ref "AWS::StackName",
#             "-",
#             !FindInMap ["ServiceInfoUIService", "ServiceName", "value"],
#           ],
#         ]
#   ECSFargateServiceUIService:
#     Type: AWS::ECS::Service
#     Condition: EnableUI
#     DependsOn:
#       - ListenerRuleUIService
#     Properties:
#       ServiceName: !FindInMap ['ServiceInfoUIService', 'ServiceName', 'value']
#       Cluster: !Ref 'ECSCluster'
#       LaunchType: FARGATE
#       DeploymentConfiguration:
#         MaximumPercent: 200
#         MinimumHealthyPercent: 75
#       DesiredCount: !FindInMap ['ServiceInfoUIService', 'DesiredCount', 'value']
#       NetworkConfiguration:
#         AwsvpcConfiguration:
#           AssignPublicIp: ENABLED
#           SecurityGroups:
#             - !Ref 'FargateSecurityGroup'
#           Subnets:
#             - !Ref 'Subnet1'
#             - !Ref 'Subnet2'
#       TaskDefinition: !Ref 'TaskDefinitionUIService'
#       LoadBalancers:
#         - ContainerName: !FindInMap ['ServiceInfoUIService', 'ServiceName', 'value']
#           ContainerPort: !FindInMap ['ServiceInfoUIService', 'ContainerPort', 'value']
#           TargetGroupArn: !Ref 'ALBUITargetGroupUIService'
#   TaskDefinitionUIStatic:
#     Type: AWS::ECS::TaskDefinition
#     Properties:
#       Family: !FindInMap ['ServiceInfoUIStatic', 'ServiceName', 'value']
#       Cpu: !FindInMap ['ServiceInfoUIStatic', 'ContainerCpu', 'value']
#       Memory: !FindInMap ['ServiceInfoUIStatic', 'ContainerMemory', 'value']
#       NetworkMode: awsvpc
#       RequiresCompatibilities:
#         - FARGATE
#       ExecutionRoleArn: !Ref 'ECSTaskExecutionRole'
#       TaskRoleArn: !GetAtt 'MetadataSvcECSTaskRole.Arn'
#       ContainerDefinitions:
#         - Name: !FindInMap ['ServiceInfoUIStatic', 'ServiceName', 'value']
#           Cpu: !FindInMap ['ServiceInfoUIStatic', 'ContainerCpu', 'value']
#           Memory: !FindInMap ['ServiceInfoUIStatic', 'ContainerMemory', 'value']
#           Image: !FindInMap ['ServiceInfoUIStatic', 'ImageUrl', 'value']
#           PortMappings:
#             - ContainerPort: !FindInMap ['ServiceInfoUIStatic', 'ContainerPort', 'value']
#           LogConfiguration:
#             LogDriver: awslogs
#             Options:
#               awslogs-group: !Join ['', ['/ecs/', !Ref 'AWS::StackName', '-', !FindInMap ['ServiceInfoUIStatic', 'ServiceName', 'value']]]
#               awslogs-region: !Ref 'AWS::Region'
#               awslogs-stream-prefix: 'ecs'
#   ServiceLogGroupUIStatic:
#     Type: AWS::Logs::LogGroup
#     Condition: EnableUI
#     Properties:
#       LogGroupName: !Join ['', ['/ecs/', !Ref 'AWS::StackName', '-', !FindInMap ['ServiceInfoUIStatic', 'ServiceName', 'value']]]
#   ECSFargateServiceUIStatic:
#     Type: AWS::ECS::Service
#     Condition: EnableUI
#     DependsOn:
#       - ListenerUI
#     Properties:
#       ServiceName: !FindInMap ['ServiceInfoUIStatic', 'ServiceName', 'value']
#       Cluster: !Ref 'ECSCluster'
#       LaunchType: FARGATE
#       DeploymentConfiguration:
#         MaximumPercent: 200
#         MinimumHealthyPercent: 75
#       DesiredCount: !FindInMap ['ServiceInfoUIStatic', 'DesiredCount', 'value']
#       NetworkConfiguration:
#         AwsvpcConfiguration:
#           AssignPublicIp: ENABLED
#           SecurityGroups:
#             - !Ref 'FargateSecurityGroup'
#           Subnets:
#             - !Ref 'Subnet1'
#             - !Ref 'Subnet2'
#       TaskDefinition: !Ref 'TaskDefinitionUIStatic'
#       LoadBalancers:
#         - ContainerName: !FindInMap ['ServiceInfoUIStatic', 'ServiceName', 'value']
#           ContainerPort: !FindInMap ['ServiceInfoUIStatic', 'ContainerPort', 'value']
#           TargetGroupArn: !Ref 'ALBTargetGroupUIStatic'
#   LoadBalancerSecurityGroupUI: # Security Group for Load Balancer allows incoming HTTPS requests
#     Type: 'AWS::EC2::SecurityGroup'
#     Condition: EnableUI
#     Properties:
#       GroupDescription: 'Load Balancer'
#       VpcId: !Ref 'VPC'
#       SecurityGroupIngress:
#       - IpProtocol: tcp
#         FromPort: 443
#         ToPort: 443
#         CidrIp: '0.0.0.0/0'
#   UserPoolUI:
#     Type: 'AWS::Cognito::UserPool'
#     Condition: EnableUI
#     Properties:
#       AdminCreateUserConfig:
#         AllowAdminCreateUserOnly: true # Disable self-registration
#         InviteMessageTemplate:
#           EmailSubject: !Sub '${AWS::StackName}: temporary password'
#           EmailMessage: 'Use the username {username} and the temporary password {####} to log in for the first time.'
#           SMSMessage: 'Use the username {username} and the temporary password {####} to log in for the first time.'
#       AutoVerifiedAttributes:
#       - email
#       UsernameAttributes:
#       - email
#       Policies:
#         PasswordPolicy:
#           MinimumLength: 16
#           RequireLowercase: false
#           RequireNumbers: false
#           RequireSymbols: false
#           RequireUppercase: false
#           TemporaryPasswordValidityDays: 21
#   UserPoolDomainUI: # Provides Cognito Login Page
#     Type: 'AWS::Cognito::UserPoolDomain'
#     Condition: EnableUI
#     Properties:
#       UserPoolId: !Ref UserPoolUI
#       Domain: !Select [2, !Split ['/', !Ref 'AWS::StackId']] # Generates a unique domain name
#   UserPoolClientUI:
#     Type: 'AWS::Cognito::UserPoolClient'
#     Condition: EnableUI
#     Properties:
#       AllowedOAuthFlows:
#       - code # Required for ALB authentication
#       AllowedOAuthFlowsUserPoolClient: true # Required for ALB authentication
#       AllowedOAuthScopes:
#       - email
#       - openid
#       - profile
#       - aws.cognito.signin.user.admin
#       CallbackURLs:
#       - !Sub https://${LoadBalancerUI.DNSName}/oauth2/idpresponse # Redirects to the ALB
#       - !Sub https://${PublicDomainName}/oauth2/idpresponse # Redirects to the ALB
#       GenerateSecret: true
#       SupportedIdentityProviders: # Optional: add providers for identity federation
#       - COGNITO
#       UserPoolId: !Ref UserPoolUI
# Outputs:
#   MetaflowDataStoreS3Url:
#     Description: Amazon S3 URL for Metaflow DataStore [METAFLOW_DATASTORE_SYSROOT_S3]
#     Value: !Sub "s3://${MetaflowS3Bucket}/metaflow"
#   MetaflowDataToolsS3Url:
#     Description: Amazon S3 URL for Metaflow DataTools [METAFLOW_DATATOOLS_S3ROOT]
#     Value: !Sub "s3://${MetaflowS3Bucket}/data"
#   BatchJobQueueArn:
#     Description: AWS Batch Job Queue ARN for Metaflow [METAFLOW_BATCH_JOB_QUEUE]
#     Value: !Ref JobQueue
#   ECSJobRoleForBatchJobs:
#     Description: Role for AWS Batch to Access Amazon S3 [METAFLOW_ECS_S3_ACCESS_IAM_ROLE]
#     Value: !GetAtt 'BatchS3TaskRole.Arn'
#   ServiceUrl:
#     Description: "URL for Metadata Service (Open to Public Access) [METAFLOW_SERVICE_URL]"
#     Value: !Sub "https://${Api}.execute-api.${AWS::Region}.amazonaws.com/api/"
#   InternalServiceUrl:
#     Description: "URL for Metadata Service (Accessible in VPC) [METAFLOW_SERVICE_INTERNAL_URL]"
#     Value: !Sub "http://${NLB.DNSName}/"
#   ApiKeyId:
#     Condition: 'EnableAuth'
#     Description: "API Gateway Key ID for Metadata Service. Fetch Key from AWS Console [METAFLOW_SERVICE_AUTH_KEY]"
#     Value: !Ref 'ApiKey'
#   MetaflowUserRoleArn:
#     Condition: 'EnableRole'
#     Description: "IAM Role for Metaflow Stack"
#     Value: !GetAtt "MetaflowUserRole.Arn"
#   SageMakerNoteBookURL:
#     Condition: 'EnableSagemaker'
#     Description: URL for SageMaker Notebook Instance
#     Value: !Sub 'https://${SageMakerNotebookInstance.NotebookInstanceName}.notebook.${AWS::Region}.sagemaker.aws/tree'
#   EventBridgeRoleArn:
#     Description: "IAM Role for Event Bridge [METAFLOW_EVENTS_SFN_ACCESS_IAM_ROLE]"
#     Value: !GetAtt "EventBridgeRole.Arn"
#   StepFunctionsRoleArn:
#     Description: "IAM Role for Step Functions [METAFLOW_SFN_IAM_ROLE]"
#     Value: !GetAtt "StepFunctionsRole.Arn"
#   DDBTableName:
#     Description: "DynamoDB Table Name [METAFLOW_SFN_DYNAMO_DB_TABLE]"
#     Value: !Ref StepFunctionsStateDDB
#   MigrationFunctionName:
#     Description: "Name of DB Migration Function"
#     Value: !Ref ExecuteDBMigration
#   VPCId:
#     Description: "VPC Id"
#     Value: !Ref VPC
#   Subnet1Id:
#     Description: "Subnet 1 Id"
#     Value: !Ref Subnet1
#   Subnet2Id:
#     Description: "Subnet 2 Id"
#     Value: !Ref Subnet2
#   RDSSecret:
#     Description: "RDS Secret"
#     Value: !Ref MyRDSSecret
#   LoadBalancerUIZoneID:
#     Condition: EnableUI
#     Description: "UI Load Balancer Canonical Hosted Zone ID"
#     Value: !GetAtt "LoadBalancerUI.CanonicalHostedZoneID"
#   LoadBalancerUIDNSName:
#     Condition: EnableUI
#     Description: "UI Load Balancer DNS Name"
#     Value: !GetAtt "LoadBalancerUI.DNSName"
