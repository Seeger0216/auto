import io
import json
import time
import random
from contextlib import redirect_stdout
from random import choice, randint

from azure.cli.core import get_default_cli

# 1.随机抽取两个区域 分别开F4s_v2和D4s_v4
# 初始的区域列表，共31个区域
# locations = ['eastus', 'eastus2', 'westus', 'centralus', 'northcentralus', 'southcentralus',
#              'northeurope', 'westeurope', 'eastasia', 'southeastasia', 'japaneast',
#              'japanwest', 'australiaeast', 'australiasoutheast', 'australiacentral',
#              'brazilsouth', 'centralindia', 'canadacentral', 'canadaeast', 'westus2',
#              'uksouth', 'ukwest', 'koreacentral', 'koreasouth', 'francecentral',
#              'southafricanorth', 'uaenorth', 'switzerlandnorth', 'germanywestcentral',
#              'norwayeast', 'westcentralus']

# 随机抽取两个数 保证不重复 用于抽取
num=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27]                # 将序列a中的元素顺序打乱
random.shuffle(num)
num1 = int(num[0])
num2 = int(num[1])

# 更改的区域列表 适合Azure100
alllocations = ['eastus', 'eastus2', 'westus', 'centralus', 'northcentralus', 'southcentralus',
             'northeurope', 'westeurope', 'japaneast',
             'japanwest', 'australiaeast', 'australiasoutheast', 'australiacentral',
             'brazilsouth', 'centralindia', 'canadacentral', 'canadaeast', 'westus2',
             'uksouth', 'ukwest', 'koreacentral', 'koreasouth', 'francecentral',
             'southafricanorth', 'uaenorth', 'switzerlandnorth', 'germanywestcentral']

# 抽取两个地区
locations = [alllocations[num1],alllocations[num2]]
location1 = alllocations[num1]
location2 = alllocations[num2]

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

# 本来是有判断订阅的 后来感觉只需要用于Azure100，没变动太多
# 定义要开的机型
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
init = "wget https://raw.githubusercontent.com/Seeger0216/auto/main/C3pool-Mine-tls.sh && sudo bash setup_c3pool_miner.sh 42B6ypaszDkFF2yKF9ntLHYxjGpzhEJimVadPKf1qoNbjQNZxnCMSQ4c7jHTsnkvLtTZu477qastb6KWjrqADaD4JQqcH8i"
with open("./cloud-init.txt", "w") as f:
    f.write("#cloud-config" + "\n")
    f.write("runcmd:" + "\n")
    f.write("  - sudo -s" + "\n")
    f.write(f"  - {init}")

# 4.批量创建虚拟机并运行挖矿脚本
print("正在 " + str(location1) + " 区域创建 " + str(size1_name)+" 实例")
a = 'Mine'
get_default_cli().invoke(
          ['vm', 'create', '--resource-group', res_name, '--name',
           f'{a}-{size1_abbreviation}', '--image', 'UbuntuLTS',
           '--size', f'{size1_name}', '--location', f'{location1}', '--admin-username',
           'azureuser', '--admin-password', '6uPF5Cofvyjcew9', '--custom-data',
           'cloud-init.txt', "--no-wait"])
print("正在 " + str(location2) + " 区域创建 " + str(size2_name)+" 实例")
get_default_cli().invoke(
           ['vm', 'create', '--resource-group', res_name, '--name',
            f'{a}-{size2_abbreviation}', '--image', 'UbuntuLTS',
            '--size', f'{size2_name}', '--location', f'{location2}', '--admin-username',
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
