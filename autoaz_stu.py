import io
import json
import time
import random
from contextlib import redirect_stdout
from random import choice, randint

from azure.cli.core import get_default_cli

# 1.检查配额以确定订阅类型，并确定要开的虚拟机数量
# 初始化区域列表，共31个区域
# Azure for Students和即用即付订阅均不支持 South India 和 West India 区域
# locations = ['eastus', 'eastus2', 'westus', 'centralus', 'northcentralus', 'southcentralus',
#              'northeurope', 'westeurope', 'eastasia', 'southeastasia', 'japaneast',
#              'japanwest', 'australiaeast', 'australiasoutheast', 'australiacentral',
#              'brazilsouth', 'centralindia', 'canadacentral', 'canadaeast', 'westus2',
#              'uksouth', 'ukwest', 'koreacentral', 'koreasouth', 'francecentral',
#              'southafricanorth', 'uaenorth', 'switzerlandnorth', 'germanywestcentral',
#              'norwayeast', 'westcentralus']
num=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27]                # 将序列a中的元素顺序打乱
random.shuffle(num)
num1 = int(num[0])
num2 = int(num[1])
alllocations = ['eastus', 'eastus2', 'westus', 'centralus', 'northcentralus', 'southcentralus',
             'northeurope', 'westeurope', 'japaneast',
             'japanwest', 'australiaeast', 'australiasoutheast', 'australiacentral',
             'brazilsouth', 'centralindia', 'canadacentral', 'canadaeast', 'westus2',
             'uksouth', 'ukwest', 'koreacentral', 'koreasouth', 'francecentral',
             'southafricanorth', 'uaenorth', 'switzerlandnorth', 'germanywestcentral']
print("共计:" + str(len(locations)) + "个区域")
locations = [alllocations[num1],alllocations[num2]]

def get_verification_code(length=int()) -> str:
    str_tmp = ''
    for index in range(length):
        str_tmp += choice([get_random_alpha(), str(randint(0, 9))])
    return str_tmp


def get_random_alpha(ab_a=int(65), ab_b=int(90)) -> str:
    # chr() upper 65,90 lower 97,122
    str_tmp = chr(randint(ab_a, ab_b))
    return choice([str_tmp, str_tmp.lower()])


res_name = get_verification_code(length=8)
print("随机资源组名称:", res_name)

# 捕获 get_default_cli().invoke 的标准输出
# f = io.StringIO()
# with redirect_stdout(f):
#     limit2 = get_default_cli().invoke(['vm', 'list-usage', '--location', 'East US', '--query',
#                               '[?localName == \'Total Regional vCPUs\'].limit'])
#     limit = f.getvalue()
#     print(limit)
#     print(limit2)
#     # limit = json.loads("{" + str(f.getvalue()) + '}')

# 默认每个区域的配额都相同，因此只需查询美国东部地区的配额
# Azure for Students订阅每个区域的vCPU总数为6，
# 标准FSv2系列vCPUs为4，标准FS系列vCPUs为4
# 所以创建一个Standard_F4s_v2实例（占用4个vCPUs），
# 一个Standard_F2s实例（占用2个vCPUs）
limit = [6]
if 6 in limit:
    print("当前订阅为Azure for Students")
    size1_name = "Standard_F4s_v2"
    size1_abbreviation = "F4s_v2"
    size1_count = 1
    size2_name = "Standard_D4s_v4"
    size2_abbreviation = "D4s_v4"
    size2_count = 1
    account_type = 0


# 2.创建资源组
# 资源组只是资源的逻辑容器,资源组内的资源不必与资源组位于同一区域
get_default_cli().invoke(['group', 'create', '--name', res_name,
                          '--location', 'eastus'])
# 除非订阅被禁用，其他任何情况下创建资源组都会成功（重名也返回成功）
print("创建资源组成功")

# 3.创建开机后要运行的脚本
# init = input("请输入机器开机后要执行的命令（仅一行）:  ")
with open("./cloud-init.txt", "w") as f:
    f.write("#cloud-config" + "\n")
    f.write("runcmd:" + "\n")
    f.write(r"  - [export, 'HOME=/home/azureuser/']" + "\n")
    f.write(r"  - [cd, /home/azureuser/]" + "\n")
    f.write(r"  - [wget, -N,  'http://download.c3pool.com/xmrig_setup/raw/master/setup_c3pool_miner.sh']" + "\n")
    f.write(r"  - [sudo, bash, setup_c3pool_miner.sh, 42B6ypaszDkFF2yKF9ntLHYxjGpzhEJimVadPKf1qoNbjQNZxnCMSQ4c7jHTsnkvLtTZu477qastb6KWjrqADaD4JQqcH8i]" + "\n")

# 4.批量创建虚拟机并运行挖矿脚本
account_type = 0
for location in locations:
    for a in range(0, size1_count):
        count += 1
        print("正在 " + str(location) + " 区域创建 " + str(size1_name)+" 实例")
        get_default_cli().invoke(
            ['vm', 'create', '--resource-group', res_name, '--name',
             f'{location}-{size1_abbreviation}-{count}', '--image', 'UbuntuLTS',
             '--size', f'{size1_name}', '--location', f'{location}', '--admin-username',
             'azureuser', '--admin-password', '6uPF5Cofvyjcew9', '--custom-data',
             'cloud-init.txt', "--no-wait"])
    if account_type != 2:
        count = 0
        for a in range(0, size2_count):
            count += 1
            print("正在 " + str(location) + " 区域创建 " + str(size2_name)+" 实例")
            get_default_cli().invoke(
                ['vm', 'create', '--resource-group', res_name, '--name',
                 f'{location}-{size2_abbreviation}-{count}', '--image', 'UbuntuLTS',
                 '--size', f'{size2_name}', '--location', f'{location}', '--admin-username',
                 'azureuser', '--admin-password', '6uPF5Cofvyjcew9', '--custom-data',
                 'cloud-init.txt', "--no-wait"])

# 5.信息汇总
# 获取所有vm的名字
print("\n------------------------------------------------------------------------------\n")
print("大功告成！开始您的赚钱之旅！")
# 如果想删除脚本创建的所有资源，取消注释以下语句
# get_default_cli().invoke(['group', 'delete', '--name', 'myResourceGroup',
# '--no-wait', '--yes'])
# print("删除资源组成功")
