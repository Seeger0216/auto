# -*- coding :  utf-8 -*-
# @Time      :  2021-01-03
# @Author    :  Github@sslspace
# @Blog      ： https://blog.shelike.me/
# @Software  :  Pycharm
 
import io
import json
import time
from contextlib import redirect_stdout
from azure.cli.core import get_default_cli
 
# 1.检查配额以确定订阅类型，并确定要开的虚拟机数量
# 初始化区域列表，共31个区域
# Azure for Students和即用即付订阅均不支持 South India 和 West India 区域
locations = ['eastus', 'eastus2', 'westus', 'centralus', 'northcentralus', 'southcentralus',
             'northeurope', 'westeurope', 'eastasia', 'southeastasia', 'japaneast',
             'japanwest', 'australiaeast', 'australiasoutheast', 'australiacentral',
             'brazilsouth', 'centralindia', 'canadacentral', 'canadaeast', 'westus2',
             'uksouth', 'ukwest', 'koreacentral', 'koreasouth', 'francecentral',
             'southafricanorth', 'uaenorth', 'switzerlandnorth', 'germanywestcentral',
             'norwayeast', 'westcentralus']
 
# 捕获 get_default_cli().invoke 的标准输出
f = io.StringIO()
with redirect_stdout(f):
    get_default_cli().invoke(['vm', 'list-usage', '--location', 'East US', '--query',
                              '[?localName == \'Total Regional vCPUs\'].limit'])
    limit = f.getvalue()
 
# 默认每个区域的配额都相同，因此只需查询美国东部地区的配额
# Azure for Students订阅每个区域的vCPU总数为6，
# 标准FSv2系列vCPUs为4，标准FS系列vCPUs为4
# 所以创建一个Standard_F4s_v2实例（占用4个vCPUs），
# 一个Standard_F2s实例（占用2个vCPUs）
if 6 in limit:
    print("当前订阅为Azure for Students")
    size1_name = "Standard_F4s_v2"
    size1_abbreviation = "F4s_v2"
    size1_count = 1
    size2_name = "Standard_F2s"
    size2_abbreviation = "F2s"
    size2_count = 1
    type = 0
 
# 即用即付订阅每个区域的vCPU总数为10，与标准FSv2系列的vCPUs相同
# 因此创建一个Standard_F8s_v2实例（占用8个vCPUs），
# 一个Standard_F2s_v2实例（占用2个vCPUs）
elif 10 in limit:
    print("当前订阅为即用即付")
    size1_name = "Standard_F8s_v2"
    size1_abbreviation = "F8s_v2"
    size1_count = 1
    size2_name = "Standard_F2s_v2"
    size2_abbreviation = "F2s_v2"
    size2_count = 1
    type = 1
 
# 免费试用订阅每个区域的vCPU总数为4，与标准FSv2系列的vCPUs相同
# 因此创建1个Standard_F4s_v2实例（共占用4个vCPUs）
elif 4 in limit:
    print("当前订阅为免费试用，每个区域的配额仅为4 vCPUs，建议升级后再用。"
          "若升级后仍看到本消息，请等待十分钟再运行脚本。")
    selection = input("输入Y继续运行，任意键退出")
    if selection != "Y" or "y":
        exit(0)
    size1_name = "Standard_F4s_v2"
    size1_abbreviation = "F4s_v2"
    size1_count = 1
    type = 2
 
else:
    print("未知订阅，请手动修改创建虚拟机的数量")
    print("若当前订阅为Azure for Students、免费试用或即用即付，"
          "请进入“创建虚拟机”界面，任意填写信息，"
          "一直到“查看+创建”项（创建虚拟机的最后一步）"
          "显示“验证通过”即可自动刷新配额")
    exit(0)
 
# 2.创建资源组
# 资源组只是资源的逻辑容器,资源组内的资源不必与资源组位于同一区域
get_default_cli().invoke(['group', 'create', '--name', 'myResourceGroup',
                          '--location', 'eastus'])
# 除非订阅被禁用，其他任何情况下创建资源组都会成功（重名也返回成功）
print("创建资源组成功")
 
# 3.创建开机后要运行的脚本
init = input("请输入机器开机后要执行的命令（仅一行）:  ")
with open("./cloud-init.txt", "w") as f:
    f.write("#cloud-config" + "\n")
    f.write("runcmd:" + "\n")
    f.write("  - sudo -s" + "\n")
    f.write(f"  - {init}")
 
# 4.批量创建虚拟机并运行挖矿脚本
for location in locations:
    # Azure for Students订阅不支持 norwayeast 区域
    if location == "norwayeast" and type == 0:
        continue
 
    # westcentralus 区域不支持 FSv2 系列，
    # Azure for Students订阅不支持 F/FS 系列
    if location == "westcentralus" and type == 0:
        size1_name = "Standard_D4ds_v4"
        size1_abbreviation = "D4ds_v4"
        size2_name = "Standard_D2s_v4"
        size2_abbreviation = "D2s_v4"
    if location == "westcentralus" and type == 1:
        size1_name = "Standard_F8s"
        size1_abbreviation = "F8s"
        size2_name = "Standard_F2s"
        size2_abbreviation = "F2s"
    if location == "westcentralus" and type == 2:
        size1_name = "Standard_F4s"
        size1_abbreviation = "F4s"
 
    count = 0
    for a in range(0, size1_count):
        count += 1
        print("正在 " + str(location) + " 区域创建第 " + str(count)
              + f" 个 {size1_name} 实例，共 " + str(size1_count) + " 个")
        get_default_cli().invoke(
            ['vm', 'create', '--resource-group', 'myResourceGroup', '--name',
             f'{location}-{size1_abbreviation}-{count}', '--image', 'UbuntuLTS',
             '--size', f'{size1_name}', '--location', f'{location}', '--admin-username',
             'azureuser', '--admin-password', '6uPF5Cofvyjcew9', '--custom-data',
             'cloud-init.txt', "--no-wait"])
    if type != 2:
        count = 0
        for a in range(0, size2_count):
            count += 1
            print("正在 " + str(location) + " 区域创建第 " + str(count)
                  + f" 个 {size2_name} 实例，共 " + str(size2_count) + " 个")
            get_default_cli().invoke(
                ['vm', 'create', '--resource-group', 'myResourceGroup', '--name',
                 f'{location}-{size2_abbreviation}-{count}', '--image', 'UbuntuLTS',
                 '--size', f'{size2_name}', '--location', f'{location}', '--admin-username',
                 'azureuser', '--admin-password', '6uPF5Cofvyjcew9', '--custom-data',
                 'cloud-init.txt', "--no-wait"])
 
# 5.信息汇总
# 获取所有vm的名字
print("\n------------------------------------------------------------------------------\n")
print("大功告成！在31个区域创建虚拟机的命令已成功执行")
for i in range(120, -1, -1):
    print("\r正在等待Azure生成统计信息，还需等待{}秒".format(i), end="", flush=True)
    time.sleep(1)
f = io.StringIO()
with redirect_stdout(f):
    get_default_cli().invoke(['vm', 'list', '--query', '[*].name'])
    result = f.getvalue()
vmname = json.loads(result)
print("\n\n-----------------------------------------------------------------------------\n")
print(str(vmname))
print("\n------------------------------------------------------------------------------\n")
print("已创建了" + str(len(vmname)) + "台虚拟机")
 
# 如果想删除脚本创建的所有资源，取消注释以下语句
# get_default_cli().invoke(['group', 'delete', '--name', 'myResourceGroup',
# '--no-wait', '--yes'])
# print("删除资源组成功")
